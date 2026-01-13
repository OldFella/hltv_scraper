from tools.scraper import team_scraper

if __name__ == '__main__':
    ts = team_scraper()
    print(ts.get_teams())