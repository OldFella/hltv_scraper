import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import datetime
import os
import numpy as np

class result_scraper:
    """
    Opens hltv.org/results and saves relevant matches
    """
    def __init__(self,page=0, url="https://www.hltv.org/results", top = 100):
        self.page = page
        self.url = url
        self.top = top
        if self.page != 0:
            self.url += f'?offset={self.page*100}'

        self.date = datetime.today().strftime('%Y-%m-%d')
        self.teams_path = "./data/team_rankings/"
        self.dir = "./data/matches/"
        self.teams = []
        self.results_data = []

        self.results_table = pd.read_csv(f"{self.dir}matches.csv",
                                         names=['match_id', 'team1', 'score1', 'team2','score2','event' ,'link'])
        self.results = pd.DataFrame(columns=['match_id', 'team1', 'score1', 'team2','score2','event' ,'link'])

        proxy = "20.235.159.154:80"
        self.options = Options()
        self.options.add_argument(f"--proxy-server={proxy}")
        self.options.add_argument("--headless")

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
            if match_id in self.results_table['match_id'].to_list():
                continue
            self.results.loc[i] = [match_id, teams[0], int(score[0][1]), teams[1], int(score[0][3]), teams[2], link]
    
    def extract_relevant_results(self):
        self.results.drop_duplicates()
        self.results = self.results[self.results['team1'].isin(self.teams) | self.results['team2'].isin(self.teams)]

    def write_rankings(self):
        self.results = pd.concat([self.results, self.results_table])
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
            self.teams = df['team_name'][:n]
        else:
            self.teams = df['team_name']


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



class match_scraper:
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless")
        self.match_src_path = "data/match_src/"
        self.player_stats = pd.DataFrame(columns=['matchID', 'playerID','team',
                                                  'map', 'side', 'k','d','ek',
                                                  'ed','roundSwing', 'adr', 'eadr',
                                                  'kast','ekast','rating'])
        
        self.players = pd.DataFrame(columns=['playerID', 'name'])
        self.match = pd.DataFrame(columns=['matchID', 'date','team1', 'score1', 'team2','score2'])

    def open_match(self, url):
        pattern_match_id = r'matches/([^"]*)/'
        match_id = re.findall(pattern_match_id,url)
        driver = webdriver.Firefox(options=self.options)
        driver.get(url)
        dates = driver.find_elements(By.CLASS_NAME, 'date')
        date = dates[1].text
        table_names = driver.find_elements(By.CLASS_NAME,'stats-menu-link')
        maps = []
        for e in table_names:
            maps.append(e.get_attribute('innerHTML'))
        table = driver.find_elements(By.CLASS_NAME,'stats-content')
        scores = []
        for e in table:
            scores.append(e.get_attribute("innerHTML"))
        
        driver.quit()        
        return zip(match_id * len(maps), [date] * len(maps),maps, scores)

    def get_stats(self,data):

        for match_id,date,maps, players in data:
            # print(maps)
            d = self.get_date(date)

            m = self.get_maps(maps)
            stats = self.get_player_stats(players)
            stats['date'] = d
            stats['map'] = m
            stats['matchID'] = match_id
            self.player_stats = pd.concat([self.player_stats, stats])
    
    def get_date(self, date):
        date = re.sub(r'(\d+)(st|nd|rd|th) of', r'\1', date)
        date = datetime.strptime(date, "%d %B %Y")
        return date.strftime("%Y-%m-%d")
    
    def get_maps(self, maps):
        pattern = r'id="[^"]*">([^"]*)</'
        map_match = re.findall(pattern, maps)
        return map_match[0]
    
    def get_player_stats(self,players):

        player_stats = pd.DataFrame(columns=['playerID', 'side','team', 'k','d','ek',
                                                  'ed','roundSwing', 'adr', 'eadr',
                                                  'kast','ekast','rating'])
        
        player_count = {}
            
        counts = {1:'total',
                2:'ct',
                3:'t'}
        teams = players.split('class="teamName')
        for team in teams:
    
            team_patterns = r'team">([^"]*)</a>'
            team_name = re.findall(team_patterns, team)

            players = team.split('<td class="players">')
            

            for player in players:
                start = player.find("/player/")
                if start == -1:
                    continue
                end = start + player[start:].find('"')
                _,_,p_id, name = player[start:end].split('/')

                player_info = pd.DataFrame({'playerID':[p_id], 'name':[name]})
                self.players = pd.concat([self.players, player_info])
                self.players = self.players.drop_duplicates()

                p_id = int(p_id)
                if p_id not in player_count.keys():
                    player_count[p_id] = 1

                pattern = r'class="([^"]*((kd|adr|roundSwing|kast|rating)[^"]*(traditional-data|eco-adjusted-data|text-center)[^"]*)[^"]*)">([+-]?[\d\.\-%]+)</td>'
                matches = re.findall(pattern, player)
                stats = {}
                for match in matches:

                    classes = match[2]
                    value = match[4]
                    value = value.replace('%','')

                    if 'eco' in match[3]:
                        classes = 'e'+classes
                        
                    if "kd" in classes and "eco" in match[3]:
                        k,d = value.split('-')
                        stats['ek'] = [float(k)]
                        stats['ed'] = [float(d)]

                    elif "kd" in classes and "eco" not in match[3]:
                        k,d = value.split('-')
                        stats['k'] = [float(k)]
                        stats['d'] = [float(d)]
                    else:
                        stats[classes] = [float(value)]


                stats['playerID'] = [p_id]
                stats['side'] = [counts[player_count[p_id]]]
                stats['team'] = team_name
                stat = pd.DataFrame(stats)
                player_count[p_id] += 1

                player_stats = pd.concat([player_stats, stat])
        
        return player_stats
