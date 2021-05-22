import numpy as np
import pandas as pd
import random
import psycopg2


# run an sql query
def run_sql(query, type='get'):
    HOSTNAME = '127.0.0.1'
    USERNAME = 'postgres'
    PASSWORD = 'Lala1421'
    DATABASE = 'FifaHackathon2'
    connection = psycopg2.connect(host=HOSTNAME, user=USERNAME, password=PASSWORD, dbname=DATABASE)
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    if type == 'get':
        results = cursor.fetchall()
        connection.close()
        return results
    connection.close()

# setting the arguments for a season
data = pd.read_csv('players_21.csv')
playing = True
print('Welcome to the Fifa21 match simulator!')

# starting a new season
while playing:
    competitors = []

    # adding a new season to the list
    query = "insert into num_of_seasons(name) values('new season')"
    run_sql(query, 'post')
    first_round = False
    query = "select season from num_of_seasons order by season desc limit 1"
    season_num, = run_sql(query)[0]
    query = f"create table season_games{season_num} (game_id serial primary key, team1 varchar not null, team2 varchar not null, team1_scored int, team2_scored int, points_team1 int, points_team2 int )"
    run_sql(query, 'post')

    # Menu
    print('Please select an options from the list below:')
    user_input = ''
    while (user_input != '1' and user_input != '2'):
        print('(1) Instructions')
        print('(2) Start a season!')
        user_input = input('Enter your choice: ')

    # instruction
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

    # user decided to start a season
    elif user_input == '2':

        # pick teams for the competition
        print('Enter at least 2 competitors in this league, to stop write "stop".')
        competitor = ''
        # making sure that the teams exists and that there are more than 1 team
        while competitor.lower() != 'stop' or len(
                list(filter(lambda a: a != 'stop', competitors))) <= 1 and best_team_rating == 0:
            competitor = input('Enter here: ')
            club_info = data[data['club_name'] == competitor]
            starting_players = club_info.sort_values(by='overall', ascending=False).head(11)
            best_team_rating = starting_players['overall'].sum()
            if best_team_rating != 0:
                competitors.append(competitor)

        competitors = list(filter(lambda a: a != 'stop', competitors))
        def_stats = []
        att_stats = []
        counter = 1
        # getting the defensive and attacking stats of the teams
        for team in competitors:
            # picks the info about the players from the club
            club_info = data[data['club_name'] == team]

            # picks defence rating
            best_def_info = club_info.sort_values(by='defending', ascending=False).head(5)
            def_mean = best_def_info['defending'].mean()
            def_stats.append(def_mean)

            # picks attack rating
            best_att_info = club_info.sort_values(by='shooting', ascending=False).head(5)
            att_mean = best_att_info['shooting'].mean()
            att_stats.append(att_mean)

        # calculating the goals scored by each team depending on the attacking and defensive ratings
        # then setting up the matches
        for index1, team1 in enumerate(competitors):
            for index2, team2 in enumerate(competitors):
                if team1 != team2:

                    # calculate the ratio between the attack end the defence
                    team1_scored = att_stats[index1] ** 6 / def_stats[index2]
                    team2_scored = att_stats[index2] ** 6 / def_stats[index1]

                    # calculating the average goals for team1
                    prob_team1_scored = team1_scored / (team1_scored + team2_scored)
                    # calculating the average goals for team2
                    prob_team2_scored = team2_scored / (team1_scored + team2_scored)

                    # randomly choosing a goals number for each team around their predicted average goals
                    goals_team1 = np.random.poisson(int((prob_team1_scored) * 5), 5)[0]
                    goals_team2 = np.random.poisson(int((prob_team2_scored) * 5), 5)[0]

                    # Game info
                    print(f"Game No.{counter}")
                    print(f"{team1} vs. {team2}")
                    print("Final Score:")
                    print(f"{goals_team1} : {goals_team2}")

                    # getting the winner and giving them points accordingly
                    # win = 3 point
                    # draw = 1 point
                    # lose = 0 points
                    if goals_team1 > goals_team2:
                        points_team1 = 3
                        points_team2 = 0
                    elif goals_team2 > goals_team1:
                        points_team2 = 3
                        points_team1 = 0
                    else:
                        points_team1 = 1
                        points_team2 = 1

                    # inserting the information to a table
                    query = f"insert into season_games{season_num}(team1, team2, team1_scored, team2_scored, points_team1, points_team2) values ('{team1}', '{team2}', {goals_team1}, {goals_team2}, {points_team1}, {points_team2})"
                    run_sql(query, 'post')

        # wrapping up the season.
        # getting all the 'home' teams points
        query = f"create view teams1_points_season{season_num} as select team1,sum(points_team1), sum(team1_scored - team2_scored) as goal_diff from season_games{season_num} group by team1"
        run_sql(query, 'post')

        # getting all the 'away' teams points
        query = f"create view teams2_points_season{season_num} as select team2,sum(points_team2), sum(team2_scored - team1_scored) as goal_diff from season_games{season_num} group by team2"
        run_sql(query, 'post')

        # joining the tables
        query = f"create view all_points_season{season_num} as select * from teams1_points_season{season_num} union select * from teams2_points_season{season_num}"
        run_sql(query, 'post')

        # returning the table
        query = f"select team1, sum(sum) as points, sum(goal_diff) as goal_difference from all_points_season{season_num} group by team1 order by points desc, goal_difference desc"
        table = run_sql(query)

        # printing the info
        print(f"This is the end of the season's table:")
        print('location | Team | Points | goal difference)')
        print('--------------------')
        for index, stats in enumerate(table):
            (team_name, team_point, goal_dif) = stats
            if index == 0:
                champions = team_name
            print(f"{index + 1} | {team_name} | {team_point} | {goal_dif}")
            print('--------------------')

        print(f"{champions} are the Ultimate CHAMPIONS!!!! ")

        # Finish the season
        playing = False
