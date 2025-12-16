import random
from data_class import Team, ScheduledGame
from schedule_core import compute_metrics, objective

def generate_swap_candidates(schedule, max_pairs=40, seed=0):
    """
    Given our initial schedule, we want to generate potential game swaps we can try to optimize it.
    
     We only consider swaps where the two games involve completely different teams
     because if we dont then we could end up with a team playing twice in the same week.
    
    Function returns a list of swap candidates in the format:
      (week1, game_index1, week2, game_index2)
    """
    random.seed(seed)
    
      # build a list of all games in the schedule by their (week, index) position
    all_games = []
    for week_number, games_this_week in schedule.items():
        for game_index in range(len(games_this_week)):
            all_games.append((week_number, game_index))

    possible_swaps = []
    already_tried = set() # track what we've already checked to avoid duplicates

    attempts = 0
    max_attempts = max_pairs * 10   # max tries to find valid swaps, saves time/computation

     #keep trying until we have enough valid swaps or run out of attempts
    while len(possible_swaps) < max_pairs and attempts < max_attempts:
        
        # pick two random games
        week1, index1 = random.choice(all_games)
        week2, index2 = random.choice(all_games)
        attempts += 1
        
        #make sure not swapping with itself
        if week1 == week2 and index1 == index2:
            continue
        
        # keep consistent permutation of order so we don't try the same swap twice in different orders
        if week1 > week2:
            week1, week2 = week2, week1
            index1, index2 = index2, index1
        
        swap_key = (week1, index1, week2, index2)
        
        #skip if we've already tried this swap
        if swap_key in already_tried:
            continue
        already_tried.add(swap_key)


        game1 = schedule[week1][index1]
        game2 = schedule[week2][index2]
        
        #Get the teams involved in each game
        teams_in_game1 = {game1.home.name, game1.away.name}
        teams_in_game2 = {game2.home.name, game2.away.name}
        
        
        # only allow the swap if the games have no teams in common
        # this stops a team from playing twice in the same week after swapping
        #looked up on google for ways to do this, .isdisjoint was given in stackoverflow
        #Link: https://stackoverflow.com/questions/45655936/how-to-test-all-items-of-a-list-are-disjoint
        
        if teams_in_game1.isdisjoint(teams_in_game2):
            possible_swaps.append((week1, index1, week2, index2))
            
    return possible_swaps

def swap_games(schedule, week1, index1, week2, index2):
    """
    Swaps two games in the schedule.
    
    We take the game at week1[index1] and swaps it with the game at week2[index2], 
    which modifies our schedule directly.
    """
    schedule[week1][index1], schedule[week2][index2] = schedule[week2][index2], schedule[week1][index1]

def optimize_schedule_backtracking(
    schedule, 
    teams, 
    base_debug, 
    travel_weight, 
    fatigue_weight, 
    sos_weight, 
    revenue_weight,
    max_depth=2,
    max_nodes=400,
    seed=0
):
    """
    This function is our main optimization of the schedule.

    Guide for how it works:
    - Start with a valid schedule
    - Tries swapping games between different weeks
    - Uses recursion with depth limits and backtracking:
        In short: Try a swap , calculate if it's better, explore deeper, undo the swap
    - Keeps track of the best schedule we've found based on our cost function
    - We stop when we hit max_nodes or explore all options up to max_depth

    This will explore the very vast space of possible schedules, and we are trying to find good tradeoffs
    between travel distance, team fatigue, schedule fairness, and TV revenue represented by cost function
    """
    random.seed(seed)
    debug = dict(base_debug) 
    debug["nodes_visited"] = 0  # how many schedules we've evaluated
    debug["backtracks"] = 0  # how many times we've undone a swap

    # calculate the cost of the starting schedule which is our baseline
    current_metrics = compute_metrics(schedule, teams, debug)
    best_cost = objective(current_metrics, travel_weight, fatigue_weight, 
                         sos_weight, revenue_weight)
    best_schedule = {week: list(games) for week, games in schedule.items()}
    best_metrics = dict(current_metrics)
    
    def explore_swaps(current_depth, best_cost, best_schedule, best_metrics):
        """
        Recursive function that explores different game swaps 
        """
        debug["nodes_visited"] += 1
        
        # we want to stop if we've evaluated too many schedules bc of computational limits
        if debug["nodes_visited"] >= max_nodes:
            return best_cost, best_schedule, best_metrics

        if current_depth >= max_depth:
            return best_cost, best_schedule, best_metrics
        
        swap_options = generate_swap_candidates(
            schedule, 
            max_pairs=20, 
            seed=current_depth + debug["nodes_visited"]
        )

        #try swap
        for week1, index1, week2, index2 in swap_options:
            # make the swap
            swap_games(schedule, week1, index1, week2, index2)
            
            #evaluate this new schedule
            temp_debug = {}
            temp_metrics = compute_metrics(schedule, teams, temp_debug)
            current_cost = objective(temp_metrics, travel_weight, fatigue_weight, 
                                    sos_weight, revenue_weight)

            found_improvement = current_cost < best_cost
            if found_improvement:
                best_cost = current_cost
                best_schedule = {week: list(games) for week, games in schedule.items()}
                best_metrics = dict(temp_metrics)

            # decide whether to explore deeper from this swap
            # we explore if we found an improvement OR if the cost is within 5% of best
            # the 5% tolerance lets us explore "nearly as good" branches that might lead somewhere, I played around with threshold a bit
            if found_improvement or current_cost <= best_cost * 1.05:
                best_cost, best_schedule, best_metrics = explore_swaps(
                    current_depth + 1, best_cost, best_schedule, best_metrics
                )

            swap_games(schedule, week1, index1, week2, index2)
            debug["backtracks"] += 1
            
            if debug["nodes_visited"] >= max_nodes:
                break
        
        return best_cost, best_schedule, best_metrics

    best_cost, best_schedule, best_metrics = explore_swaps(0, best_cost, best_schedule, best_metrics)
    debug.update(best_metrics)
    debug["best_cost"] = best_cost

    return best_schedule, debug