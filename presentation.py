import pandas as pd
from models import ScheduledGame, Team

def schedule_to_dataframe(schedule):
    """
    Converts our schedule into a pandas DataFrame, which we than can use to display in Streamlit
    """
    rows = []
    
    #This maps our slot codes to actual day/time strings
    # They also match the real NFL slots
    slot_to_day_time = {
        "SUN_1PM": ("Sun", "1:00 PM"),
        "SUN_4PM": ("Sun", "4:05 PM"),
        "SUN_NIGHT": ("Sun", "8:20 PM"),
        "MON": ("Mon", "8:15 PM"),
        "THU": ("Thu", "8:15 PM"),
    }

     # Loop through each week and each game 
    for week_number, games_this_week in schedule.items():
        for game in games_this_week:
            day, time = slot_to_day_time.get(game.slot, ("Sun", "1:00 PM"))
            # Create a row with all the game info we want to have/show
            rows.append({
                "Week": week_number,
                "Home": game.home.name,
                "Away": game.away.name,
                "City": game.home.city,
                "Day": day,
                "Time": time,
                "Slot": game.slot,
            })

    df = pd.DataFrame(rows)
    df["Matchup"] = df["Away"] + " @ " + df["Home"]
    df["Kickoff"] = df["Day"] + " " + df["Time"]
    
    # Mark the prime time games which will be useful for filtering for display later
    df["Prime Time"] = df["Slot"].isin(["SUN_NIGHT", "MON", "THU"])
    
    
    # Sort by week first, then alphabetically by matchup, will look the cleanest on UI to see
    return df.sort_values(["Week", "Matchup"]).reset_index(drop=True)