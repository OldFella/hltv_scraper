#!/bin/bash

DIR=/root/hltv_scraper/


${DIR}.venv/bin/python3 ${DIR}src/main.py -d ${DIR}data/temp/ -c ${DIR}src/db_handling/database.ini


date -u +"%Y-%m-%dT%H:%M:%SZ" > /root/hltv_api/src/last_updated.txt
