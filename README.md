# Readme
This app takes timesheet information from Toggl.com, restructures it based on the criteria described below, presents a summary of the information in a console window, then offers to auto-type using the keyboard into an Excel file in Office Online.

This app also has a feature to track hours spent on projects. It is done by adding to settings.txt in the format `tracking =  [['Pxxxxxxx - machine build', 70, '11/06/21']]` where Pxxxxxxx is the project number, 70 is the hours allowed, and the date is the due date. There is a menu option in togglcon to view status of jobs. It will then gather up the sum of hours spent on the job over the last 12 months and report it in the format: "Pxxxxxxx - machine build; 60% hrs spent & 3d remaining (35/59 hours)."

The method that information needs to be put into Toggl.com is:
* A client must be defined for each project,
* The description field must start with the job number in brackets unless it is NR; "(Wxxxxxxx) Description"

The output from Togglcon is to:
* Split out the "(Wxxxxxxx)" number from each line entry so it is shown in its own column
* All times in the output presentation view will be rounded to the nearest 0.5 hr.
* In the description field, add the client name in brackets at the start, e.g. "(Client) Description"
* In the description field, if there are multiple entries for the same project/Wxxxxxxx, it will group them and the second entry onwards will have the duration in brackets, e.g. "(Client) Description, Description1 (1.0hr), Description2 (0.5hr)"

# How to run and use it
1. Sign up for Toggl.com
2. Installation process
        a) Install Python 3.9 installed on your computer.
        b) Install Visual Studio Code
        c) `pip install pipenv`
        d) There is an exisiting Pipfile for a pipenv. Use that pipenv to run the program with `pipenv install`.
        e) From now on you only need to enter `pipenv shell` to enter the shell or use VS Code environments
        f) If the debug is not picking up the pipenv, follow this: https://stackoverflow.com/questions/72115439/python-pipenv-not-display-in-the-python-interpreter
        g) You should now be able to run TogglCon by putting into terminal `python togglcon.py`
3. (Optional) Batch file for program shortcut
        a) Install Anaconda
        b) Open `_togglcon.bat` and update as instructed. This file can then be a shortcut on the desktop. 
        c) Remove the comment at the top of the bat file after following the instructions
3. Settings
        When you start the app it will prompt you and automatically create settings.txt. There is a sample `_settings.txt` file to view. The user agent is the user's email so that Toggl can contact them if there are any issues with the API requests.
4. Auto type into Excel
        When the app prompts you, it will give you a few seconds to click in the Office Online Excel sheet before the autotyping starts.

# Improvements needed
The following are in order of priority:
* If there is an error, don't crash, leave error on screen
* Error logs not writing
* Seems to be a bug if start a time entry with 'time'
* Add functionality to sum up hours against documents on certain projects

# Improvements completed
* 13/7/22 - tracking was missing off the auto created settings file causing the program to crash

# Interested to contribute?
See the API references here and contribure https://github.com/toggl/toggl_api_docs !