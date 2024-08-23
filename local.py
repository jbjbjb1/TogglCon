import re
import json
import logging
import os.path
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import requests
import textwrap
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, NamedStyle

class TimeLocal():
    """ The class to handle local machine tasks for timesheet app. """

    def __init__(self):
        
        # Declare initial user vairables
        self.user_agent, self.api_key, self.workspace_id, self.website, self.times = ('', '', '', '', None)
        
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
        r = requests.get('https://api.track.toggl.com/api/v9/workspaces', auth=(self.api_key, 'api_token'))
        r = r.json()
        ids = []
        for entry in r:
            ids.append(str(entry['id']) + ' (' + entry['name'] + ')')
        return ids 

    def get_timesheet(self, date):
        """This is the master function to run to get a day's timesheet entry."""
        timesheet_data = self.summary_data(date)
        self.display_data()
        if len(timesheet_data['data']) != 0:    # only proceed if there is data to continue with
            self.excelLoad()
        return timesheet_data

    def excelLoad(self):
        """Copy the timesheet data rows to the clipboard, excluding the header."""
        try:
            # Then re-order
            self.times_updated = self.times[['Date', 'Branch', 'Charge Type', 'Project No', 'Job No', 'Description', 'Hours']]
            
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