# Readme
This app takes timesheet information from Toggl.com, restructures it based on the criteria described below, presents a summary of the information in a console window, then offers to load in an Excel file with easy copy/paste ability.

The method that information needs to be put into Toggl.com is:
* A client must be defined for each project,
* Each project shall be in the format (where 'x' is number and 'a' is letter): 
- 'P-xaa-xxx-xxxxx/Jaa-xxx-xxxxx - Project title/Job title', or
- 'Pxxxxxxx/W[7 or 8 x] - Project title/Job title'
* The last 4 or 5 digits can be left off if needed
* Tags of your choise must be used against each time entry
* If you want to cross reference the tags to a longer string (only for Branch, ChargeType), then you need to fill out cross_ref.xlsx like the sample shown

The output from Togglcon is to:
* For numbers Pxxxxxxx/W[7 or 8 x], they will be converted to Paaxxx-xxxx/Waaxxx-[4 or 5 x]
* All times in the output presentation view will be rounded to the nearest 0.5 hr.
* In the description field, add the client name in brackets at the start, e.g. "(Client) Description"
* In the description field, if there are multiple entries for the same project/WIPxxx-xxxx, it will group them and the second entry onwards will have the duration in brackets, e.g. "(Client) Description, Description1 (1.0hr), Description2 (0.5hr)"
* If you want to cross reference the tags to a longer string (only for Branch, ChargeType) before opening in Excel

Errors will be advised for common issues such as non-existant dates, Project title/Job title format not correct etc.

# How to run and use it
1. Sign up for Toggl.com
2. Installation process
        a) Install Python 3.9 installed on your computer.
        b) In terminal run `pip install pipenv`
        d) There is an exisiting Pipfile for a pipenv. Use that pipenv to run the program with `pipenv install`.
        e) If the debug is not picking up the pipenv, follow this: https://stackoverflow.com/questions/72115439/python-pipenv-not-display-in-the-python-interpreter
3. Batch file for program shortcut
        a) Double click on togglcon.bat to run the program. You can right click on it and send a shortcut to the desktop and put togglcon.ico as the icon.
3. Settings
        When you start the app it will prompt you and automatically create settings.txt. There is a sample `_settings.txt` file to view. The user agent is the user's email so that Toggl can contact them if there are any issues with the API requests.
4. Paste into Excel
        The app will auto copy the data to your clipboard. You can then paste it in Excel online or in the desktop app.


# Improvements needed
The following are in order of priority:
* None

# Improvements completed
See here for improvements made: https://github.com/jbjbjb1/TogglCon/releases/

# Interested to contribute?
See the API references here and contribure https://github.com/toggl/toggl_api_docs !