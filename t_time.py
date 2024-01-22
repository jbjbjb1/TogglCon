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
            self.excel_path = input('Path to excel file for your timesheet: ')
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


    def hours_function(self, r_dat):
        """Check there are no projects rounded to 0 hrs."""
        # Add the hours lost/gained by rounding to the one most rounded
        hrs_total = 0
        hrs_diff = []
        for i in r_dat['data']:
            hrs_total += self.round_half_hr(i['time'])
            hrs_diff.append( i['time']/(60*60*1000) - self.round_half_hr(i['time']) )
        
        # Don't change any hours (previously was aiming for 7.5 hrs)
        hrs_to_change = 0
        
        # Find the time entry that was most rounded
        max_index = hrs_diff.index(max(hrs_diff))
        
        # Add new entries for data with rounded time and time added to most rounded time.
        for idx, i in enumerate(r_dat['data']):
            if idx == max_index and hrs_to_change != 0:
                i['time_rounded'] = self.round_half_hr(i['time']) + hrs_to_change
                print(i['project'],'has', hrs_to_change,'hours added due to rounding.')
                continue
            elif idx == max_index and hrs_to_change == 0:
                i['time_rounded'] = self.round_half_hr(i['time'])
                print(f'{hrs_total} hrs total.')
                continue
            i['time_rounded'] = self.round_half_hr(i['time'])

        # If project time entry is 0.0hrs, remove from list
        for idx, i in enumerate(r_dat['data']):
            if i['time_rounded'] == 0:
                del r_dat['data'][idx]


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
        # Create a new variable for summarised data
        r_dat2 = {'data': [ ] }
        # Save the date in the new vaiable
        r_dat2['date'] = date

        # Get a list of the unique projects as list of dictionaries
        projects_list = []
        try:
            for i in r_dat['data']:
                if {'project': i['project']} not in projects_list:
                    # assign a new entry to the dictionary of project
                    projects_list.append({'project': i['project']})
        except KeyError:
            # Include error checking if API key is wrong
            try:
                print(r_dat['error']['message'])
            except KeyError:
                raise
        # Create base dataframe with above for timesheet
        for i in projects_list:
            if i['project'] == None:
                raise MissingProjectException(f"One of your entries is missing a project. Please fix and try again.")
            elif i['project'] == 'NR':
                r_dat2['data'].append({'project': i['project'], 'project_short': '', 'W': '', 'charge_type': 'NR'}) 
            else:
                try:
                    short_string = i['project'].split()[0]     # project_short splits string  
                    short_project = short_string.split('/')[0].strip()
                    short_job = short_string.split('/')[1].strip()
                    r_dat2['data'].append({'project': i['project'], 'project_short': short_project, 'W': short_job, 'charge_type': ''})
                except IndexError:
                    raise WrongProjectNameFormatException(f"The project name \"{i['project']}\" has not followed the correct formatting. Please fix and try again.")               

        # Add formatted data
        b_times = []
        for x in r_dat2['data']:
            x['client'] = ''
            x['charge_type'] = ''
            for i in r_dat['data']:
                if x['project'] == i['project']:
                    # Add client
                    if i['client'] != x['client']:
                        x['client'] = i['client']
                    # Add charge type tag
                    # TODO this is not correct place as project may have multiple tags that need to be split out
                    try:
                        if x['charge_type'] == '':
                            x['charge_type'] = i['tags'][0]
                    except IndexError:
                        raise MissingChargeTypeException(f"Missing charge type tag for {i['description']}. Please fix and try again.")


            # Add the times (milliseconds) to each of the unique projects.
            a_times = 0
            for i in r_dat['data']:
                if x['project'] == i['project']:
                    a_times += i['dur']
            b_times.append(a_times)
            x['time'] = a_times

            # Add comments with time if more than one comment. Store descriptions to 'temp_desc' and time to 'temp_desc_time'.
            x['temp_desc'] = []
            x['temp_desc_time'] = []
            for i in r_dat['data']:
                if x['project'] == i['project']:
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
            if x['project'] == 'NR':
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
            
            pass
                               
        # Format the hours as required and save to new variable (if there are any entries)
        if len(r_dat2['data']) != 0:
            self.hours_function(r_dat2)  # proceed if entries
        else:
            print('No timesheet entries.')
        
        # Save as Pandas dataframe
        self.times = self.create_df(r_dat2)
        
        return r_dat2


    def autocomplete(self):
        """Autocompletes Excel file by controlling the keyboard to enter text."""

        print('\nThis feature is not yet operational.')
        #TODO add this feature

    
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
            print('Data rows copied to clipboard. You can now paste them into your online Excel workbook.')
        except Exception as e:
            print(f'ERROR: Unable to copy data to clipboard. {e}')


    def display_data(self):
        # Show from Pandas dataframe
        print('')
        print(self.times.to_string(index=False))
        print('')