import logic, local
import os
from datetime import datetime, timedelta
from time import sleep
import time
import json

# import the AWS SDK if in AWS environment
if 'AWS_EXECUTION_ENV' in os.environ:
    import boto3

# Version and welcome message
version = '4.0.0'
print(f'---> togglcon, version {version} <---')


def lambda_handler(event, context):
    
    # extract values from the event object we got from the Lambda service and store in a variable
    togglapikey = event['togglapikey']
    date_str = event['date']
    email = event['email']
    workspace_ID = event['workspace_ID']

    # Convert the date format from YYYY-MM-DD to DD/MM/YY
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    date_str = date_obj.strftime('%d/%m/%y')

    # run the logic to get the timesheet data
    timesheet = logic.TimeLogic(togglapikey, email, workspace_ID)
    result = timesheet.summary_data(date_str) # advises if succeeded, if it does passes dataframe
    data = json.dumps({"Data": json.loads(result['data'].to_json(orient='records'))}) # load json, put in "Data" dict, then format as json

    # return to web app the json format to display
    if result['status'] == 'error':
        return {
            'statusCode': 400,
            'body': result['error']     #return error
        }
    else:
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': data  
        }

    # Code to save details to database

    # create a DynamoDB object using the AWS SDK
    dynamodb = boto3.resource('dynamodb')
    # use the DynamoDB object to select our table
    table = dynamodb.Table('TogglCon.log')
    
    # Get the current GMT time
    gmt_time = time.gmtime()

    # store the current time in a human readable format in a variable
    # Format the GMT time string
    now = time.strftime('%a, %d %b %Y %H:%M:%S +0000', gmt_time)

    # write name and time to the DynamoDB table using the object we instantiated and save response in a variable
    response = table.put_item(
        Item={
            'ID-timestamp': now + "_" + email,
            'time': now,
            'email': email,
            'date': date,
            })


def run_local(date):
    """ If running locally, load local package and gather settings to use for api calls. """

    local_instance = local.TimeLocal()  # get settings.txt loaded or setup

    # get timesheet data for date
    timesheet = logic.TimeLogic(local_instance.api_key, local_instance.user_agent, local_instance.workspace_id) 
    print('Loading...', end = '') # let user know loading
    result = timesheet.summary_data(date) # timesheet run
    local_instance.times = timesheet.times # pass variable to local_instance
    
    if result['status'] == 'error': # show error if one
        print(result['error']) 
    elif timesheet.notimesheetentries == True: # advise if no timesheets
        print('No timesheet entries.')
    else:
        print(f'{timesheet.actual_total_hours_nearest} hrs total.')
        local_instance.display_data()    # print timesheet to terminal
        local_instance.excelLoad()   # copy to excel


def main():
    # Terminal line interation with local user to control program
    choice = ''
    while True:   
        choice = input('\nView today (enter), yesterday (y), specific (DD/MM/YY), help (h) or exit (e): ')    
        if choice == '':
            # Get today's timesheet and open it in Excel
            date = datetime.strftime(datetime.now(), '%d/%m/%y')
            if run_local(date) is not None:  #Run the program, if no errors allow the program to close.
                input('\nPress any key to exit...')
                exit()
        elif choice == 'y':
            # Get yesterday's timesheet
            date = datetime.strftime(datetime.now() - timedelta(1), '%d/%m/%y')
            timesheet_data = run_local(date)
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
            timesheet_data = run_local(date)


if __name__ == "__main__":
    main()