import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import pickle as pkl
import pandas as pd
from datetime import datetime

class result_scraper:
    """
    Opens hltv.org/results and saves relevant matches
    """
    def __init__(self):
        ...
    
    def open_results(self):
        ...
    
    def get_teams(self):
        ...


class team_scraper:
    """
    Returns Current Top n VRS Teams
    """
    def __init__(self, n = 150):
        self.number_teams = n
        self.website = "https://www.hltv.org/valve-ranking/teams/"

        self.options = Options()
        self.options.add_argument("--headless")

        self.teams = pd.DataFrame(columns=['team_name', 'points'])
        self.team_data = []

        self.open_rankings()
        self.get_rankings()
        self.write_teams()


    def open_rankings(self):
        driver = webdriver.Firefox(options=self.options)
        driver.get(self.website)
        p_element = driver.find_elements(By.CLASS_NAME,'ranking-header')
        teams = []
        for e in p_element:
            teams.append(e.get_attribute('innerHTML'))
        driver.quit()

        self.team_data = teams

    def get_rankings(self):
        pattern = r'class="name">([^"]*)</span><span class="points">\(([^"]*)<span'
        
        for i,team in enumerate(self.team_data):
            matches = re.findall(pattern, team)
            for match in matches:
                self.teams.loc[i] = [match[0] , int(match[1])]
    
    def get_teams(self):
        return self.teams

    def write_teams(self):
        time = datetime.today().strftime('%Y-%m-%d')
        self.teams.to_pickle(f"../data/teams/team_ranking_{time}.p")