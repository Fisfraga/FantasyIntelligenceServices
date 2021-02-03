"""Visualizer Module used to create visualiations from the organized data.
Use this module to import the Visualize_Teams_Season_Data and Visualize_Teams_Week_Data classes.

Please be sure that the following libraries installed in the python Source folder:
abc, pandas, numpy, os, matplotlib, seaborn, dataframe_image, IPython, bokeh
"""

__author__ = "Felipe P A Fraga (fisfraga)"
__email__ = "lipefraga@gmail.com"

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
import os
import seaborn as sns
import dataframe_image as dfi
from IPython.display import display
from bokeh.io import show, save
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.transform import dodge


class Data_Visualization(ABC):
    """
    Abstract class for the visualization of the organized data.
    Should be initiated using an Data_Organizer object

     Attributes
    ----------
    data : pandas.core.frame.DataFrame
        the DataFrame containing the organized data for the Yahoo Fantasy League's results
    teams_names : Array
        list of teams names for the Fantasy League
    stats_list : Array
        a list of the extracted stats for the Fantasy League
    scoring_stats_list : Array
        the list of the stats which are considered for the Fantasy League
    valid_input : bool
        variable to indicate the presence of organized data
    visualization_option : Array
        list with the possible visualizations for the Data_Visualization object
    active_option: int
        integer indicating the active visualization selected
    save_dir : str
        path to the directory where the visualizations will be saved to

    Methods:
    ----------
    __init__():
        initializes a Data_Visualization object and checks if the Data_Organizer object used to initialize it contains the data
    save_visualization():
        abstract method that saves the active visualization to the save_dir
    generate_all_visualizations():
        abstract method that will generates all the non-team-specific visualizations for the Data_Visualization object
    """

    def __init__(self, organized_data):
        """Initializes a Data_Visualization object and checks if the Data_Organizer object used to initialize it contains the data

        Parameters
        ----------
        organized_data : Data_Organizer
            the data used to create the visualizations

        Returns
        ----------
        None
        """
        try:
            self.data = organized_data.final_data.copy()
            self.teams_names = organized_data.teams_names
            self.stats_list = organized_data.stats_list
            self.scoring_stats_list = organized_data.scoring_stats_list
            self.stats_drop_list = organized_data.stats_drop_list
        except AttributeError:
            print("Input not recognised, please be sure to initialize this Class with an OrganizedData object")
            self.valid_input = False
        else:
            self.visualization_options = []
            self.active_option = 0
            self.save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Visualizations_Output\\", organized_data.league_name)
            self.valid_input = True
            print("This class supports the following functionalities:")
    
    @abstractmethod
    def save_visualization(self):
        """Abstract method that saves the active visualization to the save_dir

        Parameters
        ----------
        None

        Returns
        ----------
        None
        """
        pass
    
    @abstractmethod
    def generate_all_visualizations(self):
        """Abstract method that will generates all the non-team-specific visualizations for the Data_Visualization object

        Parameters
        ----------
        None

        Returns
        ----------
        None
        """
        pass


