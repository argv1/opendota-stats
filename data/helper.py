#!/usr/bin/env python3
'''
    small utility script to scrap all dota2 heros
    (https://github.com/argv1/dota2/stats/)
    
    opendota API documentation: https://docs.opendota.com/
    please feel free to improve
'''

import numpy as np
import os.path
import pandas as pd
from   pathlib import Path
import requests

def main():
    # Create df
    df = pd.DataFrame(columns=["id", "name", "localized_name", "primary_attr", "attack_type", "roles"])

    # Request current hero list
    url = f"https://api.opendota.com/api/heroes"
    resp = requests.get(url=url)
    data = resp.json()

    df = pd.DataFrame.from_records(data)
    df_full = df.copy()
    df = df[["id", "localized_name"]]

    # write new dataframe to txt
    with open("hero_ids.txt", "w") as f:
        dfAsString = df.to_string(header=False, index=False)
        f.write(dfAsString)

    # write new dataframe to csv
    df_full.to_csv("hero_lore.csv", index=False)

if __name__ == '__main__':
    main()
