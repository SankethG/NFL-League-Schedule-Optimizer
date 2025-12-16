import math
import random
from collections import defaultdict
import streamlit as st
import pandas as pd
from data_class import Team, ScheduledGame, make_full_league
from schedule_core import (
    haversine,
    game_quality,
    assign_prime_time_slots,
    assign_bye_weeks,
    generate_initial_schedule,
    compute_team_sequences,
    compute_metrics,
    objective,
)
from optimizer import (
    generate_swap_candidates,
    swap_games,
    optimize_schedule_backtracking,
)
from schedule_to_df import schedule_to_dataframe
from simulation import (
    simulate_game,
    simulate_season,
    determine_playoff_teams,
    simulate_playoffs,
    full_season_playoff_simulation,
)

# Configuring the page layout and title
st.set_page_config(
    page_title="NFL League Scheduling Optimizer",
    layout="wide",
)

# Sidebar controls for user customization
st.title("NFL League Scheduling Optimizer")
st.caption(
    "Our app creates a valid 32-team NFL Schedule. "
    " We start with a valid random schedule and use our proprietary backtracking app to optimize it, with our goals of "
    "reducing travel, fatigue, and schedule unfairness, while putting the best matchups in prime-time slots for maximum revenue."
)
st.sidebar.header("Controls")

# Lets our different users adjust the weights for different objectives
travel_weight = st.sidebar.slider("Travel weight", 0.0, 2.0, 1.0, 0.1)
fatigue_weight = st.sidebar.slider("Fatigue weight", 0.0, 2.0, 0.7, 0.1)
sos_weight = st.sidebar.slider("Strength-of-schedule weight", 0.0, 2.0, 0.7, 0.1)
revenue_weight = st.sidebar.slider("Revenue/Prime Time weight", 0.0, 2.0, 0.5, 0.1)

#random seeds for reproducibility
initial_schedule_seed = st.sidebar.number_input("Initial schedule seed", 0, 9999, 123, 1)
optimizer_seed = st.sidebar.number_input("Optimizer seed", 0, 9999, 0, 1)


#limits for backtracking
max_depth = st.sidebar.slider("Backtracking depth", 1, 4, 2, 1)
max_nodes = st.sidebar.slider("Max search nodes", 100, 5000, 800, 100)
    
if "schedule_df" not in st.session_state:
    st.session_state["schedule_df"] = None
    st.session_state["debug"] = None
    st.session_state["initial_metrics"] = None
    st.session_state["current_schedule"] = None
    st.session_state["teams"] = None


#Used AI to debug for this(69- 78), essentially was getting same schedules, needed different randomness
# Track how many times we've generated schedules/simulations
# This helps us create different random results each time the button is clicked
if "generate_run_id" not in st.session_state:
    st.session_state["generate_run_id"] = 0
if "simulate_run_id" not in st.session_state:
    st.session_state["simulate_run_id"] = 0


# Main schedule generation button
if st.sidebar.button("Generate Schedule"):
    # Increment our run counter so we get different results each time
    st.session_state["generate_run_id"] += 1
    run_id = st.session_state["generate_run_id"]

    teams = make_full_league()  #Create league 
    
    starting_schedule, starting_debug = generate_initial_schedule( #generate some initial valid schedule
        teams, 
        num_weeks=18, 
        seed=int(initial_schedule_seed) + run_id
    )
    
    
    # Calculate metrics for the initial schedule so we can compare improvement later
    initial_metrics = compute_metrics(starting_schedule, teams, {})
    st.session_state["initial_metrics"] = initial_metrics
    
    
    # Run the backtracking optimizer to improve the schedule
    optimized_schedule, final_debug = optimize_schedule_backtracking(
        starting_schedule,
        teams,
        starting_debug,
        travel_weight=travel_weight,
        fatigue_weight=fatigue_weight,
        sos_weight=sos_weight,
        revenue_weight=revenue_weight,
        max_depth=int(max_depth),
        max_nodes=int(max_nodes),
        seed=int(optimizer_seed) + run_id, #in conjunction with lines 69-78, this was changed as I used Ai to debug 
                                            #this is because problem was getting same schedules a lot of time so I needed
                                            #to introduce more randomness, which this does, 
    )

    
    # Convert schedule to a DataFrame for easier use/display on streamlit
    schedule_df = schedule_to_dataframe(optimized_schedule)
    
    # Store everything in session state
    st.session_state["schedule_df"] = schedule_df
    st.session_state["debug"] = final_debug
    st.session_state["current_schedule"] = optimized_schedule
    st.session_state["teams"] = teams
    

# Playoff simulation section
st.sidebar.markdown("---")
st.sidebar.subheader("Playoff Simulation")
simulation_seed = st.sidebar.number_input("Simulation seed", 0, 9999, 42, 1)


