# HLTV Scraper

Project to scrape data from hltv.org. The hltv website provides information about all things Counter Strike 2 e-sports. Unfortunalty, they do not provide an api to simply obtain data about the competitive matches, as well as a fantasy league. This project aims to automatically scrape all game statistics for teams and players of the top 100 in Valve Regional Standings (VRS). Ultimately, the data will be used to make a prediction for the best draftable teams.

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

## Create Database:

- install postgresql
- make new database
- create user to with read permissions
- create user with write permissions

- create table using:
  [create_tables.sql](create_database/create_tables.sql)


## Usage:

- Get current team rankings:

```bash
python src/scripts/scrape_teams.py
```

- Get latest results:

```bash
python src/scripts/scrape_results.py
```

- Automatically scrape and update database:

```bash
python src/main.py
```

- Extract fantasy table from downloaded html:

```bash
python src/scripts/get_fantasy.py
```

- Insert fantasy into database:

```bash
python src/scripts/update_fantasy.py
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

➡️ [player_stats.csv](data/database_sample/player_stats.csv)


## Tech Stack

Python • Selenium • beautifulsoup4 • psycopg2 • JinjaSQL • PostgreSQL • pandas
