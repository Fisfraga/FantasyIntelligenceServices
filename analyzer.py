"""Analyzer Module used to generate sci-kit learn models to predict future preformance.
Use this module to import the Analyze_Players_Data class.

Please be sure that the following libraries installed in the python Source folder:
abc, sklearn, pandas, numpy, os, matplotlib, seaborn, IPython
"""

__author__ = "Felipe P A Fraga (fisfraga)"
__email__ = "lipefraga@gmail.com"

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
import os
import seaborn as sns
from IPython.display import display

from sklearn import svm
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn import linear_model
from sklearn.linear_model import ElasticNetCV, MultiTaskElasticNetCV

class Data_Analyzer(ABC):
    """
    Abstract class for the analyzing of the organized data.
    Should be initiated using an Data_Organizer object

    Attributes
    ----------
    stats_list : Array
        a list of the extracted stats for the Fantasy League
    scoring_stats_list : Array
        the list of the stats which are considered for the Fantasy League
    valid_input : bool
        variable to indicate the presence of organized data
    save_dir : str
        path to the directory where the visualizations will be saved to

    Methods:
    ----------
    __init__():
        initializes a Data_Visualization object and checks if the Data_Organizer object used to initialize it contains the data
    generate_all_analysis():
        abstract method that will generates 
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
            self.stats_list = organized_data.stats_list
            self.scoring_stats_list = organized_data.scoring_stats_list
        except AttributeError:
            print("Input not recognised, please be sure to initialize this Class with an OrganizedData object")
            self.valid_input = False
        else:
            self.save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Analyzer_Output\\", organized_data.league_name)
            self.valid_input = True
            print("This class supports the following functionalities:")


    @abstractmethod
    def generate_all_analysis(self):
        """Abstract method that will generates

        Parameters
        ----------
        None

        Returns
        ----------
        None
        """
        pass


class Analyze_Players_Data(Data_Analyzer):
    """Subclass for analysing the organized_data for players. Runs a prediction for the 
    performance of players in a selected year, based on previous performance.
    Should be initiated using a Players_Data_Organizer object.


    Attributes
    ----------
    player_info : dict
        dictionary with the descriptive information of the players, name, team, position
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
    model_names : Array
        list with the names of the models used to fit the data and predict the outcome
    predictions_3 : pandas.core.frame.DataFrame
        predictions made by the model considering the last 3 years of performance
    ranking_3 : pandas.core.frame.DataFrame
        rankings created by the model considering the last 3 years of performance
    predictions_2 : pandas.core.frame.DataFrame
        predictions made by the model considering the last 2 years of performance
    ranking_2 : pandas.core.frame.DataFrame
        rankings created by the model considering the last 2 years of performance
    predictions_1 : pandas.core.frame.DataFrame
        predictions made by the model considering the last year of performance
    ranking_1 : pandas.core.frame.DataFrame
        rankings created by the model considering the last year of performance
    final_predictions : pandas.core.frame.DataFrame
        final predictions made by the model and the actual results
    

    Methods
    --------
    generate_all_analysis(year)
        overriden method for generating all the available analysis
    generate_analysis_3_years(models_template, year):
        generates the predictions for the chosen year, using data from the last 3 years in the sci-kit learn models
    generate_analysis_2_years(models_template, year):
        generates the predictions for the chosen year, using data from the last 2 years in the  sci-kit learn models
    generate_analysis_1_year(models_template, year):
        generates the predictions for the chosen year, using data from the last year in the  sci-kit learn models
    analyse_predictions(pred, ranking, y_real, drop_list):
        creates a DataFrame for the rankings of each prediction, calculates averages and errors
    """

    def __init__(self, data):
        """
        """
        super().__init__(data)
        if self.valid_input is False:
            print("Analyzer was not created")
        else:
            self.player_info = data.player_info

            self.avg_dfs = data.avg_dfs
            self.X_dfs = data.X_dfs
            self.y_dfs = data.y_dfs

            self.avg_dfs_advanced = data.avg_dfs_advanced
            self.X_dfs_advanced = data.X_dfs_advanced
            print("Generate all the predictions for a given year: use .generate_all_analysis(year)")


    def generate_all_analysis(self, year=2019):
        """Generates all the available analysis.

        Parameters
        ----------
        year : int
            year that will be predicted by the model

        Returns
        ----------
        None
        """
        self.model_names = ["forest", "lasso", "elastic", "ridge"]
        forest = RandomForestRegressor()
        lasso = linear_model.Lasso(alpha=0.1)
        elastic = linear_model.HuberRegressor()
        #MultiTaskElasticNetCV(cv=5, random_state=0)
        ridge = linear_model.Ridge()

        models_3 = [forest, lasso, elastic, ridge]
        models_2 = [RandomForestRegressor(), linear_model.Lasso(alpha=0.1), linear_model.HuberRegressor(), linear_model.Ridge(alpha=.5)]
        models_1 = [RandomForestRegressor(), linear_model.Lasso(alpha=0.1), linear_model.HuberRegressor(), linear_model.Ridge(alpha=.5)]

        self.generate_analysis_3_years(models_3, year)
        self.generate_analysis_2_years(models_2, year)
        self.generate_analysis_1_year(models_1, year)


    def generate_analysis_3_years(self, models_template, year):
        """Generates the predictions for the chosen year, using sci-kit learn models.
        Considers the data for the past 3 years when predicting the next.

        Parameters
        ----------
        models_templates : Array
            list with the object for each sci-kit learn model that will fit the data
        year : int
            year that will be predicted by the model

        Returns
        --------
        None
        """
        print("Generating analysis using 3 previous years data")
        models = models_template.copy()
        X_3_years = []
        y_3_years = []
        for season in list(self.X_dfs.keys()):
            if season < year - 3:
                temp = pd.merge(self.X_dfs[season].copy(), self.X_dfs[season+1].copy(), suffixes=('_3', '_2'), left_index=True, right_index=True)
                X_3_years.append(pd.merge(temp, self.X_dfs[season+2].copy(), suffixes=('', '_1'), left_index=True, right_index=True))
                y_3_years.append(self.y_dfs[season+3].copy())
        
        X_3 = pd.concat(X_3_years).reset_index(drop=True)
        y_3 = pd.concat(y_3_years).reset_index(drop=True)
        
        drop_list = []
        for index, row in X_3.iterrows():
            if row['6_3'] == 0.0 or row['6_2'] == 0.0 or row[6] == 0.0:
                drop_list.append(index)
        X_3.drop(index=drop_list, inplace=True)
        y_3.drop(index=drop_list, inplace=True)

        temp = pd.merge(self.X_dfs[year-3].copy(), self.X_dfs[year-2].copy(), suffixes=('_3', '_2'), left_index=True, right_index=True)
        X_3_test = pd.merge(temp, self.X_dfs[year-1].copy(), suffixes=('', '_1'), left_index=True, right_index=True)
        y_3_real = self.y_dfs[year].copy()

        test_drop_list = []
        
        for index, row in X_3_test.iterrows():
            if row['6_3'] == 0.0 or row['6_2'] == 0.0 or row[6] == 0.0:
                test_drop_list.append(index)
        X_3_test.drop(index=test_drop_list, inplace=True)
        y_3_real.drop(index=test_drop_list, inplace=True)

        predictions = []
        for model in models:
            print(model)
            model.fit(X_3, np.ravel(y_3))
            pred = model.predict(X_3_test)
            predictions.append(pred)

        self.predictions_3 = pd.DataFrame(predictions).transpose()
        self.ranking_3 = pd.DataFrame.from_dict(self.player_info[2020], orient='index')
        
        self.analyse_predictions(self.predictions_3, self.ranking_3, y_3_real, test_drop_list)

        self.final_predictions = self.ranking_3[['Player', 'Position', 'Team', 'Average Prediction', 'Reality', 'Avg_Rank_err']].copy().sort_values('Average Prediction')
        self.final_predictions['Avg_Rank_err'] = self.final_predictions['Avg_Rank_err'].abs()
        col_1_name = str(year) + "Predictions and Reality"
        self.final_predictions['Player'].rename(col_1_name, inplace=True)
        cm = sns.diverging_palette(220, 20, as_cmap=True)
        self.final_predictions = self.final_predictions.style.background_gradient(cmap=cm).set_precision(0).hide_index()
        display(self.final_predictions)
        self.final_predictions.to_excel(self.save_dir + str(year) + "_predictions_using_last_3_years.xlsx")

    def generate_analysis_2_years(self, models_template, year):
        """Generates the predictions for the chosen year, using sci-kit learn models.
        Considers the data for the past 2 years when predicting the next.

        Parameters
        ----------
        models_templates : Array
            list with the object for each sci-kit learn model that will fit the data
        year : int
            year that will be predicted by the model

        Returns
        --------
        None
        """
        print("Generating analysis using 2 previous years data")
        models = models_template.copy()
        X_2_years = []
        y_2_years = []
        for season in list(self.X_dfs.keys()):
            if season < year-2:
                X_2_years.append(pd.merge(self.X_dfs[season].copy(), self.X_dfs[season+1].copy(), suffixes=('_2', '_1'), left_index=True, right_index=True))
                y_2_years.append(self.y_dfs[season+2].copy())
        
        X_2 = pd.concat(X_2_years).reset_index(drop=True)
        y_2 = pd.concat(y_2_years).reset_index(drop=True)
        
        drop_list = []
        for index, row in X_2.iterrows():
            if row['6_2'] == 0.0 or row['6_1'] == 0.0:
                drop_list.append(index)
        X_2.drop(index=drop_list, inplace=True)
        y_2.drop(index=drop_list, inplace=True)

        X_2_test =  pd.merge(self.X_dfs[year-2].copy(), self.X_dfs[year-1].copy(), suffixes=('_2', '_1'), left_index=True, right_index=True)
        y_2_real = self.y_dfs[year].copy()

        test_drop_list = []
        for index, row in X_2_test.iterrows():
            if row['6_2'] == 0.0 or row['6_1'] == 0.0:
                test_drop_list.append(index)
        X_2_test.drop(index=test_drop_list, inplace=True)
        y_2_real.drop(index=test_drop_list, inplace=True)

        predictions = []
        for model in models:
            model.fit(X_2, np.ravel(y_2))
            pred = model.predict(X_2_test)
            predictions.append(pred)

        self.predictions_2 = pd.DataFrame(predictions).transpose()
        self.ranking_2 = pd.DataFrame.from_dict(self.player_info[2020], orient='index')
        self.analyse_predictions(self.predictions_2, self.ranking_2, y_2_real, test_drop_list)

        final_predictions = self.ranking_2[['Player', 'Position', 'Team', 'Average Prediction', 'Reality', 'Avg_Rank_err']].copy().sort_values('Average Prediction')
        final_predictions['Avg_Rank_err'] = final_predictions['Avg_Rank_err'].abs()
        col_1_name = str(year) + "Predictions and Reality"
        final_predictions['Player'].rename(col_1_name, inplace=True)
        cm = sns.diverging_palette(220, 20, as_cmap=True)
        display_predictions = final_predictions.style.background_gradient(cmap=cm).set_precision(0).hide_index()
        display(display_predictions)

        display_predictions.to_excel(self.save_dir + str(year) + "_predictions_using_last_2_years.xlsx")

    def generate_analysis_1_year(self, models_template, year):
        """Generates the predictions for the chosen year, using sci-kit learn models.
        Considers the data for the past year when predicting the next.

        Parameters
        ----------
        models_templates : Array
            list with the object for each sci-kit learn model that will fit the data
        year : int
            year that will be predicted by the model

        Returns
        --------
        None
        """
        print("Generating analysis using the previous year's data")
        models = models_template.copy()
        X_1 = pd.concat(list(self.X_dfs[season] for season in range(2012, year-1))).reset_index(drop=True)
        y_1 = pd.concat(list(self.y_dfs[season] for season in range(2013, year))).reset_index(drop=True)
        drop_list = []
        for index, row in X_1.iterrows():
            if row[6] == 0.0:
                drop_list.append(index)
        X_1.drop(index=drop_list, inplace=True)
        y_1.drop(index=drop_list, inplace=True)
        X_1_test = self.X_dfs[year-1].copy()
        y_1_real = self.y_dfs[year].copy()

        test_drop_list = []
        for index, row in X_1_test.iterrows():
            if row[6] == 0.0:
                test_drop_list.append(index)
        X_1_test.drop(index=test_drop_list, inplace=True)
        y_1_real.drop(index=test_drop_list, inplace=True)

        predictions = []
        for model in models:
            model.fit(X_1, np.ravel(y_1))
            pred = model.predict(X_1_test)
            predictions.append(pred)
        
        self.predictions_1 = pd.DataFrame(predictions).transpose()
        self.ranking_1 = pd.DataFrame.from_dict(self.player_info[2020], orient='index')

        self.analyse_predictions(self.predictions_1, self.ranking_1, y_1_real, test_drop_list)

        final_predictions = self.ranking_1[['Player', 'Position', 'Team', 'Average Prediction', 'Reality', 'Avg_Rank_err']].copy().sort_values('Average Prediction')
        final_predictions['Avg_Rank_err'] = final_predictions['Avg_Rank_err'].abs()
        col_1_name = str(year) + "Predictions and Reality"
        final_predictions['Player'].rename(col_1_name, inplace=True)
        cm = sns.diverging_palette(220, 20, as_cmap=True)
        display_predictions = final_predictions.style.background_gradient(cmap=cm).set_precision(0).hide_index()
        display(display_predictions)

        display_predictions.to_excel(self.save_dir + str(year) + "_predictions_using_last_year.xlsx")

    def analyse_predictions(self, pred, ranking, y_real, drop_list):
        """Creates a DataFrame for the rankings of each prediction, calculates averages and errors

        Paramaters
        -----------
        pred : pandas.core.frame.DataFrame
            DataFrame with the predictions for each model
        ranking : pandas.core.frame.DataFrame
            DataFrrame that will hold the ranking for each prediction of points
        y_real : Array
            the actual performance for the players in the year that is being predicted
        drop_list : Array
            list with player ids that are not compatible with the model

        Returns
        --------
        None
        """
        ranking.columns=['Player', 'Position', 'Team']
        pred.columns = self.model_names
        names = [model + '_err' for model in self.model_names]
        ranking.drop(index=drop_list, inplace=True)
        ranking["Reality"] = y_real.rank(ascending=False)
        pred.index = ranking.index
        pred['Average'] = pred.mean(axis=1)
        pred['Reality'] = y_real
        for model in self.model_names:
            ranking[model] = pred[model].rank(ascending=False)
        ranking['Average Prediction'] = ranking.drop(columns=['Player', 'Position', 'Team', 'Reality']).mean(axis=1)
        ranking['Ranking of Averages'] = pred['Average'].rank(ascending=False)
        ranking['Avg_Rank_err'] = ranking['Average Prediction'].sub(ranking["Reality"])
        ranking['Rank_of_Avg_err'] = ranking['Ranking of Averages'].sub(ranking["Reality"])
        for i in range(len(names)):
            ranking[names[i]] = ranking[self.model_names[i]].sub(ranking["Reality"])
            error = ranking[names[i]].abs().sum()
            print(self.model_names[i], error)
        