if "playoff_results" not in st.session_state:
    st.session_state["playoff_results"] = None
    st.session_state["season_records"] = None
    st.session_state["afc_playoff"] = None
    st.session_state["nfc_playoff"] = None

if st.sidebar.button(" Simulate Season & Playoffs"):
    # Want to make sure we have a schedule first
    if st.session_state["current_schedule"] is not None and st.session_state["teams"] is not None:
        st.session_state["simulate_run_id"] += 1
        sim_run_id = st.session_state["simulate_run_id"]

        with st.spinner("Simulating season and playoffs..."):
             # Run simulation for our whole szn
            records, afc_teams, nfc_teams, playoff_results = full_season_playoff_simulation(
                st.session_state["current_schedule"],
                st.session_state["teams"],
                seed=int(simulation_seed) + sim_run_id #once Ai debugged this from line 100, i used same logic it did for playoffs
                                                        # and regular szn simulations
            )
            
            st.session_state["season_records"] = records
            st.session_state["afc_playoff"] = afc_teams
            st.session_state["nfc_playoff"] = nfc_teams
            st.session_state["playoff_results"] = playoff_results
            
        st.sidebar.success("Simulation complete!")
    else:
        st.sidebar.error("Please click the generate schedule button first!")

# Get our data from session state
schedule_df = st.session_state["schedule_df"]
debug = st.session_state["debug"]
initial_metrics = st.session_state.get("initial_metrics")

# Show the playoff results if they exist
if st.session_state["playoff_results"] is not None:
    st.markdown("---")
    st.markdown("## Season Simulation Results")
    
    champion = st.session_state["playoff_results"]["champion"]
    st.success(f"### Super Bowl Champion: **{champion.name}** ")
    
    #create different view tabs for better/easier visualizations
    tab1, tab2, tab3, tab4 = st.tabs(["Final Standings", "Playoff Bracket", "Playoff Results", "Season Stats"])
    
    with tab1:
        st.subheader("Final Regular Season Standings")
        
        col1, col2 = st.columns(2)
        
        #Standings for AFC
        with col1:
            st.markdown("### AFC Standings")
            afc_records = []
            for team_name, record in st.session_state["season_records"].items():
                if record['team'].conference == 'AFC':
                    afc_records.append({
                        'Team': team_name,
                        'Division': record['team'].division,
                        'Wins': record['wins'],
                        'Losses': record['losses'],
                        'Strength': record['team'].strength
                    })
            afc_df = pd.DataFrame(afc_records)
            afc_df = afc_df.sort_values(['Wins', 'Strength'], ascending=[False, False])
            
            playoff_team_names = [t.name for t in st.session_state["afc_playoff"]]
            
            
            # Helper function to highlight the playoff teams in green in the UI
            def highlight_playoffs(row):
                if row['Team'] in playoff_team_names:
                    return ['background-color: lightgreen'] * len(row)
                return [''] * len(row)
            
            st.dataframe(
                afc_df[['Team', 'Division', 'Wins', 'Losses']].style.apply(highlight_playoffs, axis=1),
                hide_index=True,
                use_container_width=True
            )
            st.caption("Green = Playoff Team")
        
        with col2:
            st.markdown("### NFC Standings")
            nfc_records = []
            for team_name, record in st.session_state["season_records"].items():
                if record['team'].conference == 'NFC':
                    nfc_records.append({
                        'Team': team_name,
                        'Division': record['team'].division,
                        'Wins': record['wins'],
                        'Losses': record['losses'],
                        'Strength': record['team'].strength
                    })
            nfc_df = pd.DataFrame(nfc_records)
            nfc_df = nfc_df.sort_values(['Wins', 'Strength'], ascending=[False, False])
            
            playoff_team_names = [t.name for t in st.session_state["nfc_playoff"]]
            
            #Standings for NFC
            st.dataframe(
                nfc_df[['Team', 'Division', 'Wins', 'Losses']].style.apply(highlight_playoffs, axis=1),
                hide_index=True,
                use_container_width=True
            )
            st.caption("Green = Playoff Team")
    
    with tab2:
        st.subheader("Playoff Seeding")
        
        col1, col2 = st.columns(2)
        
        # Show the 7 playoff seeds for each conference
        with col1:
            st.markdown("### AFC Playoff Seeds")
            afc_playoff_list = []
            for i, team in enumerate(st.session_state["afc_playoff"], 1):
                record = st.session_state["season_records"][team.name]
                afc_playoff_list.append({
                    'Seed': i,
                    'Team': team.name,
                    'Record': f"{record['wins']}-{record['losses']}"
                })
            st.table(pd.DataFrame(afc_playoff_list))
        
        with col2:
            st.markdown("### NFC Playoff Seeds")
            nfc_playoff_list = []
            for i, team in enumerate(st.session_state["nfc_playoff"], 1):
                record = st.session_state["season_records"][team.name]
                nfc_playoff_list.append({
                    'Seed': i,
                    'Team': team.name,
                    'Record': f"{record['wins']}-{record['losses']}"
                })
            st.table(pd.DataFrame(nfc_playoff_list))
    
    with tab3:
        st.subheader("Playoff Game Results")
        
        col1, col2 = st.columns(2)
        
        playoff_results = st.session_state["playoff_results"]
        
           # Display all playoff rounds for each conference
        with col1:
            st.markdown("### AFC Playoffs")
            st.markdown("**Wild Card Round:**")
            for result in playoff_results['wild_card']['AFC']:
                st.write(f"• {result}")
            
            st.markdown("**Divisional Round:**")
            for result in playoff_results['divisional']['AFC']:
                st.write(f"• {result}")
            
            st.markdown("**Conference Championship:**")
            st.write(f"• {playoff_results['conference']['AFC']}")
        
        with col2:
            st.markdown("### NFC Playoffs")
            st.markdown("**Wild Card Round:**")
            for result in playoff_results['wild_card']['NFC']:
                st.write(f"• {result}")
            
            st.markdown("**Divisional Round:**")
            for result in playoff_results['divisional']['NFC']:
                st.write(f"• {result}")
            
            st.markdown("**Conference Championship:**")
            st.write(f"• {playoff_results['conference']['NFC']}")
        
        st.markdown("---")
        st.markdown("### 🏆 Super Bowl")
        st.markdown(f"**{playoff_results['super_bowl']}**")
    
     # Show some basic season stats, like best team, worst team, avg wins, very basic stuff
    with tab4:
        st.subheader("Season Statistics")
        
        all_records = list(st.session_state["season_records"].values())
        
        total_wins = sum(r['wins'] for r in all_records)
        total_losses = sum(r['losses'] for r in all_records)
        avg_wins = total_wins / len(all_records)
        
        best_record_entry = max(all_records, key=lambda x: (x['wins'], x['team'].strength))
        worst_record_entry = min(all_records, key=lambda x: (x['wins'], x['team'].strength))
        
        col1, col2, col3 = st.columns(3)
          
        with col2:
            st.metric("Average Wins", f"{avg_wins:.1f}")
        
