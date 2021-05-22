import numpy as np
import pandas as pd
import random
import psycopg2
import matplotlib.pyplot as plt


def run_sql(query, type='get'):
    HOSTNAME = '127.0.0.1'
    USERNAME = 'postgres'
    PASSWORD = 'Lala1421'
    DATABASE = 'FifaHackathon'
    connection = psycopg2.connect(host=HOSTNAME, user=USERNAME, password=PASSWORD, dbname=DATABASE)
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    if type == 'get':
        results = cursor.fetchall()
        connection.close()
        return results
    connection.close()


data = pd.read_csv('players_21.csv')
playing = True
print('Welcome to the Fifa21 match simulator!')
first_round = True
while playing:

    if first_round:
        query = "insert into num_of_seasons(name) values('new season')"
        run_sql(query, 'post')
        first_round = False
        query = "select season from num_of_seasons order by season desc limit 1"
        season_num, = run_sql(query)[0]
        query = f"create table season_games{season_num} (game_id serial primary key, team1 varchar not null, team2 varchar not null, team1_scored int, team2_scored int, points_team1 int, points_team2 int )"
        run_sql(query, 'post')

    print('Please select an options from the list below:')
    user_input = ''
    while (user_input != '1' and user_input != '2' and user_input != '3'):
        print('(1) Instructions')
        print('(2) Select 2 teams')
        print('(3) Finish the season')
        user_input = input('Enter your choise: ')

    if user_input == '1':
        print('Hello and welcome to the Fifa21 match simulator!')
        print(
            '''
            This match making and result predicting ability
            are based on a Fifa21 players database
            and an algorithm of score prediction.''')
        print('You are going to select 2 teams to your liking, and the computer is going to simulate the match.')
        print('The scores are sent to a database and the champions are crowned based on their previous results.')
        print('Without further ado, let the season begin!')
    elif user_input == '2':

        team1_name = input('Enter team 1 name: ')
        # picks the info about the players from the club
        club1_info = data[data['club_name'] == team1_name]

        # picks starting 11 out of the best players in the club (to be improved)
        # starting_players1 = club1_info.sort_values(by='overall', ascending=False).head(11)

        best_def_info1 = club1_info.sort_values(by='defending', ascending=False).head(5)
        def_mean1 = best_def_info1['defending'].mean()

        best_att_info1 = club1_info.sort_values(by='shooting', ascending=False).head(5)
        att_mean1 = best_att_info1['shooting'].mean()

        # their rating
        # best_team1_rating = starting_players1['overall'].sum()


        team2_name = input('Enter team 2 name: ')
        # picks the info about the players from the club
        club2_info = data[data['club_name'] == team2_name]

        # picks starting 11 out of the best players in the club (to be improved)
        # starting_players2 = club2_info.sort_values(by='overall', ascending=False).head(11)

        best_def_info2 = club2_info.sort_values(by='defending', ascending=False).head(5)
        def_mean2 = best_def_info2['defending'].mean()

        best_att_info2 = club2_info.sort_values(by='shooting', ascending=False).head(5)
        att_mean2 = best_att_info2['shooting'].mean()

        # their rating
        # best_team2_rating = starting_players2['overall'].sum()

        # first model of score predicting
        # if best_team1_rating > best_team2_rating:
        #     team1_chance = best_team1_rating + (best_team1_rating - best_team2_rating) * 5
        #     team2_chance = best_team2_rating - (best_team1_rating - best_team2_rating) * 5
        # elif best_team1_rating < best_team2_rating:
        #     team1_chance = best_team1_rating - (best_team2_rating - best_team1_rating) * 5
        #     team2_chance = best_team2_rating + (best_team2_rating - best_team1_rating) * 5
        # else:
        #     team1_chance = best_team1_rating
        #     team2_chance = best_team2_rating

        # match = [team1_name, team2_name]

        # winner = random.choices(match, weights=(team1_chance, team2_chance))[0]

        # if winner == team1_name:
        #     loser = team2_name
        # else:
        #     loser = team1_name

        # print(f'The winner is {winner}!')

        # Second Score predicrtion model:
        match = [team1_name, team2_name]
        # calculate the ratio between the attack end the defence
        team1_scored = att_mean1 ** 6 / def_mean2
        team2_scored = att_mean2 ** 6 / def_mean1

        # calculating the average goals for team1
        prob_team1_scored = team1_scored / (team1_scored + team2_scored)
        # calculating the average goals for team2
        prob_team2_scored = team2_scored / (team1_scored + team2_scored)

        # randomly choosing a goals number for each team around their predicted average goals
        goals_team1 = np.random.poisson(int((prob_team1_scored) * 5), 5)[0]
        goals_team2 = np.random.poisson(int((prob_team2_scored) * 5), 5)[0]

        # print(f'Real Madrid scored: {goals_team1}')
        #
        # print(f'Genoa scored: {goals_team2}')
        # Who is the winner?
        if goals_team1 > goals_team2:
            points_team1 = 3
            points_team2 = 0
        elif goals_team2 > goals_team1:
            points_team2 = 3
            points_team1 = 0
        else:
            points_team1 = 1
            points_team2 = 1

        query = f"insert into season_games{season_num}(team1, team2, team1_scored, team2_scored, team1_points, team2_points) values ('{team1_name}', '{team2_name}', {goals_team1}, {goals_team2}, {points_team1}, {points_team2})"
        run_sql(query, 'post')

    if user_input == '3':
        query = f"create table season_rank{season_num} (loc_id serial primary key, team varchar not null, points int not null)"
        run_sql(query, 'post')

        query = f"select distinct winner from season_games{season_num}"
        winners = run_sql(query)
        list_winners = []

        for win in winners:
            (rw,) = win
            list_winners.append(rw, )

        query = f"select distinct loser from season_games{season_num}"
        losers = run_sql(query)
        list_losers = []

        for loss in losers:
            (rl,) = loss
            list_losers.append(rl, )

        for i in list_winners:
            query = f"select count(winner) from season_games{season_num} where winner='{i}'"
            winner_points, = run_sql(query)[0]
            query = f"insert into season_rank{season_num}(team, points) values ('{i}',{winner_points * 3})"
            run_sql(query, 'post')

        for j in list_losers:
            if j not in list_winners:
                query = f"insert into season_rank{season_num}(team, points) values ('{j}', 0)"
                run_sql(query, 'post')

        query = f"select team,points from season_rank{season_num} order by points desc"
        table = run_sql(query)
        print('location (Team, Points)')
        print('--------------------')
        for index, place in enumerate(table):
            print(index+1, place)
            print('--------------------')

        query = f"select team from season_rank{season_num} order by points desc limit 1"
        champions = run_sql(query)[0]
        print(f'{champions} are the CHAMPIONS of the season!')

        list_winners = []
        list_losers = []
        playing = False




