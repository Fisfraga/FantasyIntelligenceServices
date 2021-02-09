"""Organizer Module used to organize the extracted data into DataFrames.
Use this module to import the Teams_Weekly_Data_Organizer class.

Please be sure that the following libraries installed in the python Source folder:
json, pandas, abc
"""

__author__ = "Felipe P A Fraga (fisfraga)"
__email__ = "lipefraga@gmail.com"


import json
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from collections import ChainMap


class Data_Organizer(ABC):
    """Abstract class for organizing the extracted data into pandas DataFrames.
    Should be initiated using the SetUp object created for the Fantasy League.

    Attributes
    ----------
    read_data_dir : str
        path to the directory in which the extracted data will be read from
    save_data_dir : str
        path to the directory where the organized data will be saved to
    league_name : str
        the Yahoo Fantasy league's name
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
    stats_list : Array
        a list of the extracted stats for the Fantasy League
    scoring_stats_list: Array
        the list of the stats which are considered for the Fantasy League's scoring system
    stats_drop_list : Array
        a list of stats that are not part of the official scoring
    players_per_team : int
        the number of players for the Fantasy League
    teams_names: Array
        list of teams names for the Fantasy League
    final_data : None
        the attribute that will hold the pandas DataFrame with the organized data
    raw_data : dict
        the attribute that receives the extracted data

    Methods
    -------
    __init__(setup):
        initializes a Data_Organizer object
    read_raw_data_json():
        reads the extracted data from a json file
    check_if_empty_percentages(string):
        sees if a percentage type stat is empty, if it is, replaces -'s with 0's
    save_data():
        saves the organized data into a csv file
    """

    def __init__(self, setup):
        """Initializes the Data_Organizer object using the informations held by the SetUp object.

        Parameters
        ----------
        setup : SetUp
            the SetUp class object which holds all the necessary information to organize the data

        Returns
        ----------
        None
        """

        self.read_data_dir = setup.data_output_dir
        self.save_data_dir = setup.data_output_dir
        self.league_name = setup.league_name
        self.season = setup.season
        self.num_teams = setup.num_teams
        self.current_week = int(setup.current_week)
        self.league_scoring_type = setup.league_scoring_type
        self.stat_count = setup.stat_count
        self.stats_list = setup.stats_list
        self.scoring_stats_list = setup.scoring_stats_list
        self.stats_drop_list = []
        self.players_per_team = setup.players_per_team
        self.teams_names = setup.teams_names
        self.final_data = None
        pass

    def read_raw_data_json(self):
        """Reads the extracted data from a json file into the raw_data attribute

        Parameters
        ----------
        None

        Returns
        ----------
        None
        """
        try:
            with open(self.read_data_dir) as json_file:
                self.raw_data = json.load(json_file)
        except FileNotFoundError:
            print("The extracted raw data was not found, please be sure that the data was extracted correctly")
            return False
        return True

    def check_if_empty_percentages(self, string):
        """Sees if a percentage type stat is empty, if it is, replaces -'s with 0's

        Parameters
        ----------
        string : str
            stat string to be checked

        Returns
        ----------
        string : str
            corrected stat string
        """
        if string == '-':
            return '0'
        elif string == '-/-':
            return '0/0'
        else:
            return string

    def save_data(self):
        """Saves the organized data into a csv file

        Parameters
        ----------
        None

        Returns
        ----------
        None
        """
        self.final_data.to_csv(self.save_data_dir, sep=";")


