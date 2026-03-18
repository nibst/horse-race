from bs4 import BeautifulSoup
from bs4.element import PageElement, Tag
import re
import datetime
import requests
from horse_result import HorseResult
from race import Race
from match import Match
from typing import List
HORSE_RESULTS_URL = "https://www.jockeyrs.com.br/resultados/"
HORSE_MATCH_ENDPOINT = "https://www.jockeyrs.com.br/resultados/consultaCompetidor.php?pareo="
HORSE_RACE_DAY_ENDPOINT = "https://www.jockeyrs.com.br/resultados/consultaReuniao.php?dia=" #dd/mm/yyyy

#for now these two do the same thing, but may change based on jockey website changes
def parse_header(text):
    """just grab the number in the text"""
    match = re.search(r"\d+", text)
    return int(match.group()) if match else 0
def parse_placement(text):
    """just grab the number in the text"""
    match = re.search(r"\d+", text)
    return int(match.group()) if match else 0

def get_matches(date) -> List[Match] :
    """Get all matches data from a certain date
    Parameters
    ----------
    date: The date in which it will retrieve its matches
    
    Returns
    ---------
        a list of all matches
    """
    matches = []
    for match_id in get_matches_id(date):
        matches.append(get_match_data(match_id))
    return matches

def get_matches_id(date: str):
    html = requests.get(HORSE_RACE_DAY_ENDPOINT + date).content
    soup = BeautifulSoup(html,'html.parser')
    buttons = soup.find_all("button")
    if buttons is []:
        return []
    ids = []
    for button in buttons:
        if isinstance(button, Tag) and button.has_attr("value"):
            ids.append(button["value"])
    return ids

def get_match_data(match_id):
    match_html = requests.get(f"{HORSE_MATCH_ENDPOINT}{match_id}").content
    soup = BeautifulSoup(match_html,'html.parser')
    header = soup.find("thead") 
    sequence_number = -1
    if header:
        sequence_number = parse_header(header.get_text(strip=True)) 
    table = soup.find("tbody",class_="corpadraoLet")
    if not isinstance(table,Tag):
        print("Soup fucked up")
        return
    results = []
    for row in table.find_all("tr"):
        results.append(get_horse_result(row))
    return Match(id=match_id,sequence_number=sequence_number,results=results)

def get_horse_result(row):
    cells = [td.get_text(strip=True) for td in row.find_all("td")]
    return HorseResult(
            placement=parse_placement(cells[0]),
            name=cells[1],
            trainer=cells[2],
            jockey=cells[3],
            owner=cells[4],
            breeder=cells[5],
            weight=float(cells[6]) if cells[6] else 0.0,
            odds=float(cells[7]) if cells[7] else 0.0,
    )

def get_race_data(date):
    matches = get_matches(date)
    return Race(date=date,matches=matches)

def get_all_races_since(date):
    """
    get race data for every thursday (race day) 
    since the date parameter
    """
    thursday = 3 #on date.weekday() thursday is 3
    date = datetime.datetime.strptime(date,"%d/%m/%Y") 
    print(date.weekday())
    #get to the first thursday
    while(date.weekday() != 3):
        date += datetime.timedelta(days=1)
    while(date < datetime.datetime.now()):
        print(date)
        date += datetime.timedelta(days=7)