class Visualize_Teams_Season_Data(Data_Visualization):
    """
    Subclass for the visualization of the organized data.
    Should be initiated using an Teams_Weekly_Data_Organizer object

    Attributes
    ----------
    score_data : DataFrame
        the DataFrame containing the organized data for the Yahoo Fantasy League's score
    week : int
        the active week for generating visualizations
    season_table : pandas.io.formats.style.Styler
        styled panadas DataFrame containing the Season_Table visualization
    season_score : matplotlib.axes._subplots.AxesSubplot
        plot that contains the Season_Cumulative_Score visualization

    Methods
    ----------
    __init__(self, data):
        initializes a Visualize_Teams_Season_Data object and checks if the Teams_Weekly_Data_Organizer object used to initialize it contains the data
    save_visualization(self):
        saves the active visualization into its save directory
    generate_all_visualizations():
        generates all the non-team-specific visualizations visualizations for the Data_Visualization object
    create_season_table():
        generates the Season Table visualization
    create_season_score():
        genetates the Season Cumulative Score visualization
    """

    def __init__(self, data):
        """Initializes a Visualize_Teams_Season_Data object and
        checks if the Teams_Weekly_Data_Organizer object used to initialize it contains the data

        Parameters
        ----------
        data : Teams_Weekly_Data_Organizer
            the Teams_Weekly_Data_Organizer object used to create the visualizations

        Returns
        ----------
        None
        """
        super().__init__(data)
        if self.valid_input is False:
            print("Visualizer was not created")
        else:
            self.score_data = data.score_data.copy()
            self.week = data.current_week
            self.visualization_options = ["Season Table", "Season Cumulative Score"]
            print("1. Create and save all the visualizations below at once: use .generate_all_visualizations()")
            print("2. Create and save the Season Table visualization: use .create_season_table()")
            print("3. Create and save the Season Cumulative Score visualization: use .create_season_score()")


    def save_visualization(self):
        """Saves the active visualization into its save directory

        Parameters
        ----------
        None

        Returns
        ----------
        None
        """
        if self.active_option == 1:
            save_dir = self.save_dir + "_season_table.png"
            dfi.export(self.season_table, save_dir)
        elif self.active_option == 2:
            save_dir = self.save_dir + "_season_cumulative_score.png"
            fig = self.season_score.get_figure()
            fig.savefig(save_dir)

    def generate_all_visualizations(self):
        """Generates the Season Table and the Season Cumulative Score visualizations

        Parameters
        ----------
        None

        Returns
        ----------
        None
        """
        self.create_season_table()
        self.create_season_score()
        pass


    def create_season_table(self):
        """Generates the Season Table visualization

        Parameters
        ----------
        None

        Returns
        ----------
        None
        """
        print("Creating visualization... Season Table is being processed")
        self.active_option = 1
        self.season_table = pd.pivot_table(self.data.drop(columns=['Team_id', 'Week', 'Week_Result', 'Year']), index=['Team'], aggfunc=np.sum)
        season_table_filter = []
        for stat in self.scoring_stats_list:
            season_table_filter.append(stat[0])
        season_table_filter.extend(['GP', 'Score', 'Matchup_Wins', 'Win'])
        formatting_dict = {"Win": "{:.1f}", "Score": "{:.1f}", "Matchup_Wins": "{:.1f}"}
        for stat in self.scoring_stats_list:
            if stat[1] == "percentage":
                numerator = stat[0].split("%")[0] + "M"
                denominator = stat[0].split("%")[0] + "A"
                self.season_table[stat[0]] = self.season_table[numerator].div(self.season_table[denominator])
                formatting_dict[stat[0]] = "{:.3f}"
        self.season_table = self.season_table[season_table_filter]
        self.season_table.sort_values(by=['Matchup_Wins'], ascending=False, inplace=True)
        self.season_table = self.season_table.style.format(formatting_dict).background_gradient(cmap='RdBu', axis=0)
        self.save_visualization()
        display(self.season_table)

    def create_season_score(self):
        """Generates the Season Cumulative Score visualization
        Parameters
        ----------
        None

        Returns
        ----------
        None
        """
        print("Creating visualization... Season Cumulative Score is being processed")
        self.active_option = 2
        color = sns.color_palette("Paired", 12)
        scores = self.data.pivot(index="Week", columns="Team", values="Score")
        self.season_score = scores.cumsum().plot.line(color=color, figsize=[18, 15])
        self.save_visualization()
        display(self.season_score)


