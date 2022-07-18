import tweepy as tp
import pickle
import sys
from datetime import datetime
from riotwatcher import LolWatcher

file_path = sys.path[0]
with open(f"{file_path}\keys") as f:
    lines = f.read().splitlines()

    keys_dct = {}
    new_key = {}
    for line in lines:
        new_key[line.split(" - ")[1]] = line.split(" - ")[0]
        keys_dct.update(new_key)

try:
    with open(f"{file_path}\mypicklejar","rb") as f:
        last_tweet = pickle.load(f)
except Exception:
    pass

client = tp.Client(
    bearer_token=keys_dct["Twitter Bearer Token"],
    consumer_key=keys_dct["Twitter API Key"], consumer_secret=keys_dct["Twitter API Key Secret"],
    access_token=keys_dct["Twitter Access Token"], access_token_secret=keys_dct["Twitter Access Token Secret"],
)
lol_watcher = LolWatcher(keys_dct["Riot API Key"])

tier_dct = {
    "Iron IV":0,
    "Iron III":1,
    "Iron II":2,
    "Iron I":3,
    "Bronze IV":4,
    "Bronze III":5,
    "Bronze II":6,
    "Bronze I":7,
    "Silver IV":8,
    "Silver III":9,
    "Silver II":10,
    "Silver I":11,
    "Gold IV":12,
    "Gold III":13,
    "Gold II":14,
    "Gold I":15,
    "Platinum IV":16,
    "Platinum III":17,
    "Platinum II":18,
    "Platinum I":19,
    "Diamond IV":20,
    "Diamond III":21,
    "Diamond II":22,
    "Diamond I":23,
    "Master":24,
    "Grandmaster":25,
    "Challenger":26,
}

def SummonerToRankedStats(summonernames_list):
    summoner_details = [lol_watcher.summoner.by_name("euw1", summoner_name) for summoner_name in summonernames_list]
    account_ids = [summoner["id"] for summoner in summoner_details]

    account_league_details = [lol_watcher.league.by_summoner("euw1", account_id) for account_id in account_ids]
    return account_league_details

def getStatsToDct(account_league_details):
    dctRankedStats = {
        "tier_current":[],
        "games_played":[],
        "games_won":[],
        "games_lost":[],
    }
    
    for league in account_league_details:
        for entry in league:
            if entry["queueType"] == "RANKED_SOLO_5x5":
                try:
                    tier_rank = entry["tier"].title() + " " + entry["rank"]
                    dctRankedStats["tier_current"].append(tier_dct[tier_rank])
                    dctRankedStats["games_played"].append(entry["wins"]+entry["losses"])
                    dctRankedStats["games_won"].append(entry["wins"])
                    dctRankedStats["games_lost"].append(entry["losses"])
                except KeyError:
                    pass
    return dctRankedStats

summonernames_list = ["UEM IKnockYou", "UEM ADC", "AppleDJ", "CarryMachine", "Sascha the Exile"]
# summonernames_list = ["CV Bendixx", ]
target_tier = "Diamond IV"

account_league_details = SummonerToRankedStats(summonernames_list)
dctRankedStats = getStatsToDct(account_league_details)

current_tier = max(dctRankedStats["tier_current"])
current_rank = list(tier_dct.keys())[list(tier_dct.values()).index(max(dctRankedStats["tier_current"]))]
games_played = sum(dctRankedStats["games_played"])
games_won = sum(dctRankedStats["games_won"])
games_lost = sum(dctRankedStats["games_lost"])
winrate = round((games_won/games_played)*100,2)

last_timestamp = last_tweet[-1]
games_won_change = games_won - last_tweet[1]
games_lost_change = games_lost - last_tweet[2]
games_played_change = games_played - last_tweet[0]
winrate_change = winrate - last_tweet[-2]
sign = "+" if winrate_change > 0 else ("-" if winrate_change < 0 else "+/-")

timestamp = datetime.now().strftime("%d.%m.%y %H:%M")

tweet_txt =f"""
{"Ja" if current_tier >= tier_dct[target_tier] else "Nein"}

Current Highest Rank: {current_rank}

{games_played} Games Played ({games_won} W / {games_lost} L)

{winrate:4.02f}% Winrate Across {len(summonernames_list)} Accounts

{games_played_change} ({games_won_change} W / {games_lost_change} L) Games Played Since Last Update ({last_timestamp})

{timestamp}
"""

last_tweet = [games_played, games_won, games_lost, winrate, timestamp]
with open(f"{file_path}\mypicklejar", "wb") as f:
    pickle.dump(last_tweet, f)

# client.create_tweet(text=tweet_txt)
print(tweet_txt)
