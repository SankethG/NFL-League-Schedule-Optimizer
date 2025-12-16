import random
import math
from collections import defaultdict
from data_class import Team, ScheduledGame

def simulate_game(team1, team2, is_neutral_site=False, seed=None, noise_scale=0.05):
    """
    This method simulates a single game between two teams based on their strength ratings.
    The probability of team1 winning is based on the strength differential, with a
    small boost for home field advantage and then I add a small element of noise(bc upsets do happen ocassionally)
    It returns the winning team at end, so either team 1 or team 2
    """
    if seed is not None:
        random.seed(seed)
        
    # Home field advantage boost, arbitrary/custom value I put
    home_advantage = 0.03 if not is_neutral_site else 0.0
    
    # Calculate the strength difference between teams
    strength_diff = (team1.strength + home_advantage) - team2.strength
    
    # Add some random noise to make games not direct bc upsets happen, need to reflect this
    noise = random.gauss(0, noise_scale)
    strength_diff += noise

     #Use a logistic function to convert strength difference to win probability
    # After experimenting a bit, the factor of 10 makes the curve steep enough to be the most realistic for nfl games
    win_prob_team1 = 1 / (1 + math.exp(-10 * strength_diff))
    
    
    # basically rolling a number to see who wins based on prob value above
    if random.random() < win_prob_team1:
        return team1
    else:
        return team2


def simulate_season(schedule, teams, seed=None):
    """
    Simulates the entire regular season and returns team records.
    It gives the team records in the form  of a dictionary like: {team_name: {'wins': int, 'losses': int, 'team': Team}}
    """
    if seed is not None:
        random.seed(seed)
    
    records = {}
    for team in teams:
        records[team.name] = {
            'wins': 0,
            'losses': 0,
            'team': team
        }
    
    # Simulate every game in the schedule
    game_counter = 0
    for week_num, games in schedule.items():
        for game in games:
            home_team = game.home
            away_team = game.away
            
            # Each game gets its own seed so results are consistent but different
            game_seed = seed + game_counter if seed is not None else None
            winner = simulate_game(home_team, away_team, is_neutral_site=False, seed=game_seed)
            
             # Update win/loss records based on who won and who lost
            if winner.name == home_team.name:
                records[home_team.name]['wins'] += 1
                records[away_team.name]['losses'] += 1
            else:
                records[away_team.name]['wins'] += 1
                records[home_team.name]['losses'] += 1
            
            game_counter += 1
    
    return records

def determine_playoff_teams(records, conference):
    """
    Determines the 7 playoff teams for a given conference using NFL playoff rules, which are:
    - 4 division winners, so the best record in each division gets a spot in the playoffs
    - 3 wild card teams, which determined by the next 3 best records in that conference
    - in the end it returns list of 7 teams seeded 1-7, which is final playoff seeding
    """
    
    # Group teams by division within the conference
    divisions = defaultdict(list)
    for team_name, record in records.items():
        team = record['team']
        if team.conference == conference:
            divisions[team.division].append({
                'team': team,
                'wins': record['wins'],
                'losses': record['losses']
            })
    
    # Find the winner of each division
    # Sort by wins first, then by team strength as tiebreaker
    division_winners = []
    for division, teams_in_div in divisions.items():
        teams_in_div.sort(key=lambda x: (x['wins'], x['team'].strength), reverse=True)
        division_winners.append(teams_in_div[0])
    # Sort division winners by record to establish initial seeding (seeds 1-4)
    division_winners.sort(key=lambda x: (x['wins'], x['team'].strength), reverse=True)
    
    # Get all teams in this conference for wild card selection
    all_teams = []
    for team_name, record in records.items():
        team = record['team']
        if team.conference == conference:
            all_teams.append({
                'team': team,
                'wins': record['wins'],
                'losses': record['losses']
            })
    
    division_winner_names = {dw['team'].name for dw in division_winners}
    # Wild card pool is everyone except the division winners
    wild_card_pool = [t for t in all_teams if t['team'].name not in division_winner_names]
    # Take the top 3 non-division winners as wild cards (seeds 5-7)
    wild_card_pool.sort(key=lambda x: (x['wins'], x['team'].strength), reverse=True)
    wild_card_teams = wild_card_pool[:3]
    # Combine and sort again to get final seeding 1-7
    playoff_teams = division_winners + wild_card_teams
    playoff_teams.sort(key=lambda x: (x['wins'], x['team'].strength), reverse=True)
    
    return [t['team'] for t in playoff_teams]

