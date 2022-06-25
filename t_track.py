#Add to settings.txt a line with "tracking =  [['Axxxxxxx - machine build', 70, '11/06/21']]" to use this feature (name, hours, due date)


from datetime import datetime, timedelta
import requests
import json


class Project():
    """ Stores tracking details of a single project. """

    def __init__(self, data):
        self.project_no = data[0]
        self.hours_avail = data[1]
        self.due_date = datetime.strptime(data[2], '%d/%m/%y')     # converts to datetime
        self.days_left = (datetime.strptime(data[2], '%d/%m/%y') - datetime.now()).days + 2     #TODO update to hours then calculate days as decimal, using +2 to get correction for now.
        self.hours_spent = 0                                       # initialise variable

    def print_stats(self):
        percent_hours = (self.hours_spent / self.hours_avail) * 100
        hrs_remaining = self.hours_avail - self.hours_spent
        days_ft = hrs_remaining / 7                                 # assume 7 hrs per day at full time
        if days_ft == 0:
            buffer = 0
        else:
            buffer = (self.days_left / days_ft) * 100 - 100
        # TODO update below to be column printing style like t_time
        print(f'{self.project_no}; {percent_hours:.0f}% hours spent @ {buffer:.0f}% buffer. Due in {self.days_left:.0f}d; {days_ft:.1f}d ({hrs_remaining:.1f}hrs) work left ({self.hours_spent:.1f}/{self.hours_avail} hrs)')


class ProjectTracker():
    """ The class to handle tracking hours on projects. """

    def __init__(self, a):
        self.a = a
        self.projects = []
        for i in a.tracking:        # TODO will cause error if no projects to track
            self.projects.append(Project(i))


    def get_api_data(self):
        """ 
        Get details of project summary by API. 
        
        Details of API here: https://github.com/toggl/toggl_api_docs/blob/master/reports.md
        """
        
        # Format date required by Toggl api
        since = (datetime.now() - timedelta(days=300)).strftime('%Y-%m-%d')      # max span is 1 year
        until = datetime.now().strftime('%Y-%m-%d')
        # Set paramaters for api call
        parameters = {
        'user_agent': self.a.user_agent,
        'workspace_id':self.a.workspace_id,
        'since': since,
        'until': until,
        }
        r = requests.get('https://api.track.toggl.com/reports/api/v2/details', auth=(self.a.api_key, 'api_token'), params=parameters)
        return r.json() 

    
    def extract_data(self, project):
        """ Get sum of hours spent for a project and its description. """
        time_hrs = 0                                        # re-set each time this is done
        project.hours_spent = 0                             # re-set each time this is done
        for i in self.data['data']:                         # looping over multiple times, if slows performance refactor this
            if project.project_no in i['project']:
                time_hrs = i['dur'] / (60 * 60 * 1000)      # api has time in ms
                project.hours_spent += time_hrs


    def print_job_status(self):
        """ Call class to update project statistics then print. """
        
        self.data = self.get_api_data()  # all api data
        print('\nProject status:')
        for project in self.projects:
            self.extract_data(project)
            project.print_stats()