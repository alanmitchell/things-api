#!/usr/bin/env python

from pathlib import Path
from time import time

import duckdb
import pandas as pd

import settings
import things_parser

# Connect to MotherDuck (Use your own token)
conn = duckdb.connect("md:things", config={"motherduck_token": settings.MD_ACCESS_TOKEN})

column_names = things_parser.uplink_gateway_columns()
log_dir = Path(__file__).parent / "gtw-log"
for fpath in log_dir.glob("gtw.log.*"):
    print(fpath)
    st = time()
    df = pd.read_csv(fpath, names=column_names, header=None)
    df["ts"] = pd.to_datetime(df["ts"], unit="s")
    df.to_parquet('gtw-log/temp.parquet')
    conn.execute('''
COPY gtw 
FROM 'gtw-log/temp.parquet'
(FORMAT 'parquet');
''')
    print(time() - st)
