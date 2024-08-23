import re
import json
import logging
import os.path
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import requests


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

class DateOutOfRangeException(Exception):
    """Exception raised for no data on day selected."""
    pass

class TimeLogic():
    """ The class to handle the logic of collecting the timesheets. """

    def __init__(self,togglapikey, email, workspace_ID):
        self.api_key = togglapikey # for api
        self.user_agent = email # for api
        self.workspace_id = workspace_ID # for api
        self.times = None   # df of timesheet
        self.actual_total_hours_nearest = None  # populate later if data
        self.notimesheetentries = False # use to idenrify no timesheet entries


    def get_detailed_data(self, date):
        """Get detailed data for a specific date from toggl api"""
        # Format date required by Toggl api
        try:
            date = datetime.strptime(date, '%d/%m/%y').strftime('%Y-%m-%d')
        except ValueError:
            raise DateOutOfRangeException(f"This date does not exist. Please check and try again.")
        # Set paramaters for api call
        parameters = {
        'user_agent': self.user_agent,
        'workspace_id':self.workspace_id,
        'since': date,
        'until': date,
        'tag_ids': '',
        }
        # Get data from api
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
       

    def summary_data(self, date):
        """Get detailed data and summarises to required format for timesheet."""
        try:        
            # Get detailed timesheet
            r_dat = self.get_detailed_data(date)
            # If r_dat is empty (i.e., no entries), let user know and stop the process
            if r_dat['data'] == []:
                raise NoDayDataException(f"There is no timesheet data entered for this day.")
            # Create a new variable for summarised data
            r_dat2 = {'data': []}
            # Save the date in the new variable
            r_dat2['date'] = date

            # Get a list of the unique project/tag combinations as a list of dictionaries
            projects_list = []
            try:
                for i in r_dat['data']:
                    # Consider both project and tag for uniqueness
                    try:
                        project_tag_combination = [{'project': i['project'], 'tag': i['tags'][0]}]
                        if project_tag_combination not in projects_list:
                            # Assign a new entry to the dictionary of project
                            projects_list.append(project_tag_combination)
                    except IndexError:
                        raise MissingChargeTypeException(f"Missing charge type tag for {i['description']}. Please fix and try again.")
            except KeyError:
                raise KeyError
            
            # Create base dataframe with above for timesheet
            for entry in projects_list:
                entry = entry[0]
                if entry['project'] is None:
                    raise MissingProjectException(f"One of your entries is missing a project. Please fix and try again.")
                elif entry['project'] == 'NR':
                    r_dat2['data'].append({'project': entry['project'], 'project_short': '', 'W': '', 'charge_type': entry['tag']}) 
                else:
                    try:
                        # Extract project number and job number
                        project_parts = entry['project'].split(' - ')
                        project_no = project_parts[0].split('/')[0].strip()
                        if project_no[0:2] != 'P-':
                            project_no = 'PRO' + project_no[1:4] + '-' + project_no[4:]
                        job_no = project_parts[0].split('/')[1].strip()
                        if job_no[0] != 'J':
                            job_no = 'WIP' + job_no[1:4] + '-' + job_no[4:]
                    except IndexError:
                        raise WrongProjectNameFormatException(f"The project name \"{entry['project']}\" has not followed the correct formatting. Please fix and try again.")

                    # Validate project and job number formats
                    if not (re.match(r'[A-Z]-\d[A-Z]{3}-\d{3}', project_no) or re.match(r'[A-Z]{3}\d{3}', project_no)):
                        raise WrongProjectNameFormatException(f"The project name \"{project_no}\" has not followed the correct formatting. Please fix and try again.")
                    if not (re.match(r'[A-Z]{3}-\d{3}', job_no) or re.match(r'[A-Z]{3}\d{3}', job_no)):
                        raise WrongProjectNameFormatException(f"The job number \"{job_no}\" in Toggl should be a) [J][2xletter]-[3xdigit], or b) W[3xdigit]")

                    r_dat2['data'].append({'project': entry['project'], 'project_short': project_no, 'W': job_no, 'charge_type': entry['tag']})

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

                # Set branch to an empty string
                x['branch'] = ''

                # No need to update format for project_short and W as it's not required

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
                discrepancy = actual_total_hours_nearest - actual_total_hours_rounded
                discrepancy_sign = discrepancy / abs(discrepancy)
                adjustments_needed = int(discrepancy * 2)  # Convert to how many half-hours need adjusting

                # Sort entries by rounded time descending, so we start adjustment from the largest
                sorted_keys = sorted(project_tag_times_rounded, key=project_tag_times_rounded.get, reverse=True)
                for key in sorted_keys:
                    if adjustments_needed == 0:
                        break  # Stop if no more adjustments are needed
                    # Ensure we don't reduce below 0 hours to maintain minimum billing increments
                    if project_tag_times_rounded[key] >= 0.5:
                        project_tag_times_rounded[key] += 0.5 * discrepancy_sign  # Increase or reduce the time based on the value of discrepancy
                        adjustments_needed -= 1 * discrepancy_sign  # Decrement the needed adjustments the correct way

            # Update r_dat2 with times
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

            # Filter out entries with time_rounded == 0
            r_dat2['data'] = [entry for entry in r_dat2['data'] if entry['time_rounded'] > 0]

            self.actual_total_hours_nearest = actual_total_hours_nearest    # save as variable to report later

            # Advise user if no timesheet entries
            if len(r_dat2['data']) == 0:
                self.notimesheetentries = True
                pass

            # Save as Pandas dataframe
            self.times = self.create_df(r_dat2)
            return {"status": "success", "data": self.times}
        
        except (MissingChargeTypeException, MissingProjectException, WrongProjectNameFormatException, NoDayDataException, DateOutOfRangeException) as e:
            return {"status": "error", "error": str(e)}

        except Exception as e:
            return {"status": "error", "error": f"An unexpected error occurred: {str(e)}"}

    
    def create_df(self, r_dat2):
        """Create Pandas dataframe with data."""
        data = []
        for i in r_dat2['data']:
            data.append({'Date': self.format_date_text(r_dat2['date']), 
                'Branch': '', 
                'Charge Type': i['charge_type'], 
                'Project No': i['project_short'], 
                'Job No': i['W'], 
                'Description': i['output_desc'], 
                'Hours': str(i['time_rounded'])})
        dataframe = pd.DataFrame(data)
        # Sort the DataFrame by 'Project No'
        dataframe = dataframe.sort_values(by='Project No', ascending=False)
        return dataframe