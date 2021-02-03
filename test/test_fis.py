__author__ = "Felipe P A Fraga (fisfraga)"
__email__ = "lipefraga@gmail.com"


import os
import warnings
import json
import pandas
import matplotlib

from setup import SetUp
from extraction import Extract_Week_Data
from organizer import Teams_Weekly_Data_Organizer
from visualizer import Visualize_Teams_Season_Data, Visualize_Teams_Week_Data

import logging
log = logging.getLogger(__name__)
def pytest_assertion_pass(item, lineno, orig, expl):
   """
      Prints the log(log file) every time the assert passes
   """
   log.info(str(item) + ' | lineno: ' + str(lineno) + ' | ' + orig + ' | PASS')

# Ignore resource warnings from unittest module
warnings.simplefilter("ignore", ResourceWarning)

# Turn on/off automatic opening of browser window for OAuth
browser_callback = True

# Put private.json (see README.md) in test/ directory
auth_dir = "."

# Example code will output data here
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")

# Example vars using public Yahoo league
game_key = "402"
game_code = "nba"
season = "2020"
league_id = "107914"

# Initiate SetUp object using information for the test league
setup = SetUp(game_key, game_code, season, league_id, show_log=False)


def test_setup_league_name():
    """Test if SetUp class was initiated correctly with the information above.
    Check if league_name is 'NahasaCares'.
    """

    assert setup.league_name == "NahasaCares"


def test_setup_number_teams():
    """Test SetUp class to create a game using the information above.
    Check if number of teams is 8'.
    """

    assert setup.num_teams == 8


def test_setup_league_type():
    """Test SetUp class to create a game using the information above.
    Check if league scoring type is 'headone' and that there are 9 scoring stats.
    """

    assert setup.league_scoring_type == "headone" and len(setup.scoring_stats_list) == 9


# Initiate Extract_Week_Data object using setup object
extraction = Extract_Week_Data(setup)


def test_extraction_player_count():
    """Test if Extract_Week_Data Class is correctly created.
    Check if extraction object has the correct attribute for players_per_team,
    if this attribute was assigned correctly, the other ones must have been too.
    """

    assert extraction.players_per_team == 13

def test_extraction_week_1():
    """Test if Extract_Week_Data Class is created and executed correctly.
    Check if on week 1, team position 0 (first of 8: 0-7) has the value in stat position 9 (Steals) equals to 27,
    a very specific detail which will be True only if the data was extracted correctly
    """
    try:
        with open(extraction.data_dir_week) as json_file:
            raw_data = json.load(json_file)
    except FileNotFoundError:
        print("The extracted raw data was not found, please be sure that the data was extracted correctly")

    assert raw_data['1'][0]['9'] == '27'


# Initiate Teams_Weekly_Data_Organizer object using setup object
weeks_data = Teams_Weekly_Data_Organizer(setup)


def test_organizer_current_week():
    """Test if Teams_Weekly_Data_Organizer Class is correctly created.
    Check if the current_week attribute is assigned the correct value, which must be equal to setup.current_week
    """

    assert weeks_data.current_week == int(setup.current_week)


def test_organizer_data_output():
    """Test if Teams_Weekly_Data_Organizer Class is correctly created and outputs DataFrame objects.
    Check if final_data and score_data attributes are of DataFrame type
    """

    assert type(weeks_data.final_data) == pandas.core.frame.DataFrame and type(weeks_data.score_data) == pandas.core.frame.DataFrame


def test_organizer_week_1():
    """Test if Teams_Weekly_Data_Organizer Class is correctly created and has the correct values.
    Check if the DataFrame for final_data has the correct values, using the same data point as test_extraction_week_1,
    See if the first row of the DataFrame (week 1, first team) for the stat category Steals ('ST') is equal to 27
    """

    assert weeks_data.final_data.loc[0, 'ST'] == 27


# Initiate Visualize_Teams_Week_Data object using setup object
visualizer_weeks = Visualize_Teams_Week_Data(weeks_data)


# Use Visualizer object to Create week table for week 1 (default week)
visualizer_weeks.create_week_table()


def test_visualizer_week_1_table():
    """Test if Visualize_Teams_Week_Data Class is correctly created.
    Check if visualization for table_df is of the correct type, pandas.io.formats.style.Styler
    """

    assert type(visualizer_weeks.display_week_table) == pandas.io.formats.style.Styler


def test_visualizer_week_1_table_correctedness():
    """Test if Visualize_Teams_Week_Data Class is correctly created.
    Check if week_data DataFrame created for the generation of the pandas Styler object has the correct values, using the same data point as test_extraction_week_1,
    See if the first row (index = 0) of the Week 1 week_data is correct for the first team, i.e. the stat category Steals ('ST') is equal to 27
    """

    assert visualizer_weeks.week_table_data.loc[0,'ST'] == 27


# Use Visualizer object to Create week score
visualizer_weeks.create_week_score()


def test_visualizer_week_1_score():
    """Test if Visualize_Teams_Week_Data Class is correctly created.
    Check if visualization for scoredf is of the correct type, pandas.io.formats.style.Styler
    """

    assert type(visualizer_weeks.display_week_score) == pandas.io.formats.style.Styler


def test_visualizer_week_1_score_correctedness():
    """Test if Visualize_Teams_Week_Data Class is correctly created.
    Check if week_data DataFrame created for the generation of the pandas Styler object has the correct values, using the same data point as test_extraction_week_1,
    See if the first row (index = 0) of the Week 1 week_data is correct for the first team, i.e. the score for the stat category Steals ('ST') is equal to 10
    """

    assert visualizer_weeks.week_score_data.loc[0,'ST'] == 2.0


# Initiate Visualize_Teams_Season_Data object using setup object
visualizer_season = Visualize_Teams_Season_Data(weeks_data)


# Use Visualizer object to Create season table
visualizer_season.create_season_table()


def test_visualizer_season_table():
    """Test if Visualize_Teams_Season_Data Class is correctly created.
    Check if visualization for season_table is of the correct type, pandas.io.formats.style.Styler
    """

    assert type(visualizer_season.season_table) == pandas.io.formats.style.Styler


# Use Visualizer object to Create season score
visualizer_season.create_season_score()


def test_visualizer_season_score():
    """Test if Visualize_Teams_Season_Data Class is correctly created.
    Check if visualization for season_score is of the correct type, matplotlib.axes._subplots.AxesSubplot
    """

    assert str(type(visualizer_season.season_score)) == "<class 'matplotlib.axes._subplots.AxesSubplot'>"
