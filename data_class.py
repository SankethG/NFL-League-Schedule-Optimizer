from dataclasses import dataclass

#I used AI(lines 15-96), (basically this whole file) to make this func(make_full_league), I basically prompted GPT by asking it  
# Can you make me a team list for all teams in nfl with locations, coordinates, division, and strength ratings
# The strength ratings are random for now, will look into datasets to find real ones later, shouldn't take long

#I also used google links to get formulas/function names, I commented those in the code as well where needed

#data class was a suggestion from chat gpt, but look into maybe changing this or incorporating more class
#structure for the later bits of the code. 

@dataclass
class Team:
    
    """Gives us an NFL team with location and strength rating"""
    
    name: str               #team name
    city: str               # city where team resides(important for determine home/away games)
    lat: float              # latitude for calculating travel distance
    lon: float              # longitude for calculating travel distance
    conference: str         # conference, which is ewither AFC or NFC
    division: str           # division, which is either East, North, South, or West
    strength: float         # team strength rating 

@dataclass
class ScheduledGame:
    
    """
    Gives us a single game in the schedule, with the following time slots:
    
    Time slots:
      - "SUN_1PM"   : Sunday afternoon (1:00 PM ET)
      - "SUN_4PM"   : Sunday late afternoon (4:05 PM or 4:25 PM ET)
      - "SUN_NIGHT" : Sunday Night Football (8:20 PM EST)
      - "MON"       : Monday Night Football (8:15 PM EST)
      - "THU"       : Thursday Night Football (8:20 PM EST)
    """
    
    week: int
    home: Team
    away: Team  
    slot: str = "SUN_1PM"  

def make_full_league():
 
    teams = [
        # AFC East Division
        Team("Buffalo Bills",         "Buffalo, NY",         42.9, -78.9,  "AFC", "East", 3.7),
        Team("Miami Dolphins",        "Miami Gardens, FL",   25.9, -80.3,  "AFC", "East", -2.7),
        Team("New England Patriots",  "Foxborough, MA",      42.1, -71.2,  "AFC", "East", 1.0),
        Team("New York Jets",         "East Rutherford, NJ", 40.8, -74.1,  "AFC", "East", -8.0),

        # AFC North Division
        Team("Baltimore Ravens",      "Baltimore, MD",       39.3, -76.6,  "AFC", "North", 2.9),
        Team("Cincinnati Bengals",    "Cincinnati, OH",      39.1, -84.5,  "AFC", "North", 1.1),
        Team("Cleveland Browns",      "Cleveland, OH",       41.5, -81.7,  "AFC", "North", -8.6),
        Team("Pittsburgh Steelers",   "Pittsburgh, PA",      40.4, -80.0,  "AFC", "North", -0.7),

        # AFC South Division
        Team("Houston Texans",        "Houston, TX",         29.8, -95.4,  "AFC", "South", 3.4),
        Team("Indianapolis Colts",    "Indianapolis, IN",    39.8, -86.2,  "AFC", "South", -2.5),
        Team("Jacksonville Jaguars",  "Jacksonville, FL",    30.3, -81.7,  "AFC", "South", 1.3),
        Team("Tennessee Titans",      "Nashville, TN",       36.2, -86.8,  "AFC", "South", -9.2),

        # AFC West Division
        Team("Denver Broncos",        "Denver, CO",          39.7, -105.0, "AFC", "West", 2.6),
        Team("Kansas City Chiefs",    "Kansas City, MO",     39.1, -94.6,  "AFC", "West", 6.0),
        Team("Las Vegas Raiders",     "Las Vegas, NV",       36.1, -115.2, "AFC", "West", -6.7),
        Team("Los Angeles Chargers",  "Los Angeles, CA",     34.0, -118.2, "AFC", "West", 1.3),

        # NFC East Division
        Team("Dallas Cowboys",        "Arlington, TX",       32.8, -97.1,  "NFC", "East", 0.3),
        Team("New York Giants",       "East Rutherford, NJ", 40.8, -74.1,  "NFC", "East", -1.4),
        Team("Philadelphia Eagles",   "Philadelphia, PA",    39.9, -75.2,  "NFC", "East", 3.6),
        Team("Washington Commanders", "Landover, MD",        38.9, -76.9,  "NFC", "East", -3.8),

        # NFC North Division
        Team("Chicago Bears",         "Chicago, IL",         41.9, -87.6,  "NFC", "North", -0.5),
        Team("Detroit Lions",         "Detroit, MI",         42.3, -83.0,  "NFC", "North", 5.0),
        Team("Green Bay Packers",     "Green Bay, WI",       44.5, -88.0,  "NFC", "North", 5.2),
        Team("Minnesota Vikings",     "Minneapolis, MN",     44.9, -93.3,  "NFC", "North", -2.6),

        # NFC South Division
        Team("Atlanta Falcons",       "Atlanta, GA",         33.7, -84.4,  "NFC", "South", -4.6),
        Team("Carolina Panthers",     "Charlotte, NC",       35.2, -80.8,  "NFC", "South", -4.2),
        Team("New Orleans Saints",    "New Orleans, LA",     29.9, -90.1,  "NFC", "South", -6.7),
        Team("Tampa Bay Buccaneers",  "Tampa, FL",           27.9, -82.5,  "NFC", "South", -0.9),

        # NFC West Division
        Team("Arizona Cardinals",     "Glendale, AZ",        33.5, -112.3, "NFC", "West", -3.8),
        Team("Los Angeles Rams",      "Los Angeles, CA",     34.0, -118.2, "NFC", "West", 6.9),
        Team("San Francisco 49ers",   "Santa Clara, CA",     37.4, -121.9, "NFC", "West", 3.6),
        Team("Seattle Seahawks",      "Seattle, WA",         47.6, -122.3, "NFC", "West", 4.8),
    ]
    
    return teams