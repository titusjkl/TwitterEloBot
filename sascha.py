# import config as cfg
from riotwatcher import LolWatcher

lol_watcher = LolWatcher(cfg.riot_api_key)

account_names = ["UEMIKnockYou","AppleDJ","UEM ADC",]

summoner_names = [lol_watcher.summoner.by_name("euw1", summoner_name) for summoner_name in account_names]
account_puuids = [summoner["puuid"] for summoner in summoner_names]
account_ids = [summoner["id"] for summoner in summoner_names]
account_leagues = [lol_watcher.league.by_summoner("euw1", account_id) for account_id in account_ids]

dict_rank = {
    "I":1,
    "II":2,
    "III":3,
    "IV":4,
}

dict_queuetype = {
    "RANKED_SOLO_5x5":"Solo Queue",
    "RANKED_FLEX_SR":"Flex Queue",
}

target_tier = ["Diamond", "Master", "Grandmaster", "Challenger"]

total_games_solo = 0
total_games_flex = 0

for league in account_leagues:
    for entry in league:
        if entry["queueType"] == "RANKED_SOLO_5x5": # or "RANKED_FLEX_SR":
            try:
                queuetype = dict_queuetype[entry["queueType"]]
                tier = entry["tier"].title()
                rank = dict_rank[entry["rank"]]
                total_games = entry["wins"] + entry["losses"]

                print(entry["summonerName"])
                print("\t", queuetype, tier, rank)
                print("\t", round(entry["wins"]/total_games,2), total_games)

                if queuetype == "Solo Queue":
                    total_games_solo += total_games
                elif queuetype == "Flex Queue":
                    total_games_flex += total_games

            except KeyError:
                pass

print(total_games_solo)
print(total_games_flex)
