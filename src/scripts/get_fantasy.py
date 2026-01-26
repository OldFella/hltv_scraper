from bs4 import BeautifulSoup
import pandas as pd
import argparse
import re



class fantasy:
    
    def run(self,file):
        soup = self.open_html(file)
        fantasy, id = self.find_fantasy(soup)
        teams = self.get_teams(fantasy)
        title = self.get_title(soup)
        df = self.create_table(teams, id,title)

        return df


    def open_html(self,file):
        with open(file) as f:
            content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
    
        return(soup)

    def find_fantasy(self,soup):
        fantasy = soup.find('div', class_ = "fantasyMoneyDraft")
        fantasy_id = soup.find('div', class_= "menu-tab")
        fantasy_id = fantasy_id.find('a', href=True)
        fantasy_id = fantasy_id.get('href')
        fantasy_id = fantasy_id.split('/')
        return fantasy,fantasy_id[-2]


    def get_teams(self,fantasy):
        teams = fantasy.find_all('div', class_ = 'teamCon')
        result = {}

        player_pattern = r'/stats/players/([0-9]*)/'
        for team in teams:
            header = team.find('div', class_ = 'teamHeader')
            name = header.find('div', class_ = 'teamName text-ellipsis').text

            players = team.find_all('div', class_ = 'teamPlayer')
            team_content = {}
            for player in players:
                player_id = player.find('a', class_ = "player-stats-link")
                player_id = player_id.get('href')
                player_id = re.findall(player_pattern, player_id)[0]
                player_id = int(player_id)

                player_cost = player.find('div', class_ = 'playerButtonText').text
                team_content[player_id] = player_cost
            
            result[name] = team_content
        
        return result

    def get_title(self, soup):
        nav_item = soup.find_all('ul', class_ ='nav-item')[11]

        title = nav_item.find_all('div', class_ ="text-ellipsis")[-1]

        return title.text
        

    def create_table(self,d,id,title):
        df = pd.DataFrame(columns=['fantasyID','title','team', 'playerid', 'cost'])
        for name, team_content in d.items():
            for player, cost in team_content.items():
                cost = cost.replace("$",'')
                cost = cost.replace(',000', '')
                df.loc[len(df)] = [id, title,name ,player, int(cost)]
        return df




if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--input','-i', type = str, default = '../data/fantasy_html/fantasy.html')
    parser.add_argument('--output','-o', type = str, default = 'fantasy.csv')
    args = parser.parse_args()

    
    df = fantasy().run(args.input)
    output_path = args.input.split('/')
    output_path = output_path[:-1]
    output_path = '/'.join(output_path)
    output_path += '/' + args.output

    df.to_csv(output_path, index = False)
