[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/NdAim9o4)


# Final-Project
Template repository for 46-902 final project.
Replace the header with your project title.

### Summary

My NFL League Schedule Optimizer project’s goal is to optimize an NFL schedule.  Given the fact that there is a very large/intractable state space of possible combinations, I plan to achieve this by using smart backtracking, heuristics, and pruning to make an ideal NFL schedule. My final output will be a UI on a local host server with the made schedule, as well as toggles where you can sort by week, a specific team, etc.

### Background Knowledge
There are 32 teams in the NFL, and they each play 17 games in 18 weeks, with a bye/rest week scattered randomly after week 4 for each team. The schedule will have 18 weeks of games that follow these NFL Rules. 
If teams are within the same division, they will have two matchups per year required. If not, than teams will only play each other at maximum one time during the season. Each team must have a bye week(starting on Week 4 until Week 17). Each team must play 17 games


### Running the Project

In terms of running the current demo, you can run using the cmd--> "streamlit run app.py", where app.py is the current file I have which is a sample interface of what it would look like. 

In order to run properly, you need to pip install/have a conda environment with streamlit and pandas on it for the current demo. You will get a local host link where you can see the current UI, and this is the output/how I plan to demo when the project is done. I plan to also have this be the final file you run when I am done with the project, with the backtracking/logic stuff optimized later on.

### Update for deliverable 2

everything above is the same, here is the set of imports i use
import random
from dataclasses import dataclass 
from collections import defaultdict
import streamlit as st
import pandas as pd

pandas and streamlit are the only ones that should be in the conda/package environment, all other instructions are the same.



