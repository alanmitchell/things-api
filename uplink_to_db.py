"""Checks for complete Things message log files and writes them
to the database.
"""
from pathlib import Path

import duckdb
import pandas as pd

import things_parser

def check_for_complete_log_files():
    db_path = Path(__file__).parent / "db" / "things.db"
    conn = duckdb.connect(db_path)

    # Check to see if the gateway table exists
    tables = conn.execute("SHOW TABLES").fetchdf()
    if "gateway" not in tables["name"].values:
        # create the gateway table
        conn.execute("""
            CREATE TABLE gateway (
            source VARCHAR,
            ts TIMESTAMP,
            device_id VARCHAR,
            device_eui VARCHAR,
            frame_counter INTEGER,
            gateway_id VARCHAR,
            gateway_eui VARCHAR,
            signal_snr FLOAT,
            signal_rssi INT2,
            data_rate VARCHAR
            )"""
        )

    log_dir = Path(__file__).parent / "gtw-log"
    complete_log_files = list(log_dir.glob("gtw.log.*"))
    if len(complete_log_files):
        column_names = things_parser.uplink_gateway_columns()
        parquet_path = log_dir / 'temp.parquet'
        for fpath in complete_log_files:
            try:
                print(fpath)
                df = pd.read_csv(fpath, names=column_names, header=None)
                df["ts"] = pd.to_datetime(df["ts"], unit="s")
                df.to_parquet(log_dir / 'temp.parquet')
                conn.execute(f'''
                    COPY gateway
                    FROM '{parquet_path}'
                    (FORMAT 'parquet');
                    ''')
                fpath.unlink()
                
            except:
                print(f"Error processing {fpath}")
