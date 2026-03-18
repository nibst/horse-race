

from get_horse_data import get_all_races_since, get_race_data

def main():
    #GET horses infos
    #TRAIN some model
    #PROFIT?
    # race = get_race_data("12/03/2026")
    # print("Data: " + race.date)
    # for match in race.matches:
    #     if not match.results:
    #         continue
    #     print(match.id)
    #     print(match.sequence_number)
    #     print(*match.results, sep="\n")
    #     print("------------")
    #
    get_all_races_since("7/02/2026")
main()
