import requests
import json
from enum import Enum
import time
import os
from datetime import datetime, timedelta, date
from pytz import timezone
import random
import logging
import pytz

from . import settings

log = logging.getLogger(__name__)

with open('flags.json') as fd:
    FLAGS = json.load(fd)

WC_COMPETITION = '17' # 17 for only WC matches

FIFA_URL = 'https://api.fifa.com/api/v3'
NOW_URL = '/live/football/now'
MATCH_URL = '/timelines/{}/{}/{}/{}?language=en-US' # IdCompetition/IdSeason/IdStage/IdMatch
DAILY_URL = '/calendar/matches?from={}Z&to={}Z&idCompetition={}&language=en-US'
PLAYER_URL = ''
TEAM_URL = '/teamform/'

class EventType(Enum):
    GOAL_SCORED = 0
    UNKNOWN_1 = 1
    YELLOW_CARD = 2
    RED_CARD = 3
    DOUBLE_YELLOW = 4
    SUBSTITUTION = 5
    IGNORE = 6
    MATCH_START = 7
    HALF_END = 8
    ATTEMPT_SHOT = 12
    FOUL_UNKNOWN = 14
    UNKNOWN_13 = 13
    OFFSIDE = 15
    CORNER_KICK = 16
    BLOCKED_SHOT_2 = 17
    FOUL = 18
    UNKNOWN_19 = 19
    UNKNOWN_20 = 20
    UNKNOWN_22 = 22
    DROPPED_BALL = 23
    THROW_IN = 24
    CLEARANCE = 25
    MATCH_END = 26
    AERIAL_DUEL = 27
    UNKNOWN_29 = 29
    UNKNOWN_30 = 30
    CROSSBAR = 32
    CROSSBAR_2 = 33
    OWN_GOAL = 34
    HAND_BALL = 37
    FREE_KICK_GOAL = 39
    PENALTY_GOAL = 41
    FREE_KICK_CROSSBAR = 44
    UNKNOWN_51 = 51
    PENALTY_MISSED = 60
    PENALTY_MISSED_2 = 65
    VAR_REVIEW = 71
    VAR_PENALTY = 72
    UNKNOWN = 9999

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)

class Period(Enum):
    FIRST_PERIOD = 3
    SECOND_PERIOD = 5
    FIRST_EXTRA = 7
    SECOND_EXTRA = 9
    PENALTY_SHOOTOUT = 11

def get_daily_matches():
    daily_matches = ''
    now = datetime.now(timezone('US/Eastern'))
    start_time = now.strftime("%Y-%m-%dT%H:00:00")
    log.debug(f"start_time is {start_time}")
    now = now + timedelta(days=1)
    end_time = now.strftime("%Y-%m-%dT00:00:00")
    log.debug(f"end_time is {end_time}")
    try:
        daily_url = FIFA_URL + DAILY_URL.format(start_time, end_time, WC_COMPETITION)
        r = requests.get(daily_url)
        r.raise_for_status()
    except r.exceptions.HTTPError as ex:
        log.warn('Failed to get list of daily matches.\n{}'.format(ex))
        return daily_matches

    if len(r.json()['Results']) > 0:
        daily_matches = '*Todays Matches:*\n'
    for match in r.json()['Results']:
        #log.debug("time stamp")
        qatar_timezone = pytz.timezone("Asia/Qatar")
        local_timezone = pytz.timezone("America/New_York")
        #log.debug(f"qatar_timezone {qatar_timezone}")
        #log.debug(f"local_timezone {local_timezone}")
        
        date_start = datetime.strptime(match['LocalDate'], "%Y-%m-%dT%H:%M:%SZ")
        #log.debug(f"date_start {date_start}")

        localized_timestamp = qatar_timezone.localize(date_start)
        new_timezone_timestamp = localized_timestamp.astimezone(local_timezone)
        #log.debug("time stamp1")
        date_start_local = new_timezone_timestamp.astimezone(settings.TIMEZONE)
        #log.debug(f"qatar timestamp {localized_timestamp}")
        #log.debug(f"here timestamp {new_timezone_timestamp}")
        date_start_str = date_start_local.strftime("%A, %b %d at %I:%M%p %Z")

        home_team = match['Home']
        home_team_id = home_team['IdCountry']
        home_team_flag = ''
        if home_team_id in FLAGS.keys():
            home_team_flag = FLAGS[home_team_id]

        away_team = match['Away']
        away_team_flag = ''
        away_team_id = away_team['IdCountry']
        if away_team_id in FLAGS.keys():
            away_team_flag = FLAGS[away_team_id]

        daily_matches += '{} {} vs {} {} || {}\n'.format(home_team_flag, home_team['TeamName'][0]['Description'], away_team['TeamName'][0]['Description'], away_team_flag, date_start_str)
    return daily_matches