class Visualize_Teams_Week_Data(Data_Visualization):
    """
    Subclass for the visualization of the organized data.
    Should be initiated using an Teams_Weekly_Data_Organizer object

    Attributes
    ----------
    week : int
        the active week for generating visualizations
    last_week : int
        the last week available for visualizations
    score_data : pandas.core.frame.DataFrame
        the DataFrame containing the organized data for the Yahoo Fantasy League's score
    week_table_data : pandas.core.frame.DataFrame
        present week's data as a pandas DataFrame object
    display_week_table : pandas.io.formats.style.Styler
        formatted present week's data as a pandas Styler object
    week_score_data : pandas.core.frame.DataFrame
        the present week's score as a pandas DataFrame object
    display_week_score : pandas.io.formats.style.Styler
        formatted present week's score as a pandas Styler object

    Methods
    ----------
    __init__(self, data):
        initializes a Visualize_Teams_Week_Data object and checks if the Teams_Weekly_Data_Organizer object used to initialize it contains the data
    save_visualization(self):
        saves the active visualization into its save directory
    generate_all_visualizations():
        generates all the non-team-specific visualizations visualizations for the Data_Visualization object
    create_visualization():
        generates a new visualization with user input
    print_last_week_visualizations():
        generates all the existing visualizations for the most recent copmleted week, including stat comparisons for a specific team
    change_week(new_week):
        changes the active week to the desired week
    create_week_table():
        generates the Week Table visualization
    create_week_score():
        genetates the Week Score visualization
    create_stats_comparison(team_id, opp_id):
        genetates the Stat Comparison visualization for a specific matchup (primary team and opponent)
    separate_fraction(stat_name):
        separates a stat name that represents 2 different pieces of information (Made and Attempted) into 2 diferent names
    """

    def __init__(self, data):
        """Initializes a Visualize_Teams_Week_Data object and checks if 
        the Teams_Weekly_Data_Organizer object used to initialize it contains the data

        Parameters
        ----------
        data : Teams_Weekly_Data_Organizer
            the Teams_Weekly_Data_Organizer object used to create the visualizations

        Returns
        ----------
        None
        """
        super().__init__(data)
        if self.valid_input is False:
            print("Visualizer was not created")
        else:
            self.week = 1
            self.last_week = data.current_week
            self.score_data = data.score_data.copy()
            self.visualization_options = ["Week Table", "Week Score", "Stat Comparison"]
            print("1. Create and save all non-team-specific visualizations at once: use .generate_all_visualizations()")
            print("2. Create and print one visualization at a time: use .create_visualization()")
            print("3. Create and print the visualization for the last week: use .generate_last_week_visualizations()")

    def save_visualization(self):
        """Saves the active visualization into its save directory

        Parameters
        ----------
        None

        Returns
        ----------
        None
        """
        if self.active_option == 1:
            save_dir = self.save_dir + "_week_" + str(self.week) + "_table.png"
            dfi.export(self.display_week_table, save_dir)
        elif self.active_option == 2:
            save_dir = self.save_dir + "_week_" + str(self.week) + "_score.png"
            dfi.export(self.display_week_score, save_dir)
        pass

    def generate_all_visualizations(self):
        """Generates the Week Table and the Week Score visualizations for every week

        Parameters
        ----------
        None

        Returns
        ----------
        None
        """
        for week in range(1, self.last_week + 1):
            self.week = week
            self.create_week_table()
            self.create_week_score()

    def generate_last_week_visualizations(self):
        """Generates the Week Table and the Week Score visualizations for the last week,
        as well as the Stat Comparison visualization for a chosen team against all other teams.

        Parameters
        ----------
        None

        Returns
        ----------
        None
        """
        self.week = self.last_week - 1
        self.create_week_table()
        self.create_week_score()

        invalid_input = True
        while invalid_input:
            print('Please type the number of the Team you would like to create the Visualizations for the last week:\nSelect a team from 1 to ', len(self.teams_names), ":")
            for i in range(len(self.teams_names)):
                print(str(i+1), ": ", self.teams_names[i])
            team_id = int(input())
            if int(team_id) not in range(1, len(self.teams_names) + 1):
                print("Invalid input, please type a valid team number.")
                continue
            else:
                invalid_input = False
        for i in range(1, len(self.teams_names) + 1):
            if i != team_id:
                self.create_stats_comparison(team_id, i)

    def create_visualization(self):
        """Generates a specific visualization from the list of possibilities for a chosen week, with user input

        Parameters
        ----------
        None

        Returns
        ----------
        None
        """
        invalid_input = True
        while invalid_input:

            self.week = self.last_week
            print('Please type the number of the Week you would like to create a Visualization for:\nSelect a week from 1 to', self.last_week, ".")
            week = int(input())
            if int(week) not in range(1, self.last_week + 1):
                print("Invalid input, please type a valid week number.")
                continue
            self.change_week(week)

            print('Please type the number corresponding to the Visualization you would like to see:')
            print("0: Exit")
            for i in range(len(self.visualization_options)):
                print(i+1, ": ", self.visualization_options[i])
            self.active_option = int(input())
            if int(self.active_option) in range(1, len(self.visualization_options) + 1):
                invalid_input = False
            else:
                print("Invalid input, please type a valid visualization option.")
                

        if self.active_option == 1:
            self.create_week_table()
        elif self.active_option == 2:
            self.create_week_score()
        elif self.active_option == 3:
            invalid_input = True
            while invalid_input:
                print('Please type the number of the Team you would like to create the Visualizations for the last week:\nSelect a team from 1 to ', len(self.teams_names), ":")
                for i in range(len(self.teams_names)):
                    print(str(i+1), ": ", self.teams_names[i])
                team_id = int(input())
                if int(team_id) not in range(1, len(self.teams_names) + 1):
                    print("Invalid input, please type a valid team number.")
                    continue
                else:
                    invalid_input = False
            for i in range(1, len(self.teams_names) + 1):
                if i != team_id:
                    self.create_stats_comparison(team_id, i)


    def change_week(self, new_week):
        """Changes the active week to the desired week

        Parameters
        ----------
        new_week : int
            the desired week to become active

        Returns
        ----------
        None
        """
        if new_week in range(1, self.last_week + 1):
            old_week = self.week
            self.week = new_week
            print("Week has changed from ", old_week, "to ", new_week)
        else:
            print("Invalid week number, please try again")

    def create_week_table(self):
        """Generates the Week Table visualization for the active week

        Parameters
        ----------
        None

        Returns
        ----------
        None
        """
        print("Creating visualization... Week ", self.week, " Table is being processed")
        self.active_option = 1
        self.week_table_data = self.data[self.data['Week'] == self.week].drop(columns=["Week"])
        week_table_drops = self.stats_drop_list
        week_table_drops.extend(['Team_id', 'Year', 'Win'])
        formatting_dict = {"Week_Result": "{:.1f}", "Score": "{:.1f}", "Matchup_Wins": "{:.1f}"}

        for stat in self.scoring_stats_list:
            if stat[1] == "percentage":
                formatting_dict[stat[0]] = "{:.3f}"
        self.week_table_data.drop(columns=week_table_drops, inplace=True) 
        self.week_table_data.sort_values(by=['Score'], ascending=False, inplace=True)
        self.display_week_table = self.week_table_data.rename(columns={'Team':'Week'+str(self.week)}).style.format(formatting_dict).background_gradient(cmap='RdBu', axis=0).hide_index()
        self.display_week_table.to_excel(self.save_dir + "_excel_week" + str(self.week) + ".xlsx")
        self.save_visualization()
        display(self.display_week_table)

    def create_week_score(self):
        """Generates the Week Score visualization for the active week

        Parameters
        ----------
        None

        Returns
        ----------
        None
        """
        print("Creating visualization... Week ", self.week, " Score Table is being processed")
        self.active_option = 2
        self.week_score_data = self.score_data[self.score_data['Week']==self.week].drop(columns=["Week"])

        self.week_score_data.drop(columns=['Team_id', 'Year', 'Manager'], inplace=True) 
        self.week_score_data.sort_values(by=['Score'], ascending=False, inplace=True)
        self.display_week_score = self.week_score_data.style.format({"Week_Result": "{:.1f}"}).background_gradient(cmap='RdBu', axis=0).set_precision(1).hide_index()
        self.save_visualization()
        display(self.display_week_score)

    def create_stats_comparison(self, team_id, opp_id):
        """Generates the Stat Comparison between 2 teams for the active week.

        Parameters
        ----------
        team_id : int
            the team identifier for the team that will be the focus of the visualization
        opp_id : int
            the team identifier for the opponent

        Returns
        ----------
        None
        """

        print("Creating visualization... Week ", self.week, " Stat Comparison between", self.teams_names[team_id-1], "and", self.teams_names[opp_id-1], "is being processed")

        title = "Stat Comparison - Week " + str(self.week) + " - Matchup: " + self.teams_names[team_id-1] + " vs " + self.teams_names[opp_id-1]
        filename = self.save_dir + "_week_" + str(self.week) + "_stat_comparison_" + str(team_id) + "_vs_" + str(opp_id)  + ".html"

        self.week_data = self.data[self.data['Week'] == self.week].drop(columns=["Week"])
        self.week_data.drop(columns=['Team_id', 'Manager', 'Year', 'Win'], inplace=True)

        stats = []
        stats_round = {}

        drop_list = ['Year', 'Manager', 'Score', 'Matchup_Wins', 'Week_Result', 'Win', 'GP']
        for stat in self.stats_list:

            if stat[1] == "fraction":
                numerator, denominator = self.separate_fraction(stat[0])
                drop_list.append(numerator)
                drop_list.append(denominator)
            else:
                stats.append(stat[0])
            if stat[1] == "percentage":
                stats_round[stat[0]] = 3
            else:
                stats_round[stat[0]] = 0

        mean_stats = self.data.mean()[stats]
        normalized_temp = self.data.drop(columns=drop_list).copy()

        # Criar method para fazer normalizacao
        normalized_temp["ones"]=1
        norm = "_norm"

        for stat in self.scoring_stats_list:
            string = stat[0] + norm
            if stat[1] == "inverse":
                normalized_temp[string] = normalized_temp["ones"].div(normalized_temp[stat[0]].div(mean_stats[stat[0]]))
                target = stat[0]
            else:
                normalized_temp[string] = normalized_temp[stat[0]].div(mean_stats[stat[0]])

            normalized_temp.drop(columns=[stat[0]], inplace=True)

        names = ['Team_id', 'Week', 'Team', 'ones'] + stats
        normalized_temp.columns = names

        normalized = normalized_temp[normalized_temp['Week'] == self.week].drop(columns=["Week"])
        real_stats = normalized.copy()
        normalized = normalized.drop(columns=['Team', 'ones']).set_index('Team_id').transpose()
        real_stats[target] = real_stats['ones'].div(real_stats[target])
        real_stats = real_stats.drop(columns=['Team', 'ones']).set_index('Team_id').mul(mean_stats)
        real_stats = real_stats.transpose()

        stats = normalized.index.tolist()

        you = team_id
        opp = opp_id

        color_list = []
        for i in range(len(normalized[you].values.tolist())):
            if normalized[you].values.tolist()[i] > normalized[opp].values.tolist()[i]:
                color_list.append('00ab66')
            else:
                color_list.append('e03531')

        data = {'stats': stats,
                'you': normalized[you].values.tolist(),
                'opp': normalized[opp].values.tolist(),
                'colors': color_list,
                'real_you': real_stats[you].values.tolist(),
                'real_opp': real_stats[opp].values.tolist()}

        source = ColumnDataSource(data=data)

        hover = HoverTool(tooltips=[("Stat","@stats"),("You","@real_you"), ("Opponent","@real_opp")], mode="mouse")

        p = figure(x_range=stats, y_range=(0, 2), plot_height=250, title=title, toolbar_location=None, tools=[hover])
        p.vbar(x=dodge('stats', -0.2, range=p.x_range), top='you', width=0.33, source=source, color='colors')
        p.vbar(x=dodge('stats',  0.2,  range=p.x_range), top='opp', width=0.33, source=source, color="#a9a9b3")
        p.x_range.range_padding = 0.1
        p.xgrid.grid_line_color = None
        save(p, filename=filename)
        show(p)

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