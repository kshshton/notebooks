import json

import pandas as pd
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine

URL = 'https://www.op.gg/leaderboards/tier'

response = requests.get(URL)
soup = BeautifulSoup(response.text, "lxml")
data = json.loads(soup.find('script', {'id': "__NEXT_DATA__"}).string)
data = data['props']['pageProps']
champions_mapping = {meta['id']: meta['name'] for meta in data['championById'].values()}

leaderboard = []
for meta in data['data']:
    for champion in meta['summoner']['most_champions']['champion_stats']:
        leaderboard.append({
            'rank': meta['rank'],
            'lp': next(mode['tier_info']['lp'] 
                       for mode in meta['summoner']['league_stats'] 
                       if mode['game_type'] == 'SOLORANKED' and mode['tier_info']['tier'] == 'CHALLENGER'
                      ),
            'champion': champions_mapping.get(champion['id']),
            'games': champion['play'],
            'winratio': round((champion['win'] / champion['play']) * 100),
        })

df = pd.DataFrame(leaderboard)
engine = create_engine('sqlite:///eune.db')
df.to_sql('eune_leaderboard', con=engine, if_exists='replace', index=False)

def sql(query: str) -> pd.DataFrame:
    return pd.read_sql_query(query, con=engine)

sql(
    """    
    SELECT 
        *,
        COUNT(rank) OVER (PARTITION BY champion) AS players_cnt
    FROM eune_leaderboard el
    """
).to_sql('eune_leaderboard', con=engine, if_exists='replace', index=False)

print("\nThe most played champion in challanger")
print(sql(
    """
    WITH ranked_players_cnt AS (
        SELECT DISTINCT 
            champion, 
            players_cnt,
            DENSE_RANK() OVER (ORDER BY players_cnt DESC) AS rank
        FROM eune_leaderboard
    )
    SELECT champion, players_cnt
    FROM ranked_players_cnt
    WHERE rank <= 3
    """
))

print("\nThe best mains on EUNE")
print(sql(
    """
    SELECT DISTINCT rank, champion, games, winratio
    FROM eune_leaderboard
    WHERE winratio > 70
        AND games > 50
    ORDER BY games * winratio DESC
    """
))
