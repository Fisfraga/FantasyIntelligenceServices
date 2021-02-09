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
from yfpy_models import Player
from requests.exceptions import HTTPError

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
        print("Extracting season " + str(self.season) + " data from week 1 to", self.current_week, "\n")
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
            object containing the information for the scoreboard

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
            object containing the information for the stats
        """
        team_key = self.league_key + ".t." + str(team_id)
        return self.yahoo_query.query(
            "https://fantasysports.yahooapis.com/fantasy/v2/team/" + str(team_key) + "/stats;type=week;week=" +
            str(chosen_week), ["team"])



class Extract_Players_Season_Data(Extract_Data):
    """Subclass of Extract_Data for extracting the data representing the results for one season's Fantasy League for all players. Used to extract data from the Yahoo Fantasy API.
    This class is initiated by the Extract_NBA_Players_Data.

    Attributes
    ----------
    data_dir_relevant_players : str
        the path pointing to the directory with the file containing the players' ids that will be extracted
    relevant_players_ids : Array
        array with the ids for the players that will have their data extracted
    data_dir_player_teams : str
        a value of 1 or 0 used to differentiate if the week already has data, in order to avoid extracting empty data
    players_info : Array
        array with the descriptive information of the players, name, team, position
    data_dir_extraction_stopping_point : str
        the path pointing to the file with the last extracted season
    starting_point : int
        the season that was copmletelly extracted
    data : dict
        dictionary containing the data extracted for all players
    advanced_data : dict
        dictionaty containing advanced stats from the nba for all players, 2017 onwards only
    


    Methods
    -------
    __init__():
        initializes a Extract_Players_Season_Data object
    update_player_id_database():
        called to update the file with the ids of the players that will be extracted
    extract_players_season_data(season):
        extracts the data for each player for the called season
    convert_to_number(value_string):
        converts a string with a '-' into a '0'
    get_player_stats(player_id, season):
        extracts the season stats for a player
    get_team_roster_player_stats_by_week(team_id, chosen_week="current")
        extracts the player ids for every player in the roster
    """

    def __init__(self, setup):
        """Initializes the Extract_Players_Season_Data object,
        using the informations held by the SetUp object.

        Parameters
        ----------
        setup : SetUp
            the SetUp class object which holds all the necessary information to extract the data

        Returns
        ----------
        None
        """
        super().__init__(setup)
        self.data_dir_relevant_players = self.data_dir + "_relevant_player_ids.txt"
        print("Players extraction created for season", self.season)
        pass

    def update_player_id_database(self):
        """Extracts the player id for every player in a Yahoo Fantasy League season. Saves it as a .json file.
        Is called automatically by the Extract_NBA_Players_Data class.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.relevant_players_ids = []
        self.data_dir_players_teams = self.data_dir + "_players_teams.txt"
        self.players_info = []
        self.data_dir_extraction_stopping_point = self.data_dir + "_ids_last_extracted_season.txt"
        self.starting_point = 2017

        try:
            with open(self.data_dir_relevant_players) as json_file:
                self.relevant_players_ids = json.load(json_file)
        except FileNotFoundError:
            print("The Relevant Players list was not found, creating one now...")
        try:
            with open(self.data_dir_extraction_stopping_point) as json_file:
                self.starting_point = json.load(json_file)
        except FileNotFoundError:
            pass
        
        if int(self.season) > int(self.starting_point):
            print("Updating Extraction and Relevant Players.")
            for week in range(1, self.current_week + 1):
                for team_id in range(1, self.num_teams + 1):
                    team = self.get_team_roster_player_stats_by_week(team_id, week)
                    for player in team:
                        player_id = player["player"].player_id
                        
                        if player_id not in self.relevant_players_ids and player_id not in ['4626', '3708', '4905']:
                            self.relevant_players_ids.append(player_id)
                            self.players_info.append([self.season, player_id, player["player"].editorial_team_abbr, player["player"].display_position])
                            self.extracted_data = self.relevant_players_ids
                            self.save_to_json(self.data_dir_relevant_players)
                            self.extracted_data = self.players_info
                            self.save_to_json(self.data_dir_players_teams)
            self.extracted_data = int(self.season)
            self.save_to_json(self.data_dir_extraction_stopping_point)

            print("Relevant Players updated for", self.season, "season:")
            print(self.relevant_players_ids)

        print("Total players for extraction = ", len(self.relevant_players_ids))
        

    def extract_players_season_data(self, season):
        """Extracts the season stats for all players in the extraction list. 
        Is called automatically by the Extract_NBA_Players_Data class.

        Parameters
        ----------
        season : int
            the season for which the data will be extracted for
        
        Returns
        -------
        None
        """

        data_dir_players_data = self.data_dir + "_players_dict_" + str(season) +".txt"
        data_dir_advanced_players_data = self.data_dir + "_players_dict_advanced_" + str(season) +".txt"

        try:
            with open(self.data_dir_relevant_players) as json_file:
                self.relevant_players_ids = json.load(json_file)
        except FileNotFoundError:
            print("Relevante players list not found, please try again.")
        try:
            with open(data_dir_players_data) as json_file:
                self.data = json.load(json_file)
            with open(data_dir_advanced_players_data) as json_file:
                self.advanced_data = json.load(json_file)
        except FileNotFoundError:
            print("This season has no extraction yet. Creating one now.")
            self.data = {}
            self.advanced_data = {}
        print("Extracting players data for:")
        print("Season:", season)
        print("Extraction ids:", self.relevant_players_ids)
        print("Ids already extracted:", list(self.data.keys()))
        for idd in self.relevant_players_ids:
            if idd not in list(self.data.keys()):
                player_stats = []
                player_object = self.get_player_stats(idd, season)
                
                self.sample_player = player_object
                player_stats.append(season)
                player_stats.append(idd)
                player_stats.append(player_object['name'].full)
                player_stats.append(player_object['editorial_team_full_name'])
                player_stats.append(player_object['editorial_team_abbr'])
                player_stats.append(player_object['display_position'])
                for stat in player_object['player_stats'].stats:
                    player_stats.append(self.convert_to_number(stat['stat'].value))
                self.data[idd]=player_stats
                advanced_stats = player_stats.copy()
                for advanced_stat in player_object['player_advanced_stats']['stats']:
                        advanced_stats.append(self.convert_to_number(advanced_stat['stat'].value))
                self.advanced_data[idd]=advanced_stats
                
                self.extracted_data = self.data
                self.save_to_json(data_dir_players_data)
                
                self.extracted_data = self.advanced_data
                self.save_to_json(data_dir_advanced_players_data)
        print("Done")
        

    def convert_to_number(self, value_string):
        """Converts a stat from a string into a float, and any string with an empty stat '-' into a number, '0.0'

        Parameters
        ----------
        value_string : str
            the string containing the number for a stat

        Returns
        -------
        value_string : float
            float number corresponding to a stat value
        """
        if value_string == '-':
            return 0.0
        else:
            return float(value_string)

    def get_player_stats(self, player_id, season):
        """Retrieves the stats of a specific player by player_key and season.
        
        Parameters
        ---------
        player_id : int
            number with the indentifier for the player having data extacted
        season : int
            number of the season for the extracted data

        Returns
        -------
        Yahoo Fantasy Object
        """
        player_key = self.game_code + ".p." + str(player_id)
        return self.yahoo_query.query(
            "https://fantasysports.yahooapis.com/fantasy/v2/players;player_keys=" +
            str(player_key) + "/stats;type=season;season=" + str(season), ["players", "0", "player"])

    def get_team_roster_player_stats_by_week(self, team_id, chosen_week="current"):
        """Retrieve roster with ALL player info for the season of specific team by team_id and for chosen league.
        
        Parameters
        ----------
        team_id : int
            number with the indentifier for the team having the roster data extacted
        chosen_week : int
            number of the season for the extracted data
        
        Returns
        -------
        roster : YahooFantasyObject
            object containing the information for the team roster data
        """
        team_key = self.league_key + ".t." + str(team_id)
        return self.yahoo_query.query(
            "https://fantasysports.yahooapis.com/fantasy/v2/team/" + str(team_key) +
            "/roster/players/stats;type=week;week=" + str(chosen_week),
            ["team", "roster", "0", "players"])