# If no schedule has been generated yet, let our user know that they need to click the button first
if schedule_df is None:
    st.info("Adjust the weights on the side and click Generate Schedule to build out a full league schedule")
    st.stop()

# Show some basic stats about the schedule like games played and prime time games
st.sidebar.metric("Total Games", len(schedule_df))
st.sidebar.metric("Prime Time Games", 
                 len(schedule_df[schedule_df["Prime Time"]]))

#in case anyone wants to download and view it in csv for easier reading
csv = schedule_df.to_csv(index=False)
st.sidebar.download_button(
    label="Download Schedule as CSV",
    data=csv,
    file_name="nfl_schedule.csv",
    mime="text/csv"
)

show_prime_time = st.sidebar.checkbox(
    "Highlight prime-time games",
    value=False
)

show_comparison = st.sidebar.checkbox("Show optimization improvement", value=False)


# Different ways to view the schedule, if you want full schedule vs like schedule of only ur favorite team
view_mode = st.sidebar.radio(
    "View schedule",
    ["By Week", "By Team", "Full Schedule"],
)

if view_mode == "By Week":
    all_weeks = sorted(schedule_df["Week"].unique().tolist())
    selected_week = st.selectbox("Select week", all_weeks, index=0)

    week_games = schedule_df[schedule_df["Week"] == selected_week].copy()
    week_games = week_games[["Week", "Matchup", "Kickoff", "City", "Prime Time"]]

    if show_prime_time:
        week_games["Prime Time"] = week_games["Prime Time"].map(lambda x: "Yes" if x else "")
    else:
        week_games = week_games.drop(columns=["Prime Time"])

    st.subheader(f"Games in Week {selected_week}")
    st.dataframe(
        week_games,
        hide_index=True,
        use_container_width=True,
    )

elif view_mode == "By Team":
    all_teams = sorted(
        set(schedule_df["Home"]).union(set(schedule_df["Away"]))
    )
    selected_team = st.selectbox("Select team", all_teams, index=0)

    team_games = schedule_df[
        (schedule_df["Home"] == selected_team) | (schedule_df["Away"] == selected_team)
    ].copy()

    # Helper functions to help us decide home or away status
    def determine_home_or_away(row):
        return "Home" if row["Home"] == selected_team else "Away"

    def get_opponent(row):
        return row["Away"] if row["Home"] == selected_team else row["Home"]

    team_games["H/A"] = team_games.apply(determine_home_or_away, axis=1)
    team_games["Opponent"] = team_games.apply(get_opponent, axis=1)
    team_games = team_games[["Week", "H/A", "Opponent", "Kickoff", "City", "Prime Time"]]
    team_games = team_games.sort_values("Week")

    if show_prime_time:
        team_games["Prime Time"] = team_games["Prime Time"].map(
            lambda x: "Yes" if x else ""
        )
    else:
        team_games = team_games.drop(columns=["Prime Time"])

    st.subheader(f"Schedule for {selected_team}")
    st.table(team_games.reset_index(drop=True))