# team1_name = 'Real Madrid'
# # picks the info about the players from the club
# club1_info = data[data['club_name'] == team1_name]
#
# # picks starting 11 out of the best players in the club (to be improved)
# starting_players1 = club1_info.sort_values(by='overall', ascending=False).head(11)
#
# # their rating
# best_team1_rating = starting_players1['overall'].sum()
#
# print(best_team1_rating)
#
# team2_name = 'Genoa'
# # picks the info about the players from the club
# club2_info = data[data['club_name'] == team2_name]
#
# # picks starting 11 out of the best players in the club (to be improved)
# starting_players2 = club2_info.sort_values(by='overall', ascending=False).head(11)
#
# # their rating
# best_team2_rating = starting_players2['overall'].sum()
#
# print(best_team2_rating)
#
# # first model of score predicting
# # sum_ratings = best_team1_rating + best_team2_rating
# if best_team1_rating > best_team2_rating:
#     team1_chance = best_team1_rating + (best_team1_rating - best_team2_rating)*5
#     team2_chance = best_team2_rating - (best_team1_rating - best_team2_rating)*5
# elif best_team1_rating < best_team2_rating:
#     team1_chance = best_team1_rating - (best_team2_rating - best_team1_rating)*5
#     team2_chance = best_team2_rating + (best_team2_rating - best_team1_rating)*5
# else:
#     team1_chance = best_team1_rating
#     team2_chance = best_team2_rating
#
# # team1_chance = best_team1_rating *
# # team2_chance = best_team2_rating *
#
# print(f'{team1_name} chance: {team1_chance/(team1_chance+team2_chance)}')
# print(f'{team2_name} chance: {team2_chance/(team1_chance+team2_chance)}')
#
# match = [team1_name, team2_name]
# winners = []
# for i in range(100):
#     winner = random.choices(match, weights=(team1_chance, team2_chance))[0]
#     winners.append(winner)
#
# print(f'{team1_name} wins: {winners.count(team1_name)}%')
# print(f'{team2_name} wins: {winners.count(team2_name)}%')
