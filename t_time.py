import json
import logging
import os.path
from datetime import datetime, timedelta

import requests
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, NamedStyle


class TimeSheetLoader():
    """ The class to handle completing timesheets daily. """

    def __init__(self):
        # Declare initial user vairables
        self.user_agent, self.api_key, self.workspace_id, self.excel_path = ('', '', '', '')
        # Load user details from settings file
        try:
            with open('settings.txt') as f:
                for line in f:
                    fields = line.strip().split()
                    # for security only input these pre-defined variables
                    if fields[0] == 'user_agent' or 'api_key' or 'workspace_id' or 'excel_path' or 'tracking':
                        # Handling the path on the computer needs special help
                        if fields[0] == 'excel_path':
                            path = r'{}'.format((' ').join(fields[2:]))
                            exec("self.%s = path" % (fields[0]))
                        elif fields[0] == 'tracking':
                            projects_string = (' ').join(fields[2:])
                            exec('self.%s = %s' % (fields[0], projects_string))
                        else:
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
        self.display_data(timesheet_data)
        if len(timesheet_data['data']) != 0:    # only prompt if data to enter
            user_input = input("Autocomplete keystrokes in Excel Online (enter) yes, (n) no? ")
            if user_input == '':
                self.autocomplete(timesheet_data)
            if user_input == 'n':
                pass
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
                print('\n! Error: missing project for item in Toggl. Press any button to reset program.')
                input()
                break
            elif i['project'] == 'NR':
                r_dat2['data'].append({'project': i['project'], 'project_short': '', 'W': '', 'charge_type': 'NR'}) 
            else:
                try:
                    short_string = i['project'].split()[0]     # project_short splits string  
                    short_project = short_string.split('/')[0].strip()
                    short_job = short_string.split('/')[1].strip()
                    r_dat2['data'].append({'project': i['project'], 'project_short': short_project, 'W': short_job, 'charge_type': ''})
                except IndexError:
                    print(f"ERROR There is an issue with how you have entered \"{i['project']}\". Try again...", end = '')
                    input()
                    break                       

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
                    if x['charge_type'] == '':
                        x['charge_type'] = i['tags'][0]


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
                               
        # Format the hours as required and save to new variable (if there are any entries)
        if len(r_dat2['data']) != 0:
            self.hours_function(r_dat2)  # proceed if entries
        else:
            print('No timesheet entries.')
        return r_dat2 


    def autocomplete(self, r_dat):
        """Autocompletes Excel file by controlling the keyboard to enter text."""

        print('\nThis feature is not yet operational.')
        #TODO add this feature


    def display_data(self, r_dat):
        # Print header
        print('\n{0:12} {1:12} {2:15} {3:14} {4:14} {5:70} {6:10}'.format('Date', 'Branch', 'Charge Type', 'Project No', 'Job No', 'Description', 'Hours'))
        # Print lines of data
        for i in r_dat['data']:
            print('{0:12} {1:12} {2:15} {3:14} {4:14} {5:70} {6:10}'.format(self.format_date_text(r_dat['date']), i['branch'], i['charge_type'], i['project_short'], i['W'], i['output_desc'], str(i['time_rounded'])))
        print('')