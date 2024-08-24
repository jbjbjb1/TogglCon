""" export TOGGL_API_KEY='your_toggl_api_key_here'
export WORKSPACE_ID='your_workspace_id_here'
export USER_EMAIL='example@example.com'

or for Windows

set TOGGL_API_KEY=your_toggl_api_key_here
set WORKSPACE_ID=your_workspace_id_here
set USER_EMAIL=example@example.com """

import os
import togglcon

def test_lambda_handler():
    # Fetch environment variables
    togglapikey = os.getenv('TOGGL_API_KEY')
    workspace_ID = os.getenv('WORKSPACE_ID')
    email = os.getenv('USER_EMAIL')
    
    # Mock event and context
    event = {
        'togglapikey': togglapikey,
        'date': '21/08/24',  # Example date
        'email': email,
        'workspace_ID': workspace_ID
    }
    
    context = {}  # In most cases, context can be left as an empty dict

    # Call the lambda_handler function with the mocked event and context
    response = togglcon.lambda_handler(event, context)
    
    # Print the response to see the output
    print('Status Code:', response['statusCode'])
    print('Response Body:', response['body'])
    print('\n')
    print(response)

# Run the test
if __name__ == "__main__":
    test_lambda_handler()
