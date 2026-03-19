
import pickle
from get_horse_data import get_all_races_since, get_race_data

def main():
    #GET horses infos
    #TRAIN some model
    #PROFIT?
    date = "7/02/2026"
    
    races = get_all_races_since(date)
    safe_date = date.replace("/","-")
    with open(f"./races_since_{safe_date}", "wb") as f:
        pickle.dump(races,f)
    with open(f"races_since_{safe_date}", "rb") as f:
        races = pickle.load(f)
    # for race in races:
    #     print("Data: " + race.date)
    #     for match in race.matches:
    #         if not match.results:
    #             continue
    #         print(match.id)
    #         print(match.sequence_number)
    #         print(*match.results, sep="\n")
    #         print("------------")
main()