def get_current_matches():
    log.debug("get_current_matches")

    matches = []
    players = {}
    headers = {'Content-Type': 'application/json'}
    try:
        r = requests.get(url=FIFA_URL + NOW_URL, headers=headers)
        r.raise_for_status()
    except requests.exceptions.HTTPError as ex:
        return matches, players

    for match in r.json()['Results']:
        id_competition = match['IdCompetition']
        if WC_COMPETITION and WC_COMPETITION != id_competition:
            continue
        id_season = match['IdSeason']
        id_stage = match['IdStage']
        id_match = match['IdMatch']
        home_team_id = match['HomeTeam']['IdTeam']
        for entry in match['HomeTeam']['TeamName']:
            home_team_name = entry['Description']
        away_team_id = match['AwayTeam']['IdTeam']
        for entry in match['AwayTeam']['TeamName']:
            away_team_name = entry['Description']
        if not id_competition or not id_season or not id_stage or not id_match:
            log.warn('Invalid match information')
            continue

        matches.append({'idCompetition': id_competition, 'idSeason': id_season, 'idStage': id_stage, 'idMatch': id_match, 'homeTeamId': home_team_id,
        'homeTeam': home_team_name, 'awayTeamId': away_team_id, 'awayTeam': away_team_name, 'events': []})

        for player in match['HomeTeam']['Players']:
            player_id = player['IdPlayer']
            for player_details in player['ShortName']:
                player_name = player_details['Description']
            players[player_id] = player_name

        for player in match['AwayTeam']['Players']:
            player_id = player['IdPlayer']
            for player_details in player['ShortName']:
                player_name = player_details['Description']
            players[player_id] = player_name

    return matches, players

def get_match_events(idCompetition, idSeason, idStage, idMatch):
    log.debug("get_match_events")

    events = {}
    headers = {'Content-Type': 'application/json'}
    match_url = FIFA_URL + MATCH_URL.format(idCompetition, idSeason, idStage, idMatch)
    try:
        r = requests.get(match_url, headers=headers)
        r.raise_for_status()
        log.debug("After request")
    except requests.exceptions.HTTPError as ex:
        return events
    log.debug(f"Events {r.json()['Event']}")
    for event in r.json()['Event']:
        log.debug(f"Event {event}")
        eId = event['EventId']
        log.debug(eId)
        new_event = {}
        new_event['type'] = event['Type']
        log.debug(f"Event type == {new_event['type']}")
        new_event['team'] = event.get('IdTeam', '')
        log.debug(new_event['team'])
        new_event['player'] = event.get('IdPlayer', '')
        log.debug(new_event['player'])
        new_event['time'] = event['MatchMinute']
        log.debug(new_event['time'])
        new_event['home_goal'] = event['HomeGoals']
        log.debug(f"home_goal == {new_event['home_goal']}")
        new_event['away_goal'] = event['AwayGoals']
        log.debug(f"away_goal == {new_event['away_goal']}")
        new_event['sub'] = event.get('IdSubPlayer', '')
        log.debug(new_event['sub'])
        new_event['period'] = event['Period']
        log.debug(f"Period = {new_event['period']}")
        new_event['home_pgoals'] = event['HomePenaltyGoals']
        log.debug(f"Home_pgoals == {new_event['home_pgoals']}")
        new_event['away_pgoals'] = event['AwayPenaltyGoals']
        log.debug(f"Away_pgoals == {new_event['away_pgoals']}")
        new_event['event_description'] = event['EventDescription'][0]['Description'] if len(event.get('EventDescription', [])) > 0 else 'NA'        
        log.debug(f"event_description == {new_event['event_description']}")
        new_event['url'] = match_url
        log.debug(match_url)
        events[eId] = new_event 
    log.debug("Return events")
    return events

