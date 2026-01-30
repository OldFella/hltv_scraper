import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import datetime
import os
import numpy as np
from scraper.scraper_base import scraper_base


class result_scraper(scraper_base):
    """
    Opens hltv.org/results and saves relevant matches
    """
    def __init__(self,page=0, url="https://www.hltv.org/results", top = 100,teams_path = "./data/team_rankings/" ,dir = './data/matches/'):
        super().__init__()
        self.page = page
        self.url = url
        self.top = top
        if self.page != 0:
            self.url += f'?offset={self.page*100}'

        self.date = datetime.today().strftime('%Y-%m-%d')
        self.teams_path = teams_path
        self.dir = dir
        self.teams = []
        self.results_data = []
        self.results_table = pd.DataFrame(columns=['matchID'])
        if os.path.exists(f"{self.dir}matches.csv"):
            self.results_table = pd.read_csv(f"{self.dir}matches.csv")
        self.results = pd.DataFrame(columns=['matchID', 'team1', 'score1', 'team2','score2','event' ,'url'])

        self.get_teams(n = self.top)
        self.open_results()
        self.parse_results()
        self.extract_relevant_results()
        self.write_rankings()
    
    def open_results(self):
        driver = webdriver.Firefox(options=self.options)
        driver.get(self.url)

        results = []
        
        p_element = driver.find_elements(By.CLASS_NAME,'a-reset')
        results = []
        
        for e in p_element:
            html = e.get_attribute('innerHTML')
            link = e.get_attribute("href")
            if '/forums' in link:
                break
            results.append((html, link))
            
        driver.quit()

        self.results_data = results

    def parse_results(self):
        pattern_id = r'matches/([^"]*)/'
        pattern_team = r'<img alt="([^"]*)"'
        pattern_score = r'<td class="result-score"><span class="(score-won|score-lost)">([^"]*)</span> - <span class="(score-won|score-lost)">([^"]*)</span></td>'
        for i, (data,link) in enumerate(self.results_data):
            teams = re.findall(pattern_team, data)
            teams = pd.unique(np.array(teams)).tolist()
            score = re.findall(pattern_score, data)
            match_id = int(re.findall(pattern_id, link)[0])
            if match_id in self.results_table['matchID'].to_list():
                continue
            self.results.loc[i] = [match_id, teams[0], int(score[0][1]), teams[1], int(score[0][3]), teams[2], link]
    
    def extract_relevant_results(self):
        self.results = self.results.drop_duplicates()
        self.results = self.results[self.results['team1'].isin(self.teams) & self.results['team2'].isin(self.teams)]

    def write_rankings(self):
        self.results = pd.concat([self.results, self.results_table])
        self.results = self.results.drop_duplicates()
        self.results.to_csv(f"{self.dir}matches.csv", index= False)

    def get_results_data(self):
        return self.results_data
    
    def get_results(self):
        return self.results

    def get_teams(self,n = -1):
        rankings = os.listdir(self.teams_path)
        curr_ranking = sorted(rankings)[0]
        df = pd.read_csv(f'{self.teams_path}{curr_ranking}')
        if n != -1:
            self.teams = df['name'][:n]
        else:
            self.teams = df['name']
