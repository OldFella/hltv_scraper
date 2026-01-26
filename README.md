# HLTV Scraper

Project to scrape data from the hltv.org website to obtain per game statistics for teams and players of the top 100 in Valve Regional Standings (VRS).

## Features:
  - Scraping pipeline based on Selenium (Handling JS Websites) for websites including:
      - www.hltv.org/valve-ranking/teams/
      - www.hltv.org/results/
      - www.hltv.org/matches/*
        
  - Export in PostgreSQL Database
  - Automatic scraping and db insertion pipeline
  - Export basic spreadsheet 

## Install:
```bash
git clone https://github.com/OldFella/hltv_scraper.git
cd hltv_scraper
pip install -r requirements.txt
```

## Usage:

- Get current team rankings:

```bash
python src/scripts/scrape_teams.py
```

- Get latest results:

```bash
python src/scripts/scrape_results.py
```

- Update database:

```bash
python src/db_handling/scrape_db.py
```

- Automatically scrape and update database:

```bash
python src/main.py
```

## TODO:
  - Scraper for VRS Ranking ✅
  - Scraper for necessary matches with links ✅
  - Extracting necessary information from the match pages ✅
  - Building Database for Teams and Players ✅
  - Automating scraping process ✅
  - Create queries to create a spreadsheet (in progress)


## Database Design Sample:

You can preview a sample of the scraped data directly on GitHub:

➡️ [data/database_sample/player_stats.csv](data/database_sample/player_stats.csv)


## Tech Stack

Python • Selenium • beautifulsoup4 • psycopg2 • JinjaSQL • PostgreSQL • pandas
