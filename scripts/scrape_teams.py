import sys
sys.path.append('../')
from scraper.team_scraper import team_scraper
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url','-u', type = str, default = "https://www.hltv.org/valve-ranking/teams/")
    parser.add_argument('--dir', '-d', type = str, default = '../data/team_rankings/')
    args = parser.parse_args()
    ts = team_scraper(url = args.url, dir = args.dir)
    print(ts.get_teams())