elif view_mode == "Full Schedule":
    st.subheader("Full Optimized Schedule (All 18 Weeks)")

    full_schedule_display = schedule_df.copy()
    full_schedule_display = full_schedule_display[["Week", "Matchup", "Kickoff", "City", "Prime Time"]]
    
    if show_prime_time:
        full_schedule_display["Prime Time"] = full_schedule_display["Prime Time"].map(
            lambda x: "Yes" if x else ""
        )
    else:
        full_schedule_display = full_schedule_display.drop(columns=["Prime Time"])

    full_schedule_display = full_schedule_display.sort_values(["Week", "Matchup"])
    st.dataframe(
        full_schedule_display,
        hide_index=True,
        use_container_width=True,
    )

st.markdown("---")

if show_comparison and initial_metrics is not None:
    st.markdown("### Optimization Improvement")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculat the percent improvements for each metric
    with col1:
        initial_travel = initial_metrics.get('total_travel', 0)
        final_travel = debug.get('total_travel', 0)
        improvement = ((initial_travel - final_travel) / initial_travel * 100) if initial_travel > 0 else 0
        st.metric("Travel Distance", f"{final_travel:.1f} km", 
                 f"{-improvement:.1f}%", delta_color="inverse")
    
    with col2:
        initial_fatigue = initial_metrics.get('fatigue_penalty', 0)
        final_fatigue = debug.get('fatigue_penalty', 0)
        improvement = ((initial_fatigue - final_fatigue) / initial_fatigue * 100) if initial_fatigue > 0 else 0
        st.metric("Fatigue Penalty", f"{final_fatigue:.1f}", 
                 f"{-improvement:.1f}%", delta_color="inverse")
    
    with col3:
        initial_sos = initial_metrics.get('sos_variance', 0)
        final_sos = debug.get('sos_variance', 0)
        improvement = ((initial_sos - final_sos) / initial_sos * 100) if initial_sos > 0 else 0
        st.metric("SoS Variance", f"{final_sos:.4f}", 
                 f"{-improvement:.1f}%", delta_color="inverse")
    
    with col4:
        initial_revenue = initial_metrics.get('revenue_score', 0)
        final_revenue = debug.get('revenue_score', 0)
        improvement = ((final_revenue - initial_revenue) / initial_revenue * 100) if initial_revenue > 0 else 0
        st.metric("Revenue Score", f"{final_revenue:.1f}", 
                 f"{improvement:.1f}%")

st.markdown("### Optimization Metrics for the Full League")
# Shows the before/after comparison if user wants to see it

    
    
    # Show all the detailed metrics about the optimized schedule, with regards to 4 main variables below
if debug is not None:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.write(f"**Best objective (our cost):** {debug.get('best_cost', 0):.1f}")
        st.write(f"**Total travel:** {debug.get('total_travel', 0):.1f} km")
    
    with col2:
        st.write(f"**Travel time:** {debug.get('travel_time_hours', 0):.1f} hours")
        st.write(f"**Fatigue penalty:** {debug.get('fatigue_penalty', 0):.1f}")
    
    with col3:
        st.write(f"**SoS variance:** {debug.get('sos_variance', 0):.4f}")
        st.write(f"**Nodes visited:** {debug.get('nodes_visited', 0)}")
    
    with col4:
        st.write(f"**Revenue score:** {debug.get('revenue_score', 0):.1f}")
        st.write(f"**Backtracks:** {debug.get('backtracks', 0)}")
        if 'improvements_found' in debug:
            st.write(f"**Improvements found:** {debug.get('improvements_found', 0)}")

    if "team_sos" in debug:
        sos_breakdown = pd.DataFrame(
            [{"Team": team_name, "SoS": sos_value} 
             for team_name, sos_value in debug["team_sos"].items()]
        ).sort_values("SoS", ascending=False)
        
        st.markdown("### Strength of Schedule by Team")
        st.dataframe(sos_breakdown, hide_index=True, use_container_width=True)

    st.caption(
        "**Our Objective:** Our cost function is the following: "
        "a·(total travel) + b·(fatigue penalty) + c·(SoS variance) − d·(revenue score), "
        "where a, b, c, d are customizable weights. "
        "Travel and fatigue come from factors like distances, away game streaks, long trips, and short-rest. "
        "Revenue increases when high-quality matchups are in prime-time slots and game quality "
        "combines team strengths and rivalry bonuses."
    )