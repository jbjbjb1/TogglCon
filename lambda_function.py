import t_time
import os
# import two packages to help us with dates and date formatting
import time
from datetime import datetime, timedelta
from time import sleep
# import the json utility package since we will be working with a JSON object
import json
# import the AWS SDK (for Python the package name is boto3)
import boto3


# Version and welcome message
version = '3.9'


# create a DynamoDB object using the AWS SDK
dynamodb = boto3.resource('dynamodb')
# use the DynamoDB object to select our table
table = dynamodb.Table('HelloWorldDatabase')

# define the handler function that the Lambda service will use as an entry point
def lambda_handler(event, context):
 # Get the current GMT time
    gmt_time = time.gmtime()

    # store the current time in a human readable format in a variable
    # Format the GMT time string
    now = time.strftime('%a, %d %b %Y %H:%M:%S +0000', gmt_time)


# extract values from the event object we got from the Lambda service and store in a variable
    name = event['firstName'] +' '+ event['lastName']
# write name and time to the DynamoDB table using the object we instantiated and save response in a variable
    response = table.put_item(
        Item={
            'ID': name,
            'LatestGreetingTime':now
            })
# return a properly formatted JSON object
    return {
        'statusCode': 200,
        'body': json.dumps('Your interest has been registered, ' + name)
    }


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
    except t_time.NoDayDataException as e:
        print(e)  # Print the custom error message for missing project
        return None 


# Initiate class for timesheets
a = t_time.TimeSheetLoader()


"""
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
"""