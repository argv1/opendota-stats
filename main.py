#!/usr/bin/env python3
'''
    small script to scrap all dota2 stats
    (including turbo matches, which are usually not included)
    (https://github.com/argv1/dota2/stats/)
    
    Usage: main.py -p PLAYERIDS 
    i.e. main.py -p 221666230 12345674

    opendota API documentation: https://docs.opendota.com/
    please feel free to improve
'''

import argparse
import numpy as np
import os.path
import pandas as pd
from   pathlib import Path
import requests

def get_matches(player_Ids):
    '''
    Load already scrapped matches, 
    check for matches from the provided userid and 
    grab missing ones
    '''
    # Define path and filename
    base_path     = Path(__file__).parent.absolute()  #adjust
    game_modes_f  = base_path / 'data\game_mode.txt'       
    heroes_f      = base_path / 'data\hero_ids.txt'
    lobby_types_f = base_path / 'data\lobby_type.txt'
    match_f = player_Ids[0]

    # 0 = including turbo, 1 = without
    url = f"https://api.opendota.com/api/players/{player_Ids[0]}/matches?significant=0"
    if(len(player_Ids) > 1):
        for entry in range(1,len(player_Ids)):
            url += f"&included_account_id={player_Ids[entry]}"
            match_f += '-' + player_Ids[entry]
    match_f = base_path / f'{match_f}.csv'

    # check if match_data already exists, else create it
    if not os.path.isfile(match_f):
        df = pd.DataFrame(columns=["match_id", "player_slot", "radiant_win", "duration", "game_mode", "lobby_type", "hero_id", "start_time", "version", "kills", "deaths", "assists", "skill", "leaver_status", "party_size"])
        df.to_csv(match_f, index=False)

    # load existing matches
    df = pd.read_csv(match_f)
    match_ids = pd.Series(df.match_id)
    
    # start request
    resp = requests.get(url=url)
    data = resp.json()
    
    # store every new match in the dataframe
    df = pd.DataFrame.from_records(data)
    
    # check for duplicate matches
    df.drop_duplicates(subset='match_id',inplace=True)

    # decode lobbies, games and heroes
    for column in ["game_mode", "hero_id", "lobby_type"]:
        df[column] = df[column].astype("str")

    with game_modes_f.open("r") as f:
        game_modes = dict(x.rstrip().split(None, 1) for x in f)
    df.game_mode.replace(game_modes, inplace=True)

    with heroes_f.open("r") as f:
        heroes = dict(x.rstrip().split(None, 1) for x in f)
    df.hero_id.replace(heroes, inplace=True)

    with lobby_types_f.open("r") as f:
        lobby_types = dict(x.rstrip().split(None, 1) for x in f)
    df.lobby_type.replace(lobby_types, inplace=True)

    # Drop heroes column
    if(len(player_Ids) > 1): df.drop("heroes", axis=1,  inplace=True)

    # Add additional informations
    df['factions'] = np.where(np.greater_equal(df.player_slot,128), "Dire", "Radiant")
    df['won'] = np.where(np.logical_or(np.logical_and(np.greater_equal(df.player_slot,128),np.equal(df.radiant_win,False)),np.logical_and(np.less(df.player_slot,128),np.equal(df.radiant_win,True))), "Won", "Lost")
    df['KD'] = np.where(np.greater(df.deaths,0),df.kills / df.deaths, df.kills)
    df['KDA'] = np.where(np.greater(df.deaths,0),(df.kills + df.assists) / df.deaths, df.kills + df.assists)

    return(df, match_f)

def main():
    # Initiate the parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--player_Ids', nargs='+', help='Enter opendota user id(s)', required=True)
    args = parser.parse_args()
    player_Ids = args.player_Ids

    # get all matches
    df, match_f = get_matches(player_Ids)

    # write new dataframe to csv
    df.to_csv(match_f, index=False)

if __name__ == '__main__':
    main()