def build_event(player_list, current_match, event):
    log.debug("Inside: build_event")
    log.debug(f"Current_match is {current_match}")
    log.debug(f"Event is {event}")

    is_debug = False
    event_message = ''
    player = player_list.get(event['player'], '')
    sub_player = player_list.get(event['sub'], '')
    active_team = current_match['homeTeam'] if event['team'] == current_match['homeTeamId'] else current_match['awayTeam']
    active_team_id = current_match['homeTeamId'] if event['team'] == current_match['homeTeamId'] else current_match['awayTeamId']
   
    log.debug(f"active_team is {active_team}")
    log.debug(f"event_team is {event['team']}")

    try:
        log.debug(f"Before active_team_url")
        active_team_url = FIFA_URL + TEAM_URL + active_team_id + "?count=1&language=en"
        log.debug(f"active_team_url == {active_team_url}")
        r = requests.get(active_team_url)
        r.raise_for_status()
        active_team_code = r.json()['IdCountry']
        active_team_flag = ''
        if active_team_code in FLAGS.keys():
            active_team_flag = FLAGS[active_team_code]
            log.debug(f"active_team_flag is {active_team_flag}")
    except r.exceptions as ex:
        log.warn('Failed to home get active info.\n{}'.format(ex))

    try:
        log.debug(f"Before home_team_url")
        home_team_url = FIFA_URL + TEAM_URL + current_match['homeTeamId'] + "?count=1&language=en"
        log.debug(f"home_team_url == {home_team_url}")
        r = requests.get(home_team_url)
        r.raise_for_status()
        home_team_code = r.json()['IdCountry']
        home_team_flag = ''
        if home_team_code in FLAGS.keys():
            home_team_flag = FLAGS[home_team_code]
            log.debug(f"home_team_flag is {home_team_flag}")
    except r.exceptions as ex:
        log.warn('Failed to home get team info.\n{}'.format(ex))

    try:
        log.debug(f"Before away_team_url")
        away_team_url = FIFA_URL + TEAM_URL + current_match['awayTeamId'] + "?count=1&language=en"
        log.debug(f"away_team_url == {away_team_url}")
        r = requests.get(away_team_url)
        r.raise_for_status()
        away_team_code = r.json()['IdCountry']
        if away_team_code in FLAGS.keys():
            away_team_flag = FLAGS[away_team_code]
            log.debug(f"away_team_flag is {away_team_flag}")
    except r.exceptions as ex:
        log.warn('Failed to get away team info.\n{}'.format(ex))

    extraInfo = False
    if (event['type'] == EventType.GOAL_SCORED.value or event['type'] == EventType.FREE_KICK_GOAL.value
        or event['type'] == EventType.FREE_KICK_GOAL.value):
        num_o = random.randint(3, 12)
        event_message = ':soccer: {} G{}AL! {}{} *{}:{}* {}{}'.format(event['time'], "O"*num_o, current_match['homeTeam'],home_team_flag, event['home_goal'], event['away_goal'], current_match['awayTeam'],away_team_flag)
        extraInfo = True
    elif event['type'] == EventType.YELLOW_CARD.value:
        event_message = ':yellow_card: {} Yellow card.'.format(event['time'])
        extraInfo = True
    elif event['type'] == EventType.RED_CARD.value:
        event_message = ':red_card: {} Red card.'.format(event['time'])
        extraInfo = True
    elif event['type'] == EventType.DOUBLE_YELLOW.value:
        event_message = ':yellow_card: :red_card: {} Second yellow card.'.format(event['time'])
        extraInfo = True
    elif event['type'] == EventType.FOUL.value:
        event_message = ':angryoldman: {} FOUL! {}'.format(event['time'],active_team_flag)
        event_message += '\n> {}'.format(event['event_description'])
    elif event['type'] == EventType.ATTEMPT_SHOT.value:
        event_message = ':shotsfired: {} Shot fired !! {}'.format(event['time'],active_team_flag)
        event_message += '\n> {}'.format(event['event_description'])
    elif event['type'] == EventType.SUBSTITUTION.value:
        event_message = ':arrows_counterclockwise: {} Substitution for {}{}.'.format(event['time'], active_team,active_team_flag)
        if player and sub_player:
            event_message += '\n> {} comes on for {}.'.format(player, sub_player)
    elif event['type'] == EventType.MATCH_START.value:
        log.debug("Entering MATCH_START")
        period = None
        if event['period'] == Period.FIRST_PERIOD.value:
            event_message = ':clock12: The match between {}{} and {}{} has begun!'.format(current_match['homeTeam'], home_team_flag, current_match['awayTeam'],away_team_flag)
        elif event['period'] == Period.SECOND_PERIOD.value:
            event_message = ':clock12: The second half of the match between {}{} and {}{} has begun!'.format(current_match['homeTeam'],home_team_flag, current_match['awayTeam'],away_team_flag)
        elif event['period'] == Period.PENALTY_SHOOTOUT.value:
            event_message = ':clock12: The penalty shootout is starting between {}{} and {}{}!'.format(current_match['homeTeam'], home_team_flag,current_match['awayTeam'],away_team_flag)
        elif event['period'] == Period.FIRST_EXTRA.value:
            event_message = ':clock12: The first half of extra time is starting between {}{} and {}{}!'.format(current_match['homeTeam'], home_team_flag, current_match['awayTeam'],away_team_flag)
        elif event['period'] == Period.SECOND_EXTRA.value:
            event_message = ':clock12: The second half of extra time is starting between {}{} and {}{}!'.format(current_match['homeTeam'],home_team_flag, current_match['awayTeam'],away_team_flag)
        else:
            event_message = ':clock12: The match between {}{} and {}{} is starting again!'.format(current_match['homeTeam'],home_team_flag, current_match['awayTeam'],away_team_flag)
    elif event['type'] == EventType.HALF_END.value:
        period = None
        if event['period'] == Period.FIRST_PERIOD.value:
            period = 'first'
        elif event['period'] == Period.SECOND_PERIOD.value:
            period = 'second'
        elif event['period'] == Period.PENALTY_SHOOTOUT.value:
            event_message = ':clock1230: The penalty shootout is over.'
        elif event['period'] == Period.FIRST_EXTRA.value:
            period = 'first extra'
        elif event['period'] == Period.SECOND_EXTRA.value:
            period = 'second extra'
        else:
            period = 'invalid'
            event_message = ':clock1230: End of the half. {}{} *{}:{}* {}{}.'.format(current_match['homeTeam'], home_team_flag, event['home_goal'], event['away_goal'], current_match['awayTeam'],away_team_flag)
        if period is not None:
            event_message = ':clock1230: End of the {} half. {}{} *{}:{}* {}{}.'.format(period, current_match['homeTeam'],home_team_flag, event['home_goal'], event['away_goal'], current_match['awayTeam'],away_team_flag)
    elif event['type'] == EventType.MATCH_END.value:
        event_message = ':clock12: The match between {}{} and {}{} has ended. {}{} *{}:{}* {}{}.'.format(current_match['homeTeam'],home_team_flag, current_match['awayTeam'],away_team_flag,
        current_match['homeTeam'],home_team_flag, event['home_goal'], event['away_goal'], current_match['awayTeam'],away_team_flag)
    elif event['type'] == EventType.OWN_GOAL.value:
        event_message = ':soccer: {} Own Goal! {}{} *{}:{}* {}{}'.format(event['time'], current_match['homeTeam'],home_team_flag, event['home_goal'], event['away_goal'], current_match['awayTeam'],away_team_flag)
        extraInfo = True
    elif event['type'] == EventType.PENALTY_GOAL.value:
        log.debug(f"inside Penalty Goal")
        if event['period'] == Period.PENALTY_SHOOTOUT.value:
            event_message = ':soccer: Penalty goal! {}{} *{} ({}):{} ({})* {}{}'.format(current_match['homeTeam'],home_team_flag, event['home_goal'], event['home_pgoals'], event['away_goal'], event['away_pgoals'], current_match['awayTeam'],away_team_flag)
        else:
            log.debug(f"inside Penalty Goal else")
            event_message = ':soccer: {} Penalty goal! {}{} *{}:{}* {}{}'.format(event['time'], current_match['homeTeam'], home_team_flag, event['home_goal'], event['away_goal'], current_match['awayTeam'],away_team_flag)
        extraInfo = True
    elif event['type'] == EventType.PENALTY_MISSED.value or event['type'] == EventType.PENALTY_MISSED_2.value:
        if event['period'] == Period.PENALTY_SHOOTOUT.value:
            event_message = ':no_entry_sign: Penalty missed! {}{} *{} ({}):{} ({})* {}{}'.format(current_match['homeTeam'],home_team_flag, event['home_goal'], event['home_pgoals'], event['away_goal'], event['away_pgoals'], current_match['awayTeam'],away_team_flag)
        else:
            event_message = ':no_entry_sign: {} Penalty missed!'.format(event['time'])
        extraInfo = True
    elif event['type'] == EventType.VAR_REVIEW.value:
         log.debug(f"Inside VAR Review")
         event_message = ':referee: :looking: VAR! {}'.format(event['event_description'])
    elif event['type'] == EventType.OFFSIDE.value:
        event_message = ':raising_hand::runner: {} OFFSIDE! {}'.format(event['time'],active_team_flag)
        event_message += '\n> {}'.format(event['event_description'])
    elif EventType.has_value(event['type']):
        event_message = None
    elif DEBUG:
        event_message = 'Missing event information for {}{} vs {}{}: Event {}\n{}'.format(current_match['homeTeam'],home_team_flag, current_match['awayTeam'],away_team_flag,event['type'], event['url'])
        is_debug = True
    else:
        log.debug("build_event Else")
        event_message = None

    if (extraInfo):
        if player and active_team:
            event_message += '\n> {} ({}{})'.format(player, active_team,active_team_flag)
        elif active_team:
            event_message += '\n> {}{}'.format(active_team,active_team_flag)

    if event_message:
        log.debug('Sending event: {}'.format(event_message))
        return {'message': event_message, 'debug': is_debug}
    else:
        return None