def simulate_playoffs(afc_teams, nfc_teams, seed=None):
    """
    Simulates the NFL playoffs with the current format:
    - Wild Card Round: #7 with #2, #6 with #3, #5 with #4 x2 bc for each conference
    - Divisional Round: lowest seed plays #1, other winner will play higher remaining seed
    - Conference Championships
    - Super Bowl usually some random neutral site
    
    Returns dictionary with results of each round and Super Bowl champion
    """
    if seed is not None:
        random.seed(seed)
    
    results = {
        'wild_card': {'AFC': [], 'NFC': []},
        'divisional': {'AFC': [], 'NFC': []},
        'conference': {'AFC': None, 'NFC': None},
        'super_bowl': None
    }
    
    game_counter = 0
    
    # Run playoffs for both conferences
    for conf, teams in [('AFC', afc_teams), ('NFC', nfc_teams)]:

        # Wild Card Round, so three games per conference 7 plays 2, 6 plays 3, 5 plays 4, latter team is home team
        
        game_seed = seed + game_counter if seed is not None else None
        winner1 = simulate_game(teams[1], teams[6], seed=game_seed)
        results['wild_card'][conf].append(f"{teams[6].name} @ {teams[1].name} → {winner1.name} wins")
        game_counter += 1
        
        game_seed = seed + game_counter if seed is not None else None
        winner2 = simulate_game(teams[2], teams[5], seed=game_seed)
        results['wild_card'][conf].append(f"{teams[5].name} @ {teams[2].name} → {winner2.name} wins")
        game_counter += 1
        
        game_seed = seed + game_counter if seed is not None else None
        winner3 = simulate_game(teams[3], teams[4], seed=game_seed)
        results['wild_card'][conf].append(f"{teams[4].name} @ {teams[3].name} → {winner3.name} wins")
        game_counter += 1
        
        # Figure out which teams won and what their original seeds were
        wild_card_winners = []
        for winner in [winner1, winner2, winner3]:
            original_seed = teams.index(winner)
            wild_card_winners.append((winner, original_seed))
        
        # Sort winners by seed, so lowest seed number = higher seed
        wild_card_winners.sort(key=lambda x: x[1])
        
        # divisional Round so two games per conference, and the lowest remaining seed plays the #1 seed who had a bye
        #during wild card round 
        lowest_seed_team, _ = wild_card_winners[0]
        game_seed = seed + game_counter if seed is not None else None
        div_winner1 = simulate_game(teams[0], lowest_seed_team, seed=game_seed)
        results['divisional'][conf].append(f"{lowest_seed_team.name} @ {teams[0].name} → {div_winner1.name} wins")
        game_counter += 1
        
        # The other two wild card winners play each other, the higher seed hosts at their home stadium
        middle_seed_team, middle_seed = wild_card_winners[1]
        highest_seed_team, highest_seed = wild_card_winners[2]
        game_seed = seed + game_counter if seed is not None else None
        div_winner2 = simulate_game(highest_seed_team, middle_seed_team, seed=game_seed)
        results['divisional'][conf].append(f"{middle_seed_team.name} @ {highest_seed_team.name} → {div_winner2.name} wins")
        game_counter += 1
    
        # conference champisionship so the higher seed host, need to find the seeds of our two remaining teams
        div_w1_seed = teams.index(div_winner1) if div_winner1 in teams else 10
        div_w2_seed = teams.index(div_winner2) if div_winner2 in teams else 10
        
        if div_w1_seed < div_w2_seed:
            home_team, away_team = div_winner1, div_winner2
        else:
            home_team, away_team = div_winner2, div_winner1
        
        game_seed = seed + game_counter if seed is not None else None
        conf_champ = simulate_game(home_team, away_team, seed=game_seed)
        results['conference'][conf] = f"{away_team.name} @ {home_team.name} → {conf_champ.name} wins"
        game_counter += 1
        
        if conf == 'AFC':
            afc_champ = conf_champ
        else:
            nfc_champ = conf_champ
    
    # Super Bowl, which is played at some neutral site
    game_seed = seed + game_counter if seed is not None else None
    sb_winner = simulate_game(afc_champ, nfc_champ, is_neutral_site=True, seed=game_seed)
    results['super_bowl'] = f"{afc_champ.name} vs {nfc_champ.name} → {sb_winner.name} wins Super Bowl!"
    results['champion'] = sb_winner
    
    return results

def full_season_playoff_simulation(schedule, teams, seed=None):
    """
    Runs a full simulation of the season, which includes the regular season + playoffs
    
    Returns:
    - records: regular season records
    - afc_playoff_teams: 7 AFC playoff teams
    - nfc_playoff_teams: 7 NFC playoff teams
    - playoff_results: results of all playoff rounds
    """
    
    # Simulate all 18 weeks of regular season
    records = simulate_season(schedule, teams, seed=seed)
    
    
    # Determine which 7 teams from each conference make the playoffs
    afc_playoff_teams = determine_playoff_teams(records, 'AFC')
    nfc_playoff_teams = determine_playoff_teams(records, 'NFC')
    
    #simulates the playoffs with a different seed to add variety
    # Adding 1000 to our seed lets it so that playoff randomness is independent from regular season, we want uncorrelated randomness here
    playoff_seed = (seed + 1000) if seed is not None else None
    playoff_results = simulate_playoffs(afc_playoff_teams, nfc_playoff_teams, seed=playoff_seed)
    
    return records, afc_playoff_teams, nfc_playoff_teams, playoff_results