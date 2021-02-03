"""Extraction Module used to extract the Fantasy League data from the Yahoo Fantasy API.
Use this module to import the Extract_Week_Data class.

Please be sure that the following libraries installed in the python Source folder:
json, datetime, abc
"""

__author__ = "Felipe P A Fraga (fisfraga)"
__email__ = "lipefraga@gmail.com"


import json
import datetime
from abc import ABC, abstractmethod

class Extract_Data(ABC):
    """Abstract class for extraction classes. Used to extract data from the Yahoo Fantasy API.
    Should be initiated using the SetUp object created for the Fantasy League.

    Attributes
    ----------
    league_key : str
        the identifier for the combination of the Yahoo Fantasy league and the sport it belongs to
    yahoo_query : YahooFantasySportsQuery
        a query object used to extract data from the Yahoo Fantasy API
    game_code : str
        the lower-case written name for the sport
    season : str
        the season year for the Fantasy League
    num_teams : int
        the number of teams for the Fantasy League
    current_week : int
        the current week for the Fantasy League
    league_scoring_type : str
        the type of scoring for the Fantasy League
    stat_count : int
        the number of stats extracted for the Fantasy League
    players_per_team : int
        the number of players for the Fantasy League
    teams: dict
        a dictionary with the team_id's as keys team names and manager names as elements
    data_dir : str
        the path pointing to the directory where the data will be saved
    extracted_data : dict
        the attribute containing the extracted data which will be used futher on

    Methods
    -------
    __init__(setup):
        initializes a Extract_Data object
    save_to_json(data_dir):
        saves the extracted data into a json file

    """

    def __init__(self, setup):
        """Initializes the Extract_Data object using the informations held by the SetUp object.

        Parameters
        ----------
        setup : SetUp
            the SetUp class object which holds all the necessary information to extract the data

        Returns
        ----------
        None
        """

        self.league_key = setup.league_key
        self.yahoo_query = setup.yahoo_query
        self.game_code = setup.game_code
        self.season = setup.season
        self.num_teams = setup.num_teams

        self.current_week = int(setup.current_week)
        self.league_scoring_type = setup.league_scoring_type

        self.stat_count = setup.stat_count
        self.players_per_team = setup.players_per_team
        self.teams = setup.teams_dict

        self.data_dir = setup.data_output_dir + "extraction"
        self.extracted_data = {}

    def save_to_json(self, data_dir):
        """Initializes the Extract_Data object using the informations held by the SetUp object.

        Parameters
        ----------
        data_dir : str
            the path to the directory where the extracted data will be saved to

        Returns
        ----------
        None
        """
        with open(data_dir, 'w') as filehandle:
            json.dump(self.extracted_data, filehandle)
        pass


class Extract_Week_Data(Extract_Data):
    """Subclass for extracting the data representing the results for the Fantasy League's weeks. Used to extract data from the Yahoo Fantasy API.
    Automatically tries to extract the data when an object is created.

    Attributes
    ----------
    data_dir_week : str
        the path pointing to the directory where the weekly data will be saved
    week_has_begun : int
        a value of 1 or 0 used to differentiate if the week already has data, in order to avoid extracting empty data

    Methods
    -------
    __init__():
        initializes a Extract_Week_Data object and runs the data extraction
    extract_week_data_headone():
        main method, called during __init__(), extracts all the data categorized by weeks
    get_win_for_week(team, week_results):
        sees if a certain team has won its matchup in the week
    get_league_scoreboard(chosen_week):
        extracts the scoreboard for the week, matchups and results
    get_team_stats_by_week(team_id, chosen_week="current"):
        extracts the stats for each team in a certain week
    """

    def __init__(self, setup):
        """Initializes the Extract_Week_Data object using the informations held by the SetUp object.

        Parameters
        ----------
        setup : SetUp
            the SetUp class object which holds all the necessary information to extract the data

        Returns
        ----------
        None
        """
        super().__init__(setup)
        if self.league_scoring_type == "headone":
            self.extract_week_data_headone()
        else:
            print("League type not supported")
        pass

    def extract_week_data_headone(self):
        """Extracts the raw data for every existing week in a Yahoo Fantasy League. Saves it as a .json file.
        Is called automatically when the Extract_Week_Data object is initialized.

            Parameters
            ----------
            None

            Returns
            -------
            None
        """

        self.data_dir_week = self.data_dir + "_weekly_stats_" + str(self.season) + ".txt"
        weekly_stats = {}
        print("Importing season " + str(self.season) + " data from week 1 to", self.current_week, "\n")
        self.week_has_begun = 1
        if datetime.datetime.today().weekday() == 0:
            self.week_has_begun = 0
        for week in range(1, self.current_week + self.week_has_begun):
            print("Week: ", week, " ... Loading ... ")
            week_results = self.get_league_scoreboard(week)
            weekly_stats[str(week)] = [None]*self.num_teams
            for team in range(1, int(self.num_teams + 1)):
                team_stats = {}
                present_team_stats = self.get_team_stats_by_week(team, week)
                team_stats["Team"] = str(self.teams[str(team)][0])
                team_stats["Manager"] = str(self.teams[str(team)][1])
                for stat_id in range(1, self.stat_count + 1):
                    team_stats[stat_id] = present_team_stats['team_stats']['stats'][stat_id - 1]['stat'].value
                team_stats["GP"] = present_team_stats['team_remaining_games']['total']['completed_games']
                team_stats["Win"] = self.get_win_for_week(team, week_results)
                team_stats["Season"] = int(self.season)
                team_stats["Week"] = int(week)
                weekly_stats[str(week)][int(team-1)] = team_stats
            print("\nLoaded!\n")
        self.extracted_data = weekly_stats
        self.save_to_json(self.data_dir_week)
        print("Weekly stats saved to: ", self.data_dir_week)
        pass

    def get_win_for_week(self, team, week_results):
        """Sees if a team has won its matchup in the week.

        Parameters
        ----------
        team : int
            team identifier number
        week_results : dict
            dictionary with the results for each team in the week

        Returns
        -------
        win : int
            1 if the team's result was a win, 0.5 if it was a draw, 0 if it was a loss
        """
        for matchup in week_results["scoreboard"].matchups:
            if matchup["matchup"].teams[0]["team"].team_id == str(team) or matchup["matchup"].teams[1]["team"].team_id == str(team):
                if matchup["matchup"].is_tied == 1:
                    return 0.5
                elif matchup["matchup"].winner_team_key.split(".")[-1] == str(team):
                    return 1
        return 0

    def get_league_scoreboard(self, chosen_week):
        """extracts the scoreboard containing matchups and results for the week.

        Parameters:
        ----------
        chosen_week : int
            week number

        Returns
        -------
        scoreboard : YahooFantasyObject

        """
        return self.yahoo_query.query(
            "https://fantasysports.yahooapis.com/fantasy/v2/league/" + self.league_key + "/scoreboard;type=week;week=" +
            str(chosen_week), ["league"])

    def get_team_stats_by_week(self, team_id, chosen_week="current"):
        """extracts the stats for a team in a certain week

        Parameters:
        ----------
        team_id : int
            team identifier number
        chosen_week : int
            week number

        Returns
        -------
        stats : YahooFantasyObject
        """
        team_key = self.league_key + ".t." + str(team_id)
        return self.yahoo_query.query(
            "https://fantasysports.yahooapis.com/fantasy/v2/team/" + str(team_key) + "/stats;type=week;week=" +
            str(chosen_week), ["team"])
