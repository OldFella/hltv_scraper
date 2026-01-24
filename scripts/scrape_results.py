import sys
sys.path.append('../')
from scraper.result_scraper import result_scraper
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--top', type = int, default = 100)
    parser.add_argument('--dir', type = str, default = './data/matches/')
    parser.add_argument('--teams', type = str, default = "./data/team_rankings/")

    args = parser.parse_args()

    rs = result_scraper(top = args.top,dir = args.dir, teams_path=args.teams)
    print(rs.get_results())
