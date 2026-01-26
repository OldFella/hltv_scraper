import pandas as pd
import requests
from bs4 import BeautifulSoup


class event_scraper:
    def __init__(self):
        self.event_list = pd.DataFrame(columns=['name', 'url'])
        self.event = pd.DataFrame(columns=['name', 'lp_tier', 'valve_tier', 'pt_tier'])
    
    def getHtml(self, url):
        reg = requests.get(url)
        soup = BeautifulSoup(reg.text, 'html.parser')

        years = soup.find_all('div', class_ = "gridTable")

        for year in years:

            element = year.find_all('div', class_ = "gridCell Tournament Header")
            for e in element:
                url_element = e.find_all('a', href=True)
                last_element = url_element[-1]
                self.event_list.loc[len(self.event_list)] = [last_element.text, last_element.get('href')]
                
    def open_matches(self,f):
        df = pd.read_csv(f)
        events = df['event'].unique()
        return events
    
    def open_event(self,data):

        url = 'https://liquipedia.net' + data['url']
        reg = requests.get(url)
        soup = BeautifulSoup(reg.text, 'html.parser')

        side_info = soup.find('div', class_ = "fo-nttax-infobox")
        rows = side_info.find_all('div')
        lp_tier = None
        valve_tier = None
        pt_tier = None

        for row in rows:
            
            row_content = row.find_all('div')
            if row_content != [] and row != '' and len(row_content) == 2:
                tier_name = row_content[0].text
                tier = row_content[1].text
                if 'Liquipedia Tier' in tier_name:
                    lp_tier = tier
                if 'Pro Tour Tier' in tier_name:
                    pt_tier = tier
                if ' Tier:' == tier_name:
                    valve_tier = tier
        
        self.event.loc[len(self.event)] = [data['name'],lp_tier,valve_tier, pt_tier]