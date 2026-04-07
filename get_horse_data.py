from bs4 import BeautifulSoup
from bs4.element import PageElement, Tag
import re
import datetime
import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from domain.horse_result import HorseResult
from domain.race import Race
from domain.match import Match
from typing import List

HORSE_RESULTS_URL = "https://www.jockeyrs.com.br/resultados/"
HORSE_MATCH_ENDPOINT = "https://www.jockeyrs.com.br/resultados/consultaCompetidor.php?pareo="
HORSE_RACE_DAY_ENDPOINT = "https://www.jockeyrs.com.br/resultados/consultaReuniao.php?dia="  # dd/mm/yyyy
HORSE_INFO_ENDPOINT = "https://www.jockeyrs.com.br/resultados/consultaPerformance.php?nome="

horse_info_cache = {}
_cache_lock = threading.Lock()

# for now these two do the same thing, but may change based on jockey website changes
def parse_header(text):
    """just grab the number in the text"""
    match = re.search(r"\d+", text)
    return int(match.group()) if match else 0

def parse_placement(text):
    """just grab the number in the text"""
    match = re.search(r"\d+", text)
    return int(match.group()) if match else 0

def parse_age(text):
    """just grab the number in the text"""
    match = re.search(r"\d+", text)
    return int(match.group()) if match else 0

def get_matches(date) -> List[Match]:
    """Get all matches data from a certain date — parallelized across match IDs.

    Parameters
    ----------
    date: The date in which it will retrieve its matches

    Returns
    ---------
        a list of all matches
    """
    ids = get_matches_id(date)
    if not ids:
        return []

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(get_match_data, match_id): match_id for match_id in ids}
        results = []
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                results.append(result)
    return results

def get_matches_id(date: str):
    html = requests.get(HORSE_RACE_DAY_ENDPOINT + date).content
    soup = BeautifulSoup(html, "html.parser")
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
    soup = BeautifulSoup(match_html, "html.parser")
    header = soup.find("thead")
    sequence_number = -1
    if header:
        sequence_number = parse_header(header.get_text(strip=True))
    table = soup.find("tbody", class_="corpadraoLet")
    if not isinstance(table, Tag):
        print("Soup fucked up")
        return None
    results = []
    for row in table.find_all("tr"):
        results.append(get_horse_result(row))
    return Match(id=match_id, sequence_number=sequence_number, results=results)


def get_horse_result(row):
    cells = [td.get_text(strip=True) for td in row.find_all("td")]
    info = get_horse_info(cells[1])
    return HorseResult(
        placement=parse_placement(cells[0]),
        name=cells[1],
        trainer=cells[2],
        jockey=cells[3],
        owner=cells[4],
        breeder=cells[5],
        weight=float(cells[6]) if cells[6] else 0.0,
        odds=float(cells[7]) if cells[7] else 0.0,
        sex=info.get("Sexo", ""),
        age=info.get("Idade", 0),
    )

def get_horse_info(horse_name: str):
    with _cache_lock:
        if horse_name in horse_info_cache:
            return horse_info_cache[horse_name]

    # Fetch outside the lock so other threads aren't blocked waiting
    horse_info_html = requests.get(f"{HORSE_INFO_ENDPOINT}{horse_name}").content
    soup = BeautifulSoup(horse_info_html, "html.parser")
    info_text = soup.find("h4").get_text()
    parts = [p.strip() for p in info_text.split("|")]
    info = {}
    for part in parts:
        if ":" in part:
            key, value = part.split(":", 1)
            info[key.strip()] = parse_age(value.strip())

    # Write to cache (thread-safe)
    with _cache_lock:
        horse_info_cache[horse_name] = info
    return info

def get_race_data(date: str):
    matches = get_matches(date)
    return Race(date=date, matches=matches)

def get_all_races_since(date):
    """
    Get race data for every thursday (race day)
    since the date parameter — parallelized across race dates.
    """
    thursday = 3  # on date.weekday() thursday is 3
    date = datetime.datetime.strptime(date, "%d/%m/%Y")
    print(date.weekday())

    # Collect all thursdays up front
    while date.weekday() != thursday:
        date += datetime.timedelta(days=1)

    dates = []
    while date < datetime.datetime.now():
        dates.append(f"{date.day}/{date.month}/{date.year}")
        date += datetime.timedelta(days=7)

    # Fetch all race dates in parallel
    # max_workers=10 is a reasonable starting point; lower if the site rate-limits you
    races = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(get_race_data, d): d for d in dates}
        for future in as_completed(futures):
            try:
                races.append(future.result())
            except Exception as e:
                print(f"Error fetching a race date: {e}")

    return races
