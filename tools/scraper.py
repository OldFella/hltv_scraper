import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import datetime
import os

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
    Scrapes current hltv valve rankings
    """
    def __init__(self):
        self.website = "https://www.hltv.org/valve-ranking/teams/"

        self.options = Options()
        self.options.add_argument("--headless")

        self.teams = pd.DataFrame(columns=['team_name', 'points', 'team_id'])
        self.team_data = []

        self.time = datetime.today().strftime('%Y-%m-%d')

        self.dir = "./data/team_rankings/"

        # only scrape if it does not already exist:

        if f'{self.time}.csv' in os.listdir(self.dir):
            self.teams = pd.read_csv(f'{self.dir}{self.time}.csv')
        

        else:
            print("open website...")
            self.open_rankings()
            print("get rankings...")
            self.get_rankings()
            print("save...")
            self.write_teams()


    def open_rankings(self):
        driver = webdriver.Firefox(options=self.options)
        driver.get(self.website)
        p_element = driver.find_elements(By.CLASS_NAME,'bg-holder')
        teams = []
        for e in p_element:
            teams.append(e.get_attribute('innerHTML'))
        driver.quit()

        self.team_data = teams

    def get_rankings(self):
        pattern = r'class="name">([^"]*)</span><span class="points">\(([^"]*)<span'
        pattern_id = r'href="/team/([^"]*)/'
        for i,team in enumerate(self.team_data):
            matches = re.findall(pattern, team)
            team_id = re.findall(pattern_id, team)

            for match in matches:
                self.teams.loc[i] =  [match[0] , int(match[1]), int(team_id[0])]
                
    def get_teams(self,n= -1):
        if n == -1:
            return self.teams
        return self.teams[:n]

    def write_teams(self):
        self.teams.to_csv(f"{self.dir}{self.time}.csv", index= False)