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
* If you don't have a cross_ref.xlsx to merge with (will still display data as-is in Excel)

# How to run and use it
1. Sign up for Toggl.com
2. Use the web app (in development)

# Improvements needed
* Need to change to be serverless suitable
* Need to read in cross reference information from settings.txt rather than .xlsx

# Improvements completed
* 28/3/24 - (v3.9) Updated togglcon.bat to work. Removed setting not used. Fixed total time not rounding correctly.
* 26/3/24 - (v3.8) group entries of same project by their tag if multiple (previously grouped only as main tag)
* 23/3/24 - (v3.7) error handling if no data was in timesheet
* 22/1/24 - (v3.6) changed method to send data straight to clipboard
* 22/1/24 - (v3.5) error handling created for common errors and added icon file.
* 29/9/23 - removed project/job number ending digit limit of 4
* 26/6/23 - updated to fix 'fast fill' working and gave preview of data, removed 'today' menu option
* 24/6/23 - updated from Pxxx-x... to PROxxx-x... & similar for WIP.
* 24/6/23 - fixed issue of cross_ref.xlsx file always not importing first row
* 13/7/22 - tracking was missing off the auto created settings file causing the program to crash

# Interested to contribute?
See the API references here and contribure https://github.com/toggl/toggl_api_docs !