class Teams_Weekly_Data_Organizer(Data_Organizer):
    """Subclass for extracting the data representing the results for the Fantasy League's weeks. Used to extract data from the Yahoo Fantasy API.
    Automatically tries to extract the data when an object is created.

    Attributes
    ----------
    data_dir_week : str
        the path pointing to the directory where the weekly data will be saved
    week_has_begun : int
        a value of 1 or 0 used to differentiate if the week has started, in order to avoid extracting empty data
    final_data : pandas.core.frame.DataFrame
        the attribute that holds the pandas DataFrame with the organized data
    score_data : pandas.core.frame.DataFrame
        the attribute that holds the pandas DataFrame with the score data

    Methods
    -------
    __init__()
        initializes a Teams_Weekly_Data_Organizer object and organizes the data
    save_score_data():
        saves the score_data attribute into a .csv file
    organize_week_data_headone():
        main method in the class, organizes the raw, extracted data into weekly stats and weekly score
    create_dfs(week_data, week_score):
        creates the DataFrames for week data and week score if they do not exist
    update_dfs(week_data, week_score):
        updates the DataFrames for week data and week score if they do exist
    update_indexes():
        updates the indexes of the week data an week score DataFrames
    organize_this_weeks_data(raw_data):
        called to organize the week data for a specific week's raw data
    initialize_week_data():
        used to create the dictionary that holds the week data
    fill_in_week_data(week_data, raw_data):
        fills in the dictionary with the week data for the week from the raw data
    separate_fraction(stat_name):
        separates a stat name that represents 2 different pieces of information (Made and Attempted) into 2 diferent names
    generate_this_weeks_score(week_data):
        called to organize the week score for a specific week's week data
    initialize_week_score():
        used to create the dictionary that holds the week score
    calculate_total_score(score, result, team):
        fills in the dictionary with the score data for the week from the week data
    calculate_stat_score(stat, team):
        finds the number of wins a team has in a specific stat category
    won_at_this_stat(team, opponent):
        finds if a team has won against the opponent in a specific stat
    calculate_matchup_wins(result, team):
        calculates the total matchup wins for a specific team
    compare_with_opponent(team, opponent):
        for a specific stat, see if the team had a win, tie or loss against an opponent
    """

    def __init__(self, setup):
        """Initializes a Teams_Weekly_Data_Organizer object and organizes the data
        Calls the organize_week_data_headone automatically

        Parameters
        ----------
        setup : SetUp
            the SetUp class object which holds all the necessary information to organize the data

        Returns
        ----------
        None
        """
        super().__init__(setup)
        self.read_data_dir = setup.data_output_dir + "extraction_weekly_stats_" + str(self.season) + ".txt"
        self.save_data_dir = setup.data_output_dir + "data_weekly_stats_" + str(self.season) + ".csv"
        self.save_score_data_dir = setup.data_output_dir + "data_weekly_score_" + str(self.season) + ".csv"
        self.score_data = None
        if self.league_scoring_type == "headone":
            self.organize_week_data_headone()
        else:
            print("League type not supported")
        pass

    def save_score_data(self):
        """Saves the score_data attribute into a .csv file

        Parameters
        ----------
        None

        Returns
        ----------
        None
        """
        self.score_data.to_csv(self.save_score_data_dir, sep=";")

    def organize_week_data_headone(self):
        """Main method in this class, organizes the raw, extracted data into weekly stats and weekly score.
        Automatically called when Teams_Weekly_Data_Organizer object is initialized.
        Saves all the data in pre-determined directories for later use when generating visualizations

        Parameters
        ----------
        None

        Returns
        ----------
        None
        """
        data_present = self.read_raw_data_json()
        if data_present == False:
            print("The data will not be organized, please try again after extracting the data")
        else:
            print("Organizing season " + str(self.season) + " data from week 1 to", self.current_week, "\n")
            first = True
            for week in range(1, len(self.raw_data.keys())+1):
                week_data, week_score = self.organize_this_weeks_data(self.raw_data[str(week)])
                if first is True:
                    first = False
                    self.create_dfs(week_data, week_score)
                else:
                    self.update_dfs(week_data, week_score)

            self.update_indexes()
            self.save_data()
            self.save_score_data()
            print("Data Organized for" + str(self.league_name) + "!\n")
            print("Organized data saved to: ", self.save_data_dir)



    def create_dfs(self, week_data, week_score):
        """Creates the DataFrames for week data and week score if they do not exist

        Parameters
        ----------
        week_data : dict
            the organized week data for the first week
        week_score : dict
            the organized week score for the first week

        Returns
        ----------
        None
        """
        self.final_data = pd.DataFrame.from_dict(week_data)
        self.score_data = pd.DataFrame.from_dict(week_score) 

    def update_dfs(self, week_data, week_score):
        """Updates the DataFrames for week data and week score if they do exist

        Parameters
        ----------
        week_data : dict
            the organized week data for an intermediary week
        week_score : dict
            the organized week score for an intermediary week

        Returns
        ----------
        None
        """
        temp_df = pd.DataFrame.from_dict(week_data)
        copy_all_data = self.final_data.copy()
        self.final_data = pd.concat([copy_all_data, temp_df])
        temp_score = pd.DataFrame.from_dict(week_score)
        copy_all_score = self.score_data.copy()
        self.score_data = pd.concat([copy_all_score, temp_score])

    def update_indexes(self):
        """Updates the indexes of the week data an week score DataFrames

        Parameters
        ----------
        None

        Returns
        ----------
        None
        """
        self.final_data.reset_index(inplace=True)
        self.final_data.rename(columns={"index": "Team_id"}, inplace = True)
        self.final_data['Team_id'] = self.final_data['Team_id'].add(1)

        self.score_data.reset_index(inplace=True)
        self.score_data.rename(columns={"index": "Team_id"}, inplace = True)
        self.score_data['Team_id'] = self.score_data['Team_id'].add(1)

    def organize_this_weeks_data(self, raw_data):
        """Central method that is called to organize the raw data into structured data for a specific week's raw data

        Parameters
        ----------
        raw_data : dict
            the entire unstructured data for only one week

        Returns
        ----------
        week_data : dict
            the organized week data
        week_score : dict
            the organized week score
        """
        week_data = self.initialize_week_data()
        week_data = self.fill_in_week_data(week_data, raw_data)
        week_score = self.generate_this_weeks_score(week_data)
        week_data["Score"] = week_score["Score"]
        week_data["Matchup_Wins"] = week_score["Matchup_Wins"]
        week_data["Week_Result"] = week_score["Week_Result"]

        return week_data, week_score

    def initialize_week_data(self):
        """Used to create the dictionary that holds the week data

        Parameters
        ----------
        None

        Returns
        ----------
        week_data : dict
            empty dictionary which will be filled in by fill_in_week_data():
        """
        week_data = {}
        week_data["Year"] = []
        week_data["Week"] = []
        week_data["Team"] = []
        week_data["Manager"] = []
        for stat in self.stats_list:
            if stat[1] == "fraction":
                numerator, denominator = self.separate_fraction(stat[0])
                week_data[numerator] = []
                week_data[denominator] = []
                self.stats_drop_list.append(numerator)
                self.stats_drop_list.append(denominator)
            else:
                week_data[stat[0]] = []
        week_data["GP"] = []
        week_data["Win"] = []
        return week_data

    def fill_in_week_data(self, week_data, raw_data):
        """Used to fill in the dictionary that holds the week data

        Parameters
        ----------
        week_data : dict
            empty dictionary created by initialize_week_data():
        raw_data : dict
            the entire unstructured data for only one week

        Returns
        ----------
        week_data : dict
            dictionary with the week's data for each team
        """
        for team_data in raw_data:
            week_data["Year"].append(team_data["Season"])
            week_data["Week"].append(team_data["Week"])
            week_data["Team"].append(team_data["Team"])
            week_data["Manager"].append(team_data["Manager"])
            for i in range(self.stat_count):
                stat_value = team_data[str(i+1)]
                if self.stats_list[i][1] == "fraction":
                    numerator, denominator = self.separate_fraction(self.stats_list[i][0])
                    stat_num, stat_den = self.check_if_empty_percentages(stat_value.split('/'))
                    week_data[numerator].append(int(stat_num))
                    week_data[denominator].append(int(stat_den))
                elif self.stats_list[i][1] == "percentage":
                    week_data[self.stats_list[i][0]].append(float(stat_value))
                elif self.stats_list[i][1] == "inverse":
                    week_data[self.stats_list[i][0]].append(-1*int(stat_value))
                else:
                    week_data[self.stats_list[i][0]].append(int(stat_value))
            week_data["GP"].append(int(team_data["GP"]))
            week_data["Win"].append(team_data["Win"])
        return week_data

    def separate_fraction(self, stat_name):
        """Mehod that separates a stat name that has a '/' which denotes a fraction,
        which will be divided into 2 entries, one for numerator, one for the denominator.

        Parameters
        ----------
        stat_name : str
            stat name for a fraction that will be divided into 'made' and 'attempted'

        Returns
        ----------
        numerator : str
            stat name for 'made something'
        denominator : str
            stat name for 'attempts of something'
        """
        return stat_name.split("/")[0], stat_name.split("/")[0][0:-len(stat_name.split("/")[1])] + stat_name.split("/")[1]

    def generate_this_weeks_score(self, week_data):
        """Organizes the week score for a specific week's week data

        Parameters
        ----------
        week_data : dict
            dictionary with the week's data for each team
        Returns
        ----------
        score : dict
            dictionary with the week's score for each team
        """
        score = self.initialize_week_score()
        for team_id in range(self.num_teams):
            score = self.calculate_total_score(score, week_data, team_id)

        return score

    def initialize_week_score(self):
        """Used to create the dictionary that holds the week score

        Parameters
        ----------
        None

        Returns
        ----------
        score : dict
            empty dictionary which will be filled in by calculate_total_score():
        """
        score = {}
        score["Year"] = []
        score["Week"] = []
        score["Team"] = []
        score["Manager"] = []
        for stat in self.scoring_stats_list:
            score[stat[0]] = []
        score["Score"] = []
        score["Matchup_Wins"] = []
        score["Week_Result"] = []
        return score

    def calculate_total_score(self, score, week_data, team):
        """Used to fill in the dictionary that holds the week data

        Parameters
        ----------
        score : dict
            empty dictionary created by initialize_week_score():
        week_data : dict
            the entire unstructured data for only one week
        team : int
            team identifier to access data

        Returns
        ----------
        score : dict
            dictionary with the week's score for each team
        """
        score["Year"].append(week_data["Year"][team])
        score["Week"].append(week_data["Week"][team])
        score["Team"].append(week_data["Team"][team])
        score["Manager"].append(week_data["Manager"][team])
        total_score = 0
        for stat_name_and_type in self.scoring_stats_list:
            stat_score = self.calculate_stat_score(week_data[stat_name_and_type[0]], team)
            score[stat_name_and_type[0]].append(stat_score)
            total_score += stat_score
        score["Score"].append(round(total_score, 1))
        score["Matchup_Wins"].append(round(self.calculate_matchup_wins(week_data, team), 1))
        score["Week_Result"].append(week_data["Win"][team])
        return score

    def calculate_stat_score(self, stat, team):
        """Finds the number of wins a team has in a specific stat category

        Parameters
        ----------
        stat : dict
            the values of a specific stat for all teams
        team : int
            team identifier to access data

        Returns
        ----------
        teams_defeated : int
            the teams defeated (the score) for this team in this stat
        """
        teams_defeated = 0
        for i in range(len(stat)):
            if i != team:
                teams_defeated += self.won_at_this_stat(stat[team], stat[i])
        return teams_defeated

    def won_at_this_stat(self, team, opponent):
        """Finds if a team has won against the opponent in a specific stat

        Parameters
        ----------
        team : float
            the stat value for the team having the score calculated
        opponent : float
            the stat value for the opponent

        Returns
        ----------
        points : float
            the score for the team against the opponent
        """
        if team > opponent:
            return 1
        elif team == opponent:
            return 0.5
        else:
            return 0

    def calculate_matchup_wins(self, week_data, team):
        """Calculates the total matchup wins for a specific team

        Parameters
        ----------
        week_data : dict
            dictionary with the week's data for each team
        team : int
            team identifier to access data

        Returns
        ----------
        wins : float
            the number of matchups a team would win this week
        """
        wins = 0
        for i in range(self.num_teams):
            if i != team:
                advantage = 0
                for stat_name_and_type in self.scoring_stats_list:
                    stat = week_data[stat_name_and_type[0]]
                    advantage += self.compare_with_opponent(stat[team], stat[i])
                if advantage > 0:
                    wins += 1
                elif advantage == 0:
                    wins += 0.5

        return wins

    def compare_with_opponent(self, team, opponent):
        """For a specific stat, see if the team had a win, tie or loss against an opponent

        Parameters
        ----------
        team : float
            the stat value for the team having the score calculated
        opponent : float
            the stat value for the opponent

        Returns
        ----------
        result : int
            returns the margin of vitory for this stat, 1 for win, 0.5 for draw, -1 for loss
        """
        if team > opponent:
            return 1
        elif team == opponent:
            return 0
        else:
            return -1



