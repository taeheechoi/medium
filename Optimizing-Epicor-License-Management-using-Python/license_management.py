import json
import os

import requests

license_limits = {
    'DefaultUser': 10,
    'DataCollection': 10
}

usage_threshold = 0.95

license_types = {
    '00000000-0000-0000-0000-000000000000': 'DefaultUser',
    '11111111-1111-1111-1111-111111111111': 'DataCollection',
}


def check_license_usage(response):
    '''
    Checks the license usage based on the given response from the license API.
    Counts the number of sessions for each session type and compares them with the license limits.
    If the usage exceeds the threshold, a warning message is returned.
    Otherwise, an empty string is returned.
    '''

    session_counts = {}

    for row in response.json().get('value', []):
        session_type = license_types.get(str(row.get('SessionType')))

        if session_type in session_counts:
            # Increment session count if session type already exists
            session_counts[session_type] += 1
        else:
            # Initialize session count if session type is encountered for the first time
            session_counts[session_type] = 1

    # Get current count of DefaultUser sessions
    current_default_user_count = int(session_counts.get('DefaultUser', 0))
    # Get current count of DataCollection sessions
    current_data_collection_count = int(
        session_counts.get('DataCollection', 0))

    # Check if current counts exceed the usage threshold for respective license types
    if (
        current_default_user_count >= license_limits.get('DefaultUser') * usage_threshold or
        current_data_collection_count >= license_limits.get(
            'DataCollection') * usage_threshold
    ):
        return '95% of the total licenses have been reached, so please log out of Epicor if you are not actively using it.'
    else:
        return ''  # Return empty string if license usage is below the threshold


def get_license_usage():
    '''
    Retrieves the license usage by sending a GET request to the license API.
    Returns the response object if successful, otherwise returns None.
    '''

    try:
        # Get server URL from environment variable
        server = os.getenv('SERVER')
        # Get username from environment variable
        auth_name = os.getenv('USER_NAME')
        # Get password from environment variable
        auth_password = os.getenv('PASSWORD')

        URL = f'{server}/api/v1/Ice.BO.AdminSessionSvc/List?$filter=Expired%20eq%20false'

        # Send GET request to the API endpoint with basic authentication
        response = requests.get(
            URL, auth=requests.auth.HTTPBasicAuth(auth_name, auth_password))

        response.raise_for_status()  # Raise exception if response status is not successful

        return response

    except requests.exceptions.RequestException as e:
        print(f'An error occurred: {str(e)}')
        return None


def send_notification(message):
    '''
    Sends the error message as a notification to the specified webhook URL.
    Returns the response status code of the notification request.
    '''
    webhook_url = ''  # Replace with your actual webhook URL

    data = {
        'text': message
    }

    response = requests.post(webhook_url, data=json.dumps(data))

    if response.status_code == 200:
        print('Notification sent successfully.')
    else:
        print('Failed to send notification.')


if __name__ == '__main__':
    response = get_license_usage()

    if response is not None:
        result = check_license_usage(response)

        if result:
            send_notification(result)
