#!/usr/bin/env python

from pathlib import Path

import duckdb
import pandas as pd

import settings
import things_parser

# Connect to MotherDuck (Use your own token)
conn = duckdb.connect("md:things", config={"motherduck_token": settings.MD_ACCESS_TOKEN})

column_names = things_parser.uplink_gateway_columns()
log_dir = Path(__file__).parent / "gtw-log"
parquet_path = log_dir / 'temp.parquet'
for fpath in log_dir.glob("gtw.log.*"):
    try:
        print(fpath)
        df = pd.read_csv(fpath, names=column_names, header=None)
        df["ts"] = pd.to_datetime(df["ts"], unit="s")
        df.to_parquet(log_dir / 'temp.parquet')
        conn.execute(f'''
            COPY gtw 
            FROM '{parquet_path}'
            (FORMAT 'parquet');
            ''')
        fpath.unlink()
        
    except:
        print(f"Error processing {fpath}")
