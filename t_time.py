import json
import logging
import os.path
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

import requests
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, NamedStyle

class MissingChargeTypeException(Exception):
    """Exception raised for missing charge type tag."""
    pass

class MissingProjectException(Exception):
    """Exception raised for missing project."""
    pass

class WrongProjectNameFormatException(Exception):
    """Exception raised for wrong project name format."""
    pass

class NoDayDataException(Exception):
    """Exception raised for no data on day selected."""
    pass

class TimeSheetLoader():
    """ The class to handle completing timesheets daily. """

    def __init__(self):
        # Declare initial user vairables
        self.user_agent, self.api_key, self.workspace_id, self.website = ('', '', '', '')
        # Load user details from settings file
        try:
            with open('settings.txt') as f:
                for line in f:
                    fields = line.strip().split()
                    # for security only input these pre-defined variables
                    if fields[0] == 'user_agent' or 'api_key' or 'workspace_id' or 'website':
                        # Handling the path on the computer needs special help
                        exec('self.%s = "%s"' % (fields[0], fields[2]))
        # If it doesn't exist, prompt the user for the settings
        except FileNotFoundError:
            print('Let\'s get you setup!')
            self.user_agent = input('Your email address: ')
            self.api_key = input('Your API key (get it in Toggl Profile Settings https://toggl.com/app/profile ): ')
            print('    Your workspace IDs are:' , ', '.join(self.get_workspace_id()))
            self.workspace_id = input('Enter the 7 digit workspace ID to use: ')
        # Save the user settings to settings.txt
            with open('settings.txt', 'w') as f:
                f.write('user_agent = ' + str(self.user_agent) + '\n')
                f.write('api_key = ' + str(self.api_key) +  '\n')
                f.write('workspace_id = ' + str(self.workspace_id) +  '\n')


    def get_workspace_id(self):
        # Gets list of workspaces user has from api
        r = requests.get('https://api.track.toggl.com/api/v8/workspaces', auth=(self.api_key, 'api_token'))
        r = r.json()
        ids = []
        for entry in r:
            ids.append(str(entry['id']) + ' (' + entry['name'] + ')')
        return ids 


    def get_detailed_data(self, date):
        """Get detailed data for a specific date from toggl api"""
        # Format date required by Toggl api
        date = datetime.strptime(date, '%d/%m/%y').strftime('%Y-%m-%d')
        # Set paramaters for api call
        parameters = {
        'user_agent': self.user_agent,
        'workspace_id':self.workspace_id,
        'since': date,
        'until': date,
        'tag_ids': '',
        }
        # Get data from api
        print('Loading...', end = '')
        r = requests.get('https://api.track.toggl.com/reports/api/v2/details', auth=(self.api_key, 'api_token'), params=parameters)
        
        return r.json()  


    # Define functions for interpreting the data
    def round_half_hr(self, time_ms):
        """Toggl api returns milliseconds, round to half hours"""
        time = time_ms/(1000*60*60)
        return round(time * 2) / 2


    def format_date_text(self, date):
        return datetime.strptime(date, '%d/%m/%y').strftime('%d/%m/%y')


    def format_date_date(self, date):
        return datetime.strptime(date, '%d/%m/%y').date()


    def get_timesheet(self, date):
        """This is the master function to run to get a day's timesheet entry."""
        timesheet_data = self.summary_data(date)
        self.display_data()
        if len(timesheet_data['data']) != 0:    # only proceed if there is data to continue with
            self.excelLoad()
        return timesheet_data
        

    def summary_data(self, date):
        """Get's detailed data and summarises to required format for timesheet."""
        # Get detailed timesheet
        r_dat = self.get_detailed_data(date)
        # If r_dat is empty (i.e. no entries) let user know and stop process
        if r_dat['data'] == []:
            raise NoDayDataException(f"There is no timesheet data entererd for this day.")
        # Create a new variable for summarised data
        r_dat2 = {'data': [ ] }
        # Save the date in the new vaiable
        r_dat2['date'] = date

        # Get a list of the unique project/tag combinations as list of dictionaries
        projects_list = []
        try:
            for i in r_dat['data']:
                # Consider both project and tag for uniqueness
                try:
                    project_tag_combination = [{'project': i['project'], 'tag': i['tags'][0]}]
                    if project_tag_combination not in projects_list:
                        # assign a new entry to the dictionary of project
                        projects_list.append(project_tag_combination)
                except IndexError:
                    raise MissingChargeTypeException(f"Missing charge type tag for {i['description']}. Please fix and try again.")
        except KeyError:
            # Include error checking if API key is wrong
            try:
                print(r_dat['error']['message'])
            except KeyError:
                raise
        # Create base dataframe with above for timesheet
        for entry in projects_list:
            entry = entry[0]
            if entry['project'] == None:
                raise MissingProjectException(f"One of your entries is missing a project. Please fix and try again.")
            elif entry['project'] == 'NR':
                r_dat2['data'].append({'project': entry['project'], 'project_short': '', 'W': '', 'charge_type': entry['tag']}) 
            else:
                try:
                    short_string = entry['project'].split()[0]     # project_short splits string  
                    short_project = short_string.split('/')[0].strip()
                    short_job = short_string.split('/')[1].strip()
                    r_dat2['data'].append({'project': entry['project'], 'project_short': short_project, 'W': short_job, 'charge_type': entry['tag']})
                except IndexError:
                    raise WrongProjectNameFormatException(f"The project name \"{i['project']}\" has not followed the correct formatting. Please fix and try again.")               

        # Add formatted data
        b_times = []
        for x in r_dat2['data']:
            x['client'] = ''
            for i in r_dat['data']:
                if x['project'] == i['project']:
                    # Add client
                    if i['client'] != x['client']:
                        x['client'] = i['client']

            # Aggregate time (ms) by project_tag_combination
            project_tag_times = {}
            for entry in r_dat['data']:
                tag = entry['tags'][0] if entry.get('tags') else 'NoTag'
                key = (entry['project'], tag)
                project_tag_times[key] = project_tag_times.get(key, 0) + entry['dur']            

            # Add comments with time if more than one comment. Store descriptions to 'temp_desc' and time to 'temp_desc_time'.
            x['temp_desc'] = []
            x['temp_desc_time'] = []
            for i in r_dat['data']:
                if x['project'] == i['project'] and x['charge_type'] == i['tags'][0]:
                    if i['description'] not in x['temp_desc']:
                        x['temp_desc'].append(i['description'])
                        x['temp_desc_time'].append(i['dur'])
            # If there are repeats of descriptions, sum the time.
                    else:
                        idx = x['temp_desc'].index(i['description'])
                        x['temp_desc_time'][idx] += i['dur']
                                
            # Write complete description string with time to x['description'].
            x['description'] = []
            for idx in range(len(x['temp_desc'])):
                # Only show sub-time if does not round to 0.0hrs
                if self.round_half_hr(x['temp_desc_time'][idx]) > 0:
                    # Don't include the time in the first description
                    if idx == 0:
                        x['description'].append(x['temp_desc'][idx])
                    # Otherwise add the time of future descriptions
                    else:
                        x['description'].append(x['temp_desc'][idx] + ' (' + str(self.round_half_hr(x['temp_desc_time'][idx])) + 'hr)')

            # Get output description string
            if x['project'] == 'NR' and x['charge_type'] == i['tags'][0]:
                description = ', '.join(x['description'])
            else:
                description = '(' + x['client'] + ') ' + ', '.join(x['description'])
            x['output_desc'] = description

            # Get branch number
            if x['project'] == 'NR':
                branch = '575'
            else:
                branch = x['project_short'].split('P')[1][:3]
            x['branch'] = branch

            # Update format for Pxxx-x... to PROxxx-x... & similar for WIP
            if x['project'] != 'NR':
                x['project_short'] = 'PRO' + x['project_short'][1:4] + '-' + x['project_short'][4:]
                x['W'] = 'WIP' + x['W'][1:4] + '-' + x['W'][4:]

        # Now doing times
        # First, calculate the sum of actual unrounded hours
        actual_total_hours_unrounded = sum(time_ms for time_ms in project_tag_times.values()) / (1000 * 60 * 60)
        
        # Then, round this sum to the nearest half-hour if necessary
        actual_total_hours_nearest = round(actual_total_hours_unrounded * 2) / 2

        # Round each project_tag_combination total time to the nearest half-hour
        project_tag_times_rounded = project_tag_times.copy()
        for key, time_ms in project_tag_times_rounded.items():
            hours = time_ms / (1000 * 60 * 60)  # Convert ms to hours
            project_tag_times_rounded[key] = round(hours * 2) / 2  # Round to nearest half-hour
       
        actual_total_hours_rounded = sum(project_tag_times_rounded.values())

        # Assuming the discrepancy must be resolved in half-hour increments
        if actual_total_hours_rounded != actual_total_hours_nearest:
            discrepancy = actual_total_hours_rounded - actual_total_hours_nearest
            adjustments_needed = int(discrepancy * 2)  # Convert to how many half-hours need adjusting

            # Sort entries by rounded time descending, so we start adjustment from the largest
            sorted_keys = sorted(project_tag_times_rounded, key=project_tag_times_rounded.get, reverse=True)
            for key in sorted_keys:
                if adjustments_needed == 0:
                    break  # Stop if no more adjustments are needed
                # Ensure we don't reduce below 0.5 hours to maintain minimum billing increments
                if project_tag_times_rounded[key] >= 0.5:
                    project_tag_times_rounded[key] -= 0.5  # Reduce by half-hour
                    adjustments_needed -= 1  # Decrement the needed adjustments

        # Update rdat2 with times
        for entry in r_dat2['data']:
            # Create a key based on the project and charge_type
            project = entry['project']
            charge_type = entry['charge_type']
            key = (project, charge_type)

            # Find the corresponding rounded time and insert it into the entry
            if key in project_tag_times_rounded:
                entry['time_rounded'] = project_tag_times_rounded[key]
            else:
                entry['time_rounded'] = 0  # or handle as appropriate if the key is not found
        print(f'{actual_total_hours_nearest} hrs total.')
        
        # Advise user if no timesheet entries
        if len(r_dat2['data']) == 0:
            print('No timesheet entries.')
        
        # Save as Pandas dataframe
        self.times = self.create_df(r_dat2)
            
        return r_dat2

    
    def create_df(self, r_dat2):
        """Create Pandas dataframe with data."""
        data = []
        for i in r_dat2['data']:
            data.append({'Date': self.format_date_text(r_dat2['date']), 
                'Branch': i['branch'], 
                'Charge Type': i['charge_type'], 
                'Project No': i['project_short'], 
                'Job No': i['W'], 
                'Description': i['output_desc'], 
                'Hours': str(i['time_rounded'])})
        dataframe = pd.DataFrame(data)
        dataframe['Branch'] = pd.to_numeric(dataframe['Branch'])
        return dataframe


    def merge_cross_ref(self):
        """Merge cross_ref.xlsx into the datframe."""
        try:
            # Load merge data
            merge_data_branch = pd.read_excel('cross_ref.xlsx', 'Branch', header=None, names=['Branch', 'Full'])
            merge_data_charge = pd.read_excel('cross_ref.xlsx', 'ChargeType', header=None, names=['Charge Type', 'Full'])
            # Merge branch code
            times_branch = self.times.merge(merge_data_branch, how='left', on='Branch')
            times_branch.drop(columns=['Branch'], inplace=True)
            times_branch.rename(columns={"Full": "Branch"}, inplace=True)
            # Merge charge code
            times_charge = times_branch.merge(merge_data_charge, how='left', on='Charge Type')
            times_charge.drop(columns=['Charge Type'], inplace=True)
            times_charge.rename(columns={"Full": "Charge Type"}, inplace=True)
            # Then re-order
            times_updated = times_charge[['Date', 'Branch', 'Charge Type', 'Project No', 'Job No', 'Description', 'Hours']]
        except FileExistsError:
            print('File cross_ref.xlsx does not exist.')

        return times_updated


    def excelLoad(self):
        """Copy the timesheet data rows to the clipboard, excluding the header."""
        try:
            self.times_updated = self.merge_cross_ref()
            # Copy data to clipboard without the header
            self.times_updated.to_clipboard(index=False, header=False, excel=True)
            print('Data rows copied to clipboard. You can now paste them into your Excel workbook.')
        except Exception as e:
            print(f'ERROR: Unable to copy data to clipboard. {e}')


    def display_data(self):
        # Show from Pandas dataframe
        print('')
        print(self.times.to_string(index=False))
        print('')