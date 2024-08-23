import logic, local
import os
from datetime import datetime, timedelta
from time import sleep

if 
    # import the AWS SDK (for Python the package name is boto3)
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

    # run the logic to get the timesheet data
    instance = logic.TimeLogic(togglapikey, email, workspace_ID)
    instance.summary_data(date_str)
    df = instance.times # get timesheet data
    result = df.to_json(orient='records') #convert for sending as JSON

    # If an error was returned
    if isinstance(result, dict) and 'error' in result:
        return {
            'statusCode': 400,
            'body': result['error']
        }

    return {
        'statusCode': 200,
        'body': result
    }

    # save details to database

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
    
    

    try:
        local_instance = local.TimeLocal()  # get settings.txt loaded/setup

        instance = logic.TimeLogic()
        instance.summary_data(date)
        df = instance.times # get timesheet data

        pass

    except t_time.MissingChargeTypeException as e:
        print(e)  # Print the custom error message
        return None
    except t_time.MissingProjectException as e:
        print(e)  # Print the custom error message
        return None
    except t_time.WrongProjectNameFormatException as e:
        print(e)  # Print the custom error message
        return None
    except t_time.NoDayDataException as e:
        print(e)  # Print the custom error message
        return None
    except t_time.DateOutOfRangeException as e:
        print(e)  # Print the custom error message
        return None 

def main():
    # Terminal line interation with user to control program
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