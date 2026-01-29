import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import datetime

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
        self.match = pd.DataFrame(columns=['matchID', 'map','side','date','team', 'score'])

    def open_match(self, row):
        url = row['url']

        pattern_match_id = r'matches/([^"]*)/'
        match_id = re.findall(pattern_match_id,url)
        driver = webdriver.Firefox(options=self.options)
        driver.get(url)
        dates = driver.find_elements(By.CLASS_NAME, 'date')
        date = dates[1].text
        map_rounds = driver.find_elements(By.CLASS_NAME, 'results-center-half-score')
        rounds_won = [f'({row["score1"]}:{row["score2"]})']
        to_replace = ['<','/','>', 'span', 'class=', '"'," "]
        for e in map_rounds:
            text = e.get_attribute('innerHTML')
            # Check for map forfeits
            if text == '':
                continue
            for r in to_replace:
                text = text.replace(r,"")
            rounds_won.append(text)
        table_names = driver.find_elements(By.CLASS_NAME,'stats-menu-link')
        maps = []
        for e in table_names:
            maps.append(e.get_attribute('innerHTML'))
        table = driver.find_elements(By.CLASS_NAME,'stats-content')
        scores = []
        for e in table:
            scores.append(e.get_attribute("innerHTML"))
        
        driver.quit()        
        return zip(match_id * len(maps), [date] * len(maps),maps, scores, rounds_won)

    def get_stats(self,data,row):

        for match_id,date,maps, players,rounds_won in data:
            d = self.get_date(date)

            m = self.get_maps(maps)
            stats = self.get_player_stats(players)
            # stats['date'] = d
            stats['map'] = m
            stats['matchID'] = match_id
            if self.player_stats.empty:
                self.player_stats = stats
            else:
                self.player_stats = pd.concat([self.player_stats, stats])
            if m == 'All':
                for team,score in [(row['team1'],row['score1']), (row['team2'],row['score2'])]:
                    match = [match_id, m,'total',d,team, score]
                    self.match.loc[len(self.match)] = match
            else:
                pattern = r'(ct|t)(\d+):(ct|t)(\d+)'
                reg_ot= rounds_won.split(')(')
                total_teams = [0,0]
                for s in reg_ot:
                    round_score = re.findall(pattern, s)
                    if round_score != []:
                        for side in round_score:
                            match = [match_id, m,side[0],d,row['team1'], int(side[1])]
                            self.match.loc[len(self.match)] = match
                            total_teams[0] += int(side[1])

                            match = [match_id, m,side[2],d,row['team2'], (side[3])]
                            self.match.loc[len(self.match)] = match
                            total_teams[1] += int(side[3])
                    else:
                        pattern = r'(\d+):(\d+)'
                        round_score = re.findall(pattern, s)
                        for i,side in enumerate(round_score[0]):
                            total_teams[i] += int(side)
                
                match = [match_id, m,'total',d,row['team1'], total_teams[0]]
                self.match.loc[len(self.match)] = match

                match = [match_id, m,'total',d,row['team2'], total_teams[1]]
                self.match.loc[len(self.match)] = match


    
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
                if player_stats.empty:
                    player_stats = stat
                else:
                    player_stats = pd.concat([player_stats, stat])
        
        return player_stats
