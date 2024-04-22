# import the json utility package since we will be working with a JSON object
import json
# import the AWS SDK (for Python the package name is boto3)
import boto3
# import time 
import time
from datetime import datetime
# import two packages to help us with dates and date formatting

# define the handler function that the Lambda service will use as an entry point
def lambda_handler(event, context):
    
    # create a DynamoDB object using the AWS SDK
    dynamodb = boto3.resource('dynamodb')
    # use the DynamoDB object to select our table
    table = dynamodb.Table('TogglCon.log')
    
    # Get the current GMT time
    gmt_time = time.gmtime()

    # store the current time in a human readable format in a variable
    # Format the GMT time string
    now = time.strftime('%a, %d %b %Y %H:%M:%S +0000', gmt_time)


    # extract values from the event object we got from the Lambda service and store in a variable
    togglapikey = event['togglapikey']
    date_str = event['date']
    email = event['email']
    workspace_ID = event['workspace_ID']
    
    
    # format extracted values to how they will need to be presented
    emailname = email.split('@')[0]
    # Assuming date_str is your date in "YYYY-MM-DD" format
    date_object = datetime.strptime(date_str, '%Y-%m-%d')
    # Now format this date object into "DD/MM/YY"
    date = formatted_date = date_object.strftime('%d/%m/%y')
    

    # write name and time to the DynamoDB table using the object we instantiated and save response in a variable
    response = table.put_item(
        Item={
            'ID-timestamp': now + "_" + email,
            'time': now,
            'email': email,
            'date': date,
            })


    # return a properly formatted JSON object
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        'body': json.dumps({"Data": [
            {
                "Date": f"{date}",
                "Branch": f"{emailname}",
                "Charge Type": "ABCABCAB-AB",
                "Project No": f"{togglapikey}",
                "Job No": "ABC0001111",
                "Description": "(Client) Planning",
                "Hours": "3.5"
            },
            {
                "Date": "05/04/24",
                "Branch": "Branch 1",
                "Charge Type": "TYPE 1",
                "Project No": "PROJ 2",
                "Job No": f"{workspace_ID}",
                "Description": "First aid training (3.5hr)",
                "Hours": "3.5"
            }
            ]
            })
    }