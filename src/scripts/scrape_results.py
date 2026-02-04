import sys
sys.path.append('../')
from scraper.result_scraper import result_scraper
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--top', type = int, default = -1)
    parser.add_argument('--dir', type = str, default = 'matches/')
    parser.add_argument('--teams', type = str, default = "../data/temp/tmp_2026-02-02/team_rankings/")
    parser.add_argument('--max_pages', type = int, default=6)

    args = parser.parse_args()
    for page in range(args.max_pages):
        rs = result_scraper(page=page,top = args.top,dir = args.dir, teams_path=args.teams)
    print(rs.get_results())