class Players_Data_Organizer(Data_Organizer):
    """Subclass for extracting the data representing the results for the Fantasy League's players. Used to extract data from the Yahoo Fantasy API.
    Automatically tries to extract the data when an object is created.

    Attributes
    ----------
    active_players_list : Array
        array with the ids for the players that will have their data extracted
    X_columns : Array
        the columns that are important for the pre_processing of the data
    X_columns_advanced : Array
        the columns that are important for the pre_processing of the data considering advanced stats
    stats_to_take_average : Array
        list of stats that are dependent on the number of games
    num_stats : int
        number of stats extracted for each player
    stats_to_take_average_advanced : Array
        list of stats that are dependent on the number of games, considering advanced stats
    num_stats_advanced : int
        number of stats extracted for each player, considering advanced stats
    player_info : dict
        dictionary with the descriptive information of the players, name, team, position
    points_breakdown : dict
        dictionary with the points made by each stat category for each player
    avg_dfs : dict
        dictionary with pandas DataFrames containing the average stats for each player in the season
    X_dfs : dict
        dictionary with pandas DataFrames containing the stats that will input the model
    y_dfs : dict
        dictionary with pandas DataFrames containing the points made by each player in a season
    avg_dfs_advanced : dict
        dictionary with pandas DataFrames containing the average stats for each player in the season
    X_dfs_advanced : dict
        dictionary with pandas DataFrames containing the stats that will input the model, considering advanced stats


    Methods
    -------
    __init__()
        initializes a Players_Data_Organizer object and organizes the data
    read_raw_data_json(data_dir):
        reads any .json file and returns the raw_data
    organize_player_data():
        main method in the class, organizes the raw, extracted data into the season data for each player
    create_average_stats(raw_dict, stats_to_take_average):
        receives the raw data and returns the average data for each player in the dict
    pre_process_data(avg_dfs, X_columns):
        filters the average data for the chosen columns for the model to predict the rankings next season
    calculate_points(avg_stats_df):
        using the average stats for the season, calculates the points used to rank the players, for each player
    """

    def __init__(self, setup, pre_process_stats=0):
        """initializes a Players_Data_Organizer object and organizes the data

        Parameters
        ----------
        setup : SetUp
            the SetUp class object which holds all the necessary information to organize the data
        pre_process_stats : Array
            the list of columns that will be used for pre-processing the data
        """
        super().__init__(setup)
        self.read_data_dir = setup.data_output_dir + "extraction_"
        self.save_data_dir = setup.data_output_dir + "data_league_teams_past_stats_week_" + str(self.current_week) + ".csv"
        self.active_players_list = self.read_raw_data_json(self.read_data_dir + "relevant_player_ids.txt")
        self.active_players_list = list(set(self.active_players_list))
        self.organize_player_data(pre_process_stats)
        

    def read_raw_data_json(self, data_dir):
        """Reads the data present in a json file and returns the raw_data

        Parameters
        ----------
        data_dir : str
            directory to the .json file that will be read

        Returns
        ----------
        raw_data : dict
            the data read from the .json file
        """
        try:
            with open(data_dir) as json_file:
                raw_data = json.load(json_file)
        except FileNotFoundError:
            print("The extracted raw data was not found, please be sure that the data was extracted correctly")
            return 0
        else:
            return raw_data

    def organize_player_data(self, pre_process_stats):
        """Main method in the class, organizes the raw, extracted data into the season data for each player.
        Automatically called when Players_Data_Organizer object is initialized.
        Saves all the data in pre-determined directories for later use when generating visualizations

        Parameters
        ----------
        pre_process_stats : Array
            list of the stats that will be considered to run the predictive model for player stats

        Returns
        ----------
        None
        """
        if pre_process_stats == 0:
            self.X_columns = [6, 8, 9, 11, 12, 14, 16, 18, 21, 22, 23, 24, 25, 26, 27, 32, 33]
        else:
            self.X_columns = pre_process_stats
        
        self.X_columns_advanced = self.X_columns.copy()
        self.X_columns_advanced.extend([34, 35, 38, 41, 42, 44, 45, 49, 50])

        self.stats_to_take_average = [8, 9, 10, 12, 13, 15, 16, 18, 19, 20, 21, 22, 23, 24, 25, 27]
        self.num_stats = 34

        self.stats_to_take_average_advanced = [8, 9, 10, 12, 13, 15, 16, 18, 19, 20, 21, 22, 23, 24, 25, 27, 34, 35, 42, 43]
        self.num_stats_advanced = 51

        self.player_info = {}
        self.points_breakdown = {}

        self.avg_dfs = {}
        self.X_dfs = {}
        self.y_dfs = {}

        self.avg_dfs_advanced = {}
        self.X_dfs_advanced = {}
        

        for season in range(2012, 2021):
            self.season = season
            self.points_breakdown[season] = {}
            read_data_dict = self.read_data_dir + "players_dict_" + str(season) + ".txt"
            data = self.read_raw_data_json(read_data_dict)
            
            for player_id in self.active_players_list:
                if player_id not in list(data.keys()):
                    data[player_id] = [0]*self.num_stats
            avg = self.create_average_stats(data, self.stats_to_take_average)
            self.avg_dfs[season] = pd.DataFrame.from_dict(avg, orient='index')
            self.X_dfs[season] = self.pre_process_data(self.avg_dfs[season], self.X_columns)
            self.y_dfs[season] = pd.DataFrame.from_dict(self.calculate_points(self.avg_dfs[season]), orient='index') 
            
            if season > 2016:
                read_advanced_data_dict = self.read_data_dir + "players_dict_advanced_" + str(season) + ".txt"
                advanced_data = self.read_raw_data_json(read_advanced_data_dict)

                for player_id in self.active_players_list:
                    if player_id not in list(advanced_data.keys()):
                        advanced_data[player_id] = [0]*self.num_stats_advanced
                advanced_avg = self.create_average_stats(advanced_data, self.stats_to_take_average_advanced)
                self.avg_dfs_advanced[season] = pd.DataFrame.from_dict(advanced_avg, orient='index')
                self.X_dfs_advanced[season] = self.pre_process_data(self.avg_dfs_advanced[season], self.X_columns_advanced)

    def create_average_stats(self, raw_dict, stats_to_take_average):
        """Receives the raw data and returns the average data for each player in the dict

        Parameters
        ----------
        raw_dict : dict
            dict with the raw data for every player
        stats_to_take_average
            list with the stats that are dependent on the number of games
        
        Returns
        --------
        data : dict
            average_data for each player
        """
        data = raw_dict.copy()
        for key in list(raw_dict.keys()):
            for stat_position in stats_to_take_average:
                if data[key][6] > 0:
                    data[key][stat_position] = float(data[key][stat_position])/float((data[key][6]))
        
        return data


    def pre_process_data(self, avg_df, X_columns):
        """filters the average data for the chosen columns for the model to predict the rankings next season

        Parameters
        ----------
        avg_dif : pandas.core.frame.DataFrame
            DataFrame with all the stats for each player
        X_columns : Array
            list with the columns that are important for the pre_processing of the data
        
        Returns
        -------
        X_df : pandas.core.frame.DataFrame
            DataFrame containing only the selected columns
        """
        return avg_df[X_columns].copy()


    def calculate_points(self, avg_stats_df):
        """

        Parameters
        ----------
        avg_stats_df : pandas.core.frame.DataFrame
            DataFrame with the stats for each player

        Returns
        --------
        points_dict : dict
            dictionary with the points for each player for the season
        """
        multiplier = {'FG%' : [8, 9], 'FT%' : [15, 10], '3PTM' : 6, 'PTS' : 0.8, \
        'REB' : 1.8, 'AST' : 3, 'ST' : 13, 'BLK' : 9, 'TO' : -4}
        points_dict = {}
        player_info = {}

        for index, row in avg_stats_df.iterrows():
            player_stats = row
            player_id = index
            points = 0
            points_list = [self.season, player_stats[2]]
            #FG%
            if player_stats[11] > 0.46:
                pos = 0
            else:
                pos = 1
            if player_stats[9] > 0:
                points_list.append((player_stats[10]/player_stats[9] - 0.46) * player_stats[9] * multiplier['FG%'][pos])
            else:
                points_list.append(0)
            #FT%
            if player_stats[14] > 0.78:
                pos = 0
            else:
                pos = 1
            if player_stats[12] > 0:
                points_list.append((player_stats[13]/player_stats[12] - 0.78) * player_stats[12] * multiplier['FT%'][pos])
            else:
                points_list.append(0)
            #3PTM
            points_list.append(player_stats[16] * multiplier['3PTM'])
            #PTS
            points_list.append(player_stats[18] * multiplier['PTS'])
            #REB
            points_list.append(player_stats[21] * multiplier['REB'])
            #AST
            points_list.append(player_stats[22] * multiplier['AST'])
            #ST
            points_list.append(player_stats[23] * multiplier['ST'])
            #BLK
            points_list.append(player_stats[24] * multiplier['BLK'])
            #TO
            points_list.append(player_stats[25] * multiplier['TO'])
            #Total
            points_list.append(sum(points_list[2:11]))
            points_dict[player_id] = points_list[11]
            self.points_breakdown[self.season][player_id] = points_list
            player_info[player_id] = [player_stats[2], player_stats[5], player_stats[4]]
        
        self.player_info[self.season] = player_info

        return points_dict
