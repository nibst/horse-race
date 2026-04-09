
import pickle
from get_horse_data import get_all_races_since, get_race_data
from prediction.winner_predictor import WinnerPredictor
from prediction.race_preprocessor import RacePreprocessor

def main():
    #GET horses infos
    #TRAIN some model
    #PROFIT?
    date = "01/11/2023"
    
    #races = get_all_races_since(date)
    safe_date = date.replace("/","-")
    # with open(f"./data/races_since_{safe_date}", "wb") as f:
        # pickle.dump(races,f)
    with open(f"./data/races_since_{safe_date}", "rb") as f:
        races = pickle.load(f)
    test_race = None
    for i, race in enumerate(races):
        if race.date == "26/3/2026":
            test_race = race
            races.pop(i)
    for race in races:
        print("Data: " + race.date)
        for match in race.matches:
            if not match.results:
                continue
            print(match.id)
            print(match.sequence_number)
            print(*match.results, sep="\n")
            print("------------")
    preprocessor = RacePreprocessor()
    predictor = WinnerPredictor(preprocessor)
    predictor.train(races)
    if not test_race:
        return
    match = test_race.matches[3]
    predictions = predictor.predict_match(match)
    print("TEST MATCH")
    print(match.id)
    print(match.sequence_number)
    print(*match.results, sep="\n")
    print("------------")
    print(predictions)
main()
