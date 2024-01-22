# Readme
This app takes timesheet information from Toggl.com, restructures it based on the criteria described below, presents a summary of the information in a console window, then offers to load in an Excel file with easy copy/paste ability.

The method that information needs to be put into Toggl.com is:
* A client must be defined for each project,
* Each project shall be in the format: 'Pxxxxxxx/Wxxxxxxx - Project title/Job title'
* Tags of your choise must be used against each time entry
* If you want to cross reference the tags to a longer string (only for Branch, ChargeType), then you need to fill out cross_ref.xlsx like the sample shown

The output from Togglcon is to:
* Split out the "(WIPxxx-xxxx)" number from each line entry so it is shown in its own column
* All times in the output presentation view will be rounded to the nearest 0.5 hr.
* In the description field, add the client name in brackets at the start, e.g. "(Client) Description"
* In the description field, if there are multiple entries for the same project/WIPxxx-xxxx, it will group them and the second entry onwards will have the duration in brackets, e.g. "(Client) Description, Description1 (1.0hr), Description2 (0.5hr)"
* If you want to cross reference the tags to a longer string (only for Branch, ChargeType) before opening in Excel

Errors that will be advised are:
* If the format 'Pxxxxxxx/Wxxxxxxx - Project title/Job title' in Toggl is not followed
* If trying to load the Excel file and it is already open
* If you don't have a cross_ref.xlsx to merge with (will still display data as-is in Excel)

Note: a current limitation is that there can only be one tag for a project/job combination on each day's timesheet.

# How to run and use it
1. Sign up for Toggl.com
2. Installation process
        a) Install Python 3.9 installed on your computer.
        b) Install Visual Studio Code, go to the folder of the code, View -> Command Pallet and choose Python
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
* Charge type tags from Toggl not fully functional, needs to split into multiple rows if different charge types
* Error logs not writing

# Improvements completed
* 22/1/24 - if there is an error, don't crash, leave error on screen. Added icon file.
* 29/9/23 - removed project/job number ending digit limit of 4
* 26/6/23 - updated to fix 'fast fill' working and gave preview of data, removed 'today' menu option
* 24/6/23 - updated from Pxxx-x... to PROxxx-x... & similar for WIP.
* 24/6/23 - fixed issue of cross_ref.xlsx file always not importing first row
* 13/7/22 - tracking was missing off the auto created settings file causing the program to crash

# Interested to contribute?
See the API references here and contribure https://github.com/toggl/toggl_api_docs !