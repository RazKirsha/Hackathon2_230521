import numpy as np
import pandas as pd
import random
import psycopg2


def run_sql(query, type='get'):
    HOSTNAME = '127.0.0.1'
    USERNAME = 'postgres'
    PASSWORD = 'Lala1421'
    DATABASE = 'test_Hackthon'
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
        print('(2) Select teams to compete!')
        print('(3) Finish the season')
        user_input = input('Enter your choice: ')

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

        best_def_info1 = club1_info.sort_values(by='defending', ascending=False).head(5)
        def_mean1 = best_def_info1['defending'].mean()

        best_att_info1 = club1_info.sort_values(by='shooting', ascending=False).head(5)
        att_mean1 = best_att_info1['shooting'].mean()

        team2_name = input('Enter team 2 name: ')
        # picks the info about the players from the club
        club2_info = data[data['club_name'] == team2_name]

        best_def_info2 = club2_info.sort_values(by='defending', ascending=False).head(5)
        def_mean2 = best_def_info2['defending'].mean()

        best_att_info2 = club2_info.sort_values(by='shooting', ascending=False).head(5)
        att_mean2 = best_att_info2['shooting'].mean()

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

        print(f'{team1_name} scored: {goals_team1}')

        print(f'{team2_name} scored: {goals_team2}')

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

        query = f"insert into season_games{season_num}(team1, team2, team1_scored, team2_scored, points_team1, points_team2) values ('{team1_name}', '{team2_name}', {goals_team1}, {goals_team2}, {points_team1}, {points_team2})"
        run_sql(query, 'post')

    if user_input == '3':

        query = f"create view teams1_points_season{season_num} as select team1,sum(points_team1), sum(team1_scored - team2_scored) as goal_diff from season_games{season_num} group by team1"
        run_sql(query, 'post')

        query = f"create view teams2_points_season{season_num} as select team2,sum(points_team2), sum(team2_scored - team1_scored) as goal_diff from season_games{season_num} group by team2"
        run_sql(query, 'post')

        query = f"create view all_points_season{season_num} as select * from teams1_points_season{season_num} union select * from teams2_points_season{season_num}"
        run_sql(query, 'post')

        query = f"select team1, sum(sum) as points, sum(goal_diff) as goal_difference from all_points_season{season_num} group by team1 order by points desc, goal_difference desc"
        table = run_sql(query)

        print(f"This is the end of the season's table:")
        print('location (Team, Points)')
        print('--------------------')
        for index, stats in enumerate(table):
            (team_name, team_point, goal_dif) = stats
            if index == 0:
                champions = team_name
            print(f"{index + 1} - {team_name} - {team_point} - {goal_dif}")
            print('--------------------')

        print(f"{champions} are the Ultimate CHAMPIONS!!!! ")

        playing = False
