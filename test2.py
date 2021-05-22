import numpy as np
import pandas as pd
import random
from scipy import stats

# import psycopg2
# import matplotlib.pyplot as plt

data = pd.read_csv('players_21.csv')

team1_name = 'Real Madrid'

club1_info = data[data['club_name'] == team1_name]

best_def_info1 = club1_info.sort_values(by='defending', ascending=False).head(5)
def_mean1 = best_def_info1['defending'].mean()
print(f'def real madrid {def_mean1}')

best_att_info1 = club1_info.sort_values(by='shooting', ascending=False).head(5)
att_mean1 = best_att_info1['shooting'].mean()
print(f'att real madrid {att_mean1}')


team2_name = 'Genoa'

club2_info = data[data['club_name'] == team2_name]

best_def_info2 = club2_info.sort_values(by='defending', ascending=False).head(5)
def_mean2 = best_def_info2['defending'].mean()
print(f'def genoa {def_mean2}')

best_att_info2 = club2_info.sort_values(by='shooting', ascending=False).head(5)
att_mean2 = best_att_info2['shooting'].mean()
print(f'att genoa {att_mean2}')

# calculate the ratio between the attack end the defence
team1_scored = att_mean1**6 / def_mean2
team2_scored = att_mean2**6 / def_mean1

# calculating the average goals for team1
prob_team1_scored = team1_scored/(team1_scored+team2_scored)
# calculating the average goals for team2
prob_team2_scored = team2_scored/(team1_scored+team2_scored)

# randomly choosing a goals number for each team around their predicted average goals
goals_team1 = np.random.poisson(int((prob_team1_scored)*5), 5)[0]
goals_team2 = np.random.poisson(int((prob_team2_scored)*5), 5)[0]

print(f'Real Madrid scored: {goals_team1}')

print(f'Genoa scored: {goals_team2}')

# if best_team1_rating > best_team2_rating:
#     team1_chance = best_team1_rating + (best_team1_rating - best_team2_rating) * 5
#     team2_chance = best_team2_rating - (best_team1_rating - best_team2_rating) * 5
# elif best_team1_rating < best_team2_rating:
#     team1_chance = best_team1_rating - (best_team2_rating - best_team1_rating) * 5
#     team2_chance = best_team2_rating + (best_team2_rating - best_team1_rating) * 5
# else:
#     team1_chance = best_team1_rating
#     team2_chance = best_team2_rating
#
# # print(team1_scored/team2_scored)
# print(s[0])

# print(int(stats.mode(np.random.poisson((team1_scored),100000))[0]))
# print(int(stats.mode(np.random.poisson((team2_scored),100000))[0]))