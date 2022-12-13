import t_time
import os
from datetime import datetime, timedelta
from time import sleep


# Version and welcome message
version = '3.3'
print(f'---> togglcon, version {version} <---')

# Initiate class for timesheets
a = t_time.TimeSheetLoader()

# Terminal line interation with user to control program
choice = ''
while True:   
    choice = input('\nFast-load (enter), view today (t), yesterday (y), specific (DD/MM/YY), help (h) or exit (e): ')    
    if choice == '':
        # Get today's timesheet and open it in Excel
        date = datetime.strftime(datetime.now(), '%d/%m/%y')
        timesheet_data = a.summary_data(date)
        a.excelLoad(timesheet_data)
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