def save_last_daily_matches_sent():
    dt = datetime.now()
    with open('daily_matches.txt', 'w') as file:
        file.write(dt.date().isoformat())
    return

def should_send_daily_matches():
    if settings.ONLY_SEND_DAILY_MATCHES_ONCE:
        if not os.path.isfile('daily_matches.txt'):
            return False
        with open('daily_matches.txt', 'r') as file:
            content = file.read().strip()

        last_sent = date.fromisoformat(content)
        now = datetime.now().date()
        log.debug(f"last_sent == {last_sent}")
        log.debug(f"now == {now}")
        return now - last_sent >= timedelta(days=1)
    else:
        last_sent_daily = (datetime.now() - timedelta(days=1)).timetuple().tm_yday
        if (last_sent_daily < datetime.now().timetuple().tm_yday):
            last_sent_daily = datetime.now().timetuple().tm_yday
            return True
        else:
            return False

def save_matches(match_list):
    with open('match_list.txt', 'w') as file:
        file.write(json.dumps(match_list))

def load_matches():
    if not os.path.isfile('match_list.txt'):
        return {}
    with open('match_list.txt', 'r') as file:
        content = file.read()
    return json.loads(content) if content else {}


def check_for_updates():
    events = []
    match_list = load_matches()
    player_list = {}
    live_matches, players = get_current_matches()
    for match in live_matches:
        if not match['idMatch'] in match_list:
            match_list[match['idMatch']] = match

    for player in players:
        if not player in player_list:
            player_list[player] = players[player]

    done_matches = []
    for match in match_list:
        current_match = match_list[match]
        event_list = get_match_events(current_match['idCompetition'], current_match['idSeason'], current_match['idStage'], current_match['idMatch'])
        for event in event_list:
            if event in current_match['events']:
                log.debug("Skipping event already reported")
                continue # We already reported the event, skip it
            log.debug("Before event_notification")
            event_notification = build_event(player_list, current_match, event_list[event])
            log.debug("After event_notification")
            current_match['events'].append(event)
            log.debug("After current_match")
            if event_notification:
                log.debug("Inside event_notification")
                events.append(event_notification)
            if event_list[event]['type'] == EventType.MATCH_END.value:
                done_matches.append(match)
            log.debug("Done with event within event_list")
        log.debug("Done with event_list")

    for match in done_matches:
        del match_list[match]

    save_matches(match_list)
    return events
