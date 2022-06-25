import t_time, t_track
from datetime import datetime, timedelta
from time import sleep


# Version and welcome message
version = '2.0'
print(f'---> togglcon, version {version} <---')

# Initiate class for timesheets
a = t_time.TimeSheetLoader()
b = t_track.ProjectTracker(a)

# Terminal line interation with user to control program
choice = ''
while True:   
    choice = input('\nFast-fill (enter), view today (t), yesterday (y), specific (DD/MM/YY), proj. status (s), help (h) or exit (e): ')    
    if choice == '':
        # Get today's timesheet and enter it
        date = datetime.strftime(datetime.now(), '%d/%m/%y')
        timesheet_data = a.summary_data(date)
        a.autocomplete(timesheet_data)
        b.print_job_status()            # show tracking, TODO will cause error if no projects to track
        input('\nPress any key to exit...')
        exit()
    elif choice == 't':
        # Get today's timesheet
        date = datetime.strftime(datetime.now(), '%d/%m/%y')
        timesheet_data = a.get_timesheet(date)
    elif choice == 'y':
        # Get yesterday's timesheet
        date = datetime.strftime(datetime.now() - timedelta(1), '%d/%m/%y')
        timesheet_data = a.get_timesheet(date)
    elif choice =='s':
        # Display status of tracked jobs (time against planned time)
        b.print_job_status()
    elif choice =='h':
        # See help
        print('App version:', version)
        print('To re-enter you user settings, edit or delete settings.txt in the same folder as this program and re-run togglcon.exe.')
    elif choice == 'e':
        # Exit program
        break
    else:
        # Assume user has entered date in format DD/MM/YY
        date = choice
        timesheet_data = a.get_timesheet(date)