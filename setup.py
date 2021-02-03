"""Setup Module used to retreive and hold all the relevant information used by the other Modules (the setup)
Use this module to import the SetUp class, which is responsible for creating the setup object which will be used to initialize other classes.

Please be sure that the following libraries installed in the python Source folder:
os, unicodedata, csv, logging

Uses the class YahooFantasySportsQuery from the yfpy_query file
"""

__author__ = "Felipe P A Fraga (fisfraga)"
__email__ = "lipefraga@gmail.com"


import os
import unicodedata
import csv
import logging
from yfpy_query import YahooFantasySportsQuery


class SetUp():
    """A class used to extract the necessary information to initialize the other classes.


    Attributes
    ----------
    auth_dir : str
        a string that holds the path to the authentication key for OAuth
    game_id : str
        the number that represents a certain sport in Yahoo Fantasy
    game_code : str
        the lower-case written name for the sport in Yahoo Fantasy
    season : str
        the season year for the Fantasy League
    league_id : str
        number representing the specific Yahoo Fantasy league that will be analysed
    data_output_dir : str
        the path pointing to the directory where the data will be saved
    league_key : str
        the identifier for the combination of the Yahoo Fantasy league and the sport it belongs to
    yahoo_query : YahooFantasySportsQuery
        a query object used to extract data from the Yahoo Fantasy API
    league_info : YahooFantasyObject
        the extracted data for the league information
    league_name : str
        the Yahoo Fantasy league's name
    current_week : int
        the current week for the Fantasy League
    last_week : int
        the last week for the Fantasy League
    num_teams : int
        the number of teams for the Fantasy League
    players_per_team : int
        the number of players for the Fantasy League
    IL_spots : int
        the number of Injury spots in the roster for the Fantasy League
    league_scoring_type : str
        the type of scoring for the Fantasy League
    stat_count : int
        the number of stats extracted for the Fantasy League
    stats_list : Array
        a list of the extracted stats for the Fantasy League
    scoring_stats_list : Array
        the list of the stats which are considered for the Fantasy League's scoring system
    league_teams_raw : YahooFantasyObject
        the extracted data for the league teams information
    teams_dict : dict
        a dictionary with the team_id's as keys team names and manager names as elements
    teams_names : Array
        list of teams names for the Fantasy League
    manager_names
        list of manager names for the Fantasy League
    game_weeks_raw : YahooFantasyObject
        the extracted data for the league weeks information
    weeks : dict
        dictionary with the game weeks as keys and start and end date to each week
    num_weeks : int
        number of weeks for the Fantasy League


    Methods
    -------
    __init__(game_id, game_code, season, league_id, show_log=False)
        initializes a SetUp object
    fill_in_league_dependent_info()
        fills in the information regarding league settings
    get_stat_type(stat_info)
        gets the stat type for a certain stat category
    fill_in_teams_info()
        fills in the information regarding league stats categories
    fill_in_week_info()
        fills in the information regarding league weeks
    """

    def __init__(self, game_id, game_code, season, league_id, show_log=False):
        """Initializes the SetUp object using the necessary informations for the Yahoo Fantasy League that will be analyzed.

        Parameters
        ----------
        game_id : int
            The number identification the Yahoo Fantasy League's sport in Yahoo Fantasy
        game_code : str
            The lower-case written name for the Yahoo Fantasy League's sport in Yahoo Fantasy
        season : int
            The season year for the Yahoo Fantasy League
        league_id : int
            A number representing the specific Yahoo Fantasy league that will be analyzed
        show_log : bool, optional
            A boolean that when True, prints the logging info for the queries to Yahoo Fantasy API

        Returns
        ----------
        None
        """
        # Put private.json (see README.md) in the directory
        self.auth_dir = "."
        self.game_id = str(game_id)
        self.game_code = str(game_code)
        self.season = str(season)
        self.league_id = str(league_id)
        self.data_output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data_Output\\")
        self.league_key = self.game_id + ".l." + self.league_id
        self.yahoo_query = YahooFantasySportsQuery(self.auth_dir, self.league_id, game_id=self.game_id, game_code=self.game_code, offline=False)

        if not show_log:
            logging.getLogger("yfpy_query").setLevel(level=logging.INFO)

        self.fill_in_league_settings_info()
        self.fill_in_team_names_info()
        self.fill_in_weeks_info()

        print("Initializing setup for", self.game_code.capitalize(), "Fantasy game for the League: ", self.league_name)
        print("\nSeason:", self.season)
        print("\nNumber of teams:", self.num_teams)
        print("\nLegue scoring type:", self.league_scoring_type)
        if self.league_scoring_type == "headone":
            print("\nStat categories:")
            for stat in self.scoring_stats_list:
                print("   ", stat[0])
        pass

    def fill_in_league_settings_info(self):
        """Queries the information for the league information and settings. Fills in the relevant attributes.

        Parameters
        -------
        None

        Returns
        -------
        None
        """
        league_info = self.yahoo_query.get_league_info()

        self.league_info = league_info
        self.league_name = league_info.name #unicodedata.normalize("NFD", league_info.name).encode("ascii", "ignore").decode("utf-8")
        self.data_output_dir = self.data_output_dir + self.league_name + "_"
        self.current_week = int(league_info.current_week)
        self.last_week = int(league_info.settings.playoff_start_week) - 1
        if int(self.season) < 2019:
            self.current_week = self.last_week

        self.num_teams = league_info.num_teams
        self.players_per_team = 0
        self.IL_spots = 0
        for i in range(len(league_info.settings.roster_positions)):
            if league_info.settings.roster_positions[i]['roster_position'].position != "IL":
                self.players_per_team += int(league_info.settings.roster_positions[i]['roster_position'].count)
            else:
                self.IL_spots += 1

        self.league_scoring_type = league_info.settings.scoring_type

        if self.league_scoring_type == "headone":
            self.stat_count = len(league_info.settings.stat_categories.stats)
            self.stats_list = []
            self.scoring_stats_list = []
            for i in range(self.stat_count):
                present_stat = ["stat_name", "stat_type"]
                present_stat[0] = league_info.settings.stat_categories.stats[i]['stat'].display_name
                present_stat[1] = self.get_stat_type(league_info.settings.stat_categories.stats[i]['stat'])
                self.stats_list.append(present_stat)
                if present_stat[1] != "fraction":
                    self.scoring_stats_list.append(present_stat)
        else:
            print("League type not supported")

        pass

    def get_stat_type(self, stat_info):
        """Returns the stat category type label for a stat_category object.

        Parameters
        ----------
        stat_info : YahooFantasyObject
            The object containing relevant information about a specific stat category

        Returns
        ----------
        stat_label : str
            The string identifying the stat type for futher manipulations

        """
        if "/" in stat_info.display_name:
            return "fraction"
        elif stat_info.sort_order == '0':
            return "inverse"
        elif "%" in stat_info.display_name:
            return "percentage"
        return "standard"

    def fill_in_team_names_info(self):
        """Queries the information for the league teams. Fills in the relevant attributes.

        Parameters
        ----------
        None

        Returns
        ----------
        None
        """
        league_teams = self.yahoo_query.get_league_teams()
        self.league_teams_raw = league_teams
        self.teams_dict = {}
        for team in league_teams:
            self.teams_dict[team['team'].team_id] = [unicodedata.normalize("NFD", team['team'].name.decode('utf-8')).encode("ascii", "ignore").decode("utf-8"), unicodedata.normalize("NFD", team['team'].managers['manager'].nickname).encode("ascii", "ignore").decode("utf-8"), team['team'].team_logos['team_logo'].url]
        self.teams_names = []
        self.manager_names = []
        for key in self.teams_dict.keys():
            self.teams_names.append(self.teams_dict[key][0])
            self.manager_names.append(self.teams_dict[key][1])
        pass

    def fill_in_weeks_info(self):
        """Queries the information for the league weeks. Fills in the relevant attributes.

        Parameters
        ----------
        None

        Returns
        ----------
        None
        """
        game_weeks = self.yahoo_query.get_game_weeks_by_game_id(self.game_id)
        self.game_weeks_raw = game_weeks

        self.weeks = {}
        self.num_weeks = 0
        for week in game_weeks:
            self.num_weeks = self.num_weeks + 1
            self.weeks[week['game_week'].week] = [week['game_week'].start, week['game_week'].end]
        pass
