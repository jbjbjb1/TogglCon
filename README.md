# Readme
This app takes timesheet information from Toggl.com, restructures it based on the criteria described below, presents a summary of the information in a console window, then offers to auto-type using the keyboard into an Excel file in Office Online.

This app also has a feature to track hours spent on projects. It is done by adding to settings.txt in the format `tracking =  [['Pxxxxxxx - machine build', 70, '11/06/21']]` where Pxxxxxxx is the project number, 70 is the hours allowed, and the date is the due date. There is a menu option in togglcon to view status of jobs. It will then gather up the sum of hours spent on the job over the last 12 months and report it in the format: "Pxxxxxxx - machine build; 60% hrs spent & 3d remaining (35/59 hours)."

The method that information needs to be put into Toggl.com is:
* A client must be defined for each project,
* The description field must start with the job number in brackets unless it is NR; "(Wxxxxxxx) Description"

The output from Togglcon is to:
* Split out the "(Wxxxxxxx)" number from each line entry so it is shown in its own column

# Getting Started
1. Installation process
        You will need Python 3.9 installed on your computer.
2. API references
        Toggl API was used: https://github.com/toggl/toggl_api_docs
3. Settings
        When you start the app it will prompt you and automatically create settings.txt. There is a sample `_settings.txt` file to view. The user agent is the user's email so that Toggl can contact them if there are any issues with the API requests.
4. Export to Excel
        The app will write the summarised timesheet row from Toggl to the next free line in the Excel document.

# Build and Test
1. First time
        `pip install pipenv`
2. Run
        Use Visual Studio Code, clone from remote repository, there is an exisiting Pipfile for a pipenv. Use that pipenv to run the program with `pipenv install` for the first time or `pipenv shell` to enter the shell. If the debug is not picking up the pipenv, follow this: https://stackoverflow.com/questions/72115439/python-pipenv-not-display-in-the-python-interpreter
3. Shortcut
        Open `_togglcon.bat` and update as instructed. THis file can then be a shortcut on the desktop. Note that this bat file runs from anaconda, whereas the above method is using pipenv.

# Updates to app
* TBA

# Improvements needed
The following are in order of priority:
* If there is an error, don't crash, leave error on screen
* Error logs not writing
* Seems to be a bug if start a time entry with 'time'
* Add functionality to sum up hours against documents on certain projects
* Allow for different project / job number structures (via setting in settings.txt)

# Improvements completed
* 13/7/22 - tracking was missing off the auto created settings file causing the program to crash