class Extract_NBA_Players_Data():
    """Class for creating multiple Extract_Players_Season_Data objects.Extracts the player ids 
    for the relevant players. Extracts the data of every season for that players
    Will probably raise the 999 timeout error in the yfpy, because the limit for the the daily limit
    of accesses with the Yahoo API will be exceeded. Change your VPN location to continue extracting data.
    

    Attributes
    ----------
    update_possible : bool
        boolean indicating if the players19 and players18 attributes can be created
    players18 : Extract_Players_Season_Data
        attribute that extracts and saves the relevant players id
    players19 : Extract_Players_Season_Data
        attribute that extracts and saves the relevant players id
    players20 : Extract_Players_Season_Data
        attribute that extracts and saves the data for every player

    Methods
    -------
    __init__():
        initializes a Extract_Players_Season_Data object
    update_player_id_database():
        called to update the file with the ids of the players that will be extracted
    extract_all_seasons_data(season):
        extracts the data for each player for each season
    """

    def __init__(self, setup20, setup19=0, setup18=0):
        """Initializes the Extract_NBA_Players_Data object using the informations held by one or more SetUp object.

        Parameters
        ----------
        setup20 : SetUp
            the SetUp class object that holds the information to extract the data from the 2019 season
        setup19 : SetUp
            the SetUp class object that holds the information to extract the data from the 2019 season
        setup18 : SetUp
            the SetUp class object that holds the information to extract the data from the 2019 season
        Returns
        ----------
        None
        """
        self.update_possible = False
        if setup18 != 0:
            self.update_possible = True
            self.players18 = Extract_Players_Season_Data(setup18)
            self.players19 = Extract_Players_Season_Data(setup19)
        self.players20 = Extract_Players_Season_Data(setup20)
        pass

    def update_player_id_database(self):
        """Extracts the player id for every player in 2020, 2019 and 2018 Yahoo Fantasy Leagues seasons. 
        Saves it as a .json file. Is calls a method in the Extract_Players_Season_Data object.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        if self.update_possible:
            self.players18.update_player_id_database()
            self.players19.update_player_id_database()
        else:
            print("Update is not possible for the seasons of 2019 and 2018, only for 2020")
        self.players20.update_player_id_database()

    def extract_all_seasons_data(self):
        """Extracts the season stats for all players in the extraction list. 
        Is calls a method in the Extract_Players_Season_Data object.

        Parameters
        ----------
                
        Returns
        -------
        None
        """
        for season in range(2012, 2021):
            self.players20.extract_players_season_data(season)
