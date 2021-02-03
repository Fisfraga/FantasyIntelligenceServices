# FantasyIntelligenceServices
Framework for acessing fantasy basketball data


README for Fantasy Intelligence Services
-----------------------------------------------

This is a Framework for accessing Fantasy Leagues with scoring type head-to-head-one-win.

The program can be adapted to various types of Leagues and for different types of information.

The program can be:

    used through the jupyter notebook (00_FantasyIntelligenceServices.ipynb) file
    used as a library
    extended as a Framework



Setup for using the program with your own league
-----------------------------------------------


Log in to a Yahoo account with access to whatever fantasy leagues from which you wish to retrieve data.
Go to https://developer.yahoo.com/apps/create/ and create an app (you must be logged into your Yahoo account as stated above). For the app, select the following options:
Application Name (Required): FIS (you can name your app whatever you want, this is just an example).
Description (Optional): you may write a short description of what the app does.
Home Page URL (Optional): if you have a web address related to your app you may add it here.
Redirect URI(s) (Required): this field must contain a valid redirect address, so you can use https://localhost:8080
API Permissions (Required): check the Fantasy Sports checkbox. You can leave the Read option selected (appears in an accordion expansion underneath the Fantasy Sports checkbox once you select it).

Click the Create App button.
Once the app is created, it should redirect you to a page for your app, which will show both a Client ID and a Client Secret.
Make a copy of examples/EXAMPLE-private.json, rename it to just private.json, and copy the Client ID and Client Secret values to their respective fields (make sure the strings are wrapped regular quotes (""), NOT formatted quotes (“”)). The path to this file will be needed to point FIS to your credentials.
Now you should be ready to initialize the OAuth2 connection between FIS and your Yahoo account.


PLEASE NOTE: Assuming you followed the setup instructions correctly, the first time you use FIS, a browser window will open up asking you to allow your app to access your Yahoo fantasy sports data. You MUST hit allow, and then copy the verification code that pops up into the command line prompt where it will now be asking for verification, hit enter, and the OAuth2 three-legged handshake should be complete and your data should have been successfully retrieved.

FIS should have now generated a token.json for you in the same directory where you stored your private.json credentials, and for all subsequent runs of your app, you should be able to keep retrieving Yahoo fantasy sports data using FIS without re-verifying, since the generated refresh token should now just renew whenever you use the same token.json file to authenticate your app.



Setup just to test the program
-----------------------------------------------

No action is required.
Use the private.json file that is already in the directory.



Pre-requisites for using Fantasy Intelligence Services
-----------------------------------------------

Python 3.7.4 or more recent


The following libraries are used as a part of FIS:

json
abc
os
csv
logging
abc
datetime
importlib
requests
sys
requests.exceptions
unicodedata
ipython
bokeh
time
yahoo_oauth
pandas
numpy
seaborn
jinja2
openpyxl

The necessary installations to use the program are:

pip install numpy
pip install yahoo-oauth
pip install pandas
pip install jinja2
pip install seaborn
pip install openpyxl
pip install matplotlib
pip install ipython
pip install bokeh
pip install dataframe_image




Program execution and data output
-----------------------------------------------------------

The suggested usage for this program is through the jupyter notebook (00_FantasyIntelligenceServices.ipynb) file

There you can go through the step by step process needed to setup, extract, organize and visualize the data.


To initialize a SetUp class object, there are 4 key inputs:

self.game_id --> 402				#The id for the 2020/2021 NBA season
self.game_code --> nba				#NBA in lower case
self.season --> 2020				#Present year (league started in 2020)
self.league_id --> 107914			#A public league code, can be accessed without a yahoo account

The league_id can be found by opening the league page in any browser, and copying the number that appears after the game_code:

https://basketball.fantasysports.yahoo.com/nba/107914   <---------- THIS NUMBER


To initialize a Data_Extraction class object, use the SetUp class object.

To initialize a Data_Organization class object, use the SetUp class object.

To initialize a Data_Visualization class object, use the Data_Organization class object.


The output for the Fantasy Intelligence Services are saved on the directory you clone it to, in the Visualizations_Output folder.
