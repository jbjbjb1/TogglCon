import t_time
import os
from datetime import datetime, timedelta
from time import sleep


# Version and welcome message
version = '3.5'
print(f'---> togglcon, version {version} <---')

def get_and_handle_timesheet(date):
    try:
        timesheet_data = a.get_timesheet(date)
        return timesheet_data
    except t_time.MissingChargeTypeException as e:
        print(e)  # Print the custom error message
        return None
    except t_time.MissingProjectException as e:
        print(e)  # Print the custom error message for missing project
        return None
    except t_time.WrongProjectNameFormatException as e:
        print(e)  # Print the custom error message for missing project
        return None     

# Initiate class for timesheets
a = t_time.TimeSheetLoader()

# Terminal line interation with user to control program
choice = ''
while True:   
    choice = input('\nView today (enter), yesterday (y), specific (DD/MM/YY), help (h) or exit (e): ')    
    if choice == '':
        # Get today's timesheet and open it in Excel
        date = datetime.strftime(datetime.now(), '%d/%m/%y')
        if get_and_handle_timesheet(date) is not None:  #Run the program, if no errors allow the program to close.
            input('\nPress any key to exit...')
            exit()
    elif choice == 'y':
        # Get yesterday's timesheet
        date = datetime.strftime(datetime.now() - timedelta(1), '%d/%m/%y')
        timesheet_data = get_and_handle_timesheet(date)
    elif choice =='h':
        # See help
        print('App version:', version)
        print('To re-enter you user settings, edit or delete settings.txt in the same folder as this program and re-run togglcon.exe. See github for readme.')
    elif choice == 'e':
        # Exit program
        break
    else:
        # Assume user has entered date in format DD/MM/YY
        date = choice
        timesheet_data = get_and_handle_timesheet(date)