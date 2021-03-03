import pandas as pd
import os
from prettytable import PrettyTable
import re

GROUP_ONE = ['Hull Kingston Redskins', 'Sydney Oilers', 'Perth Panthers', 'Glasgow Reapers', 'Merseyside Dockers', 'Brisbane Raiders', 'Darwin Dragons', 'Auckland Orcas', 'Adelaide Attitude', 'Gold Coast Crusade']
GROUP_TWO = ['Trafford Metro', 'Kensington Highrollers', 'Partick Pirates', 'Surfers Paradise Punks', 'Mandurah Maples', 'Byron Brewers', 'South Lancs Saints', 'Sunshine Coast Fury', 'Balmain Storm', 'Alice Springs Dingoes']

GAME_DATA_COLUMNS = {
                        'Knock-ons': '{} knocks-on',
                        'Great Runs': 'Great run by {}',
                        'Great Line Breaks': 'Great line break by {}',
                        'Kicks for Touch': '{} kicks for touch',
                        'Minor Injuries': '{} suffers minor injury.',
                        'Moderate Injuries': '{} suffers minor injury.',

                        'Major Injuries': '{} suffers major injury.'
}


def load_data(cur_rd_dir='data/', group=None, season_data=True):
    teams = []
    for t in os.listdir(cur_rd_dir):
        add_team = False
        if ' form ' in t:
            if not isinstance(group, type(None)):
                for team_name in group:
                    if team_name in t:
                        add_team = True
            else:
                add_team = True

            if add_team:
                team_name = ' '.join([x for x in t.split(' ')[:t.split(' ').index('form')]])
                team_data = pd.read_csv(cur_rd_dir + t, skiprows=[0, 1, 2], skipfooter=1, engine='python')
                team_data['Team'] = team_name
                team_data['Kick_Percentage'] = round((team_data['Goals'] / team_data['Attempts']) * 100)
                team_data['Total_Score'] = (team_data['Tries'] * 4) + (team_data['Goals'] * 2)
                teams.append(team_data)

    full_data = pd.concat(teams)

    rounds_to_include = previous_rounds(cur_rd_dir) if season_data else [cur_rd_dir]

    for previous_round in rounds_to_include:
        games = load_games(previous_round, group)
        for game in games:
            full_data = stats_from_game(previous_round, game, full_data)

    return full_data


def generate_stat_text(form_data, stat, n=20, order_type='largest', return_text=False):
    if stat[0] == '-':
        order_type = 'smallest'
        stat = stat[1:]

    if order_type == 'largest':
        stat_data = form_data.nlargest(n, [stat])
    elif order_type == 'smallest':
        stat_data = form_data.nsmallest(n, [stat])

    players = stat_data['Name'].values
    teams = stat_data['Team'].values
    values = stat_data[stat].values

    if return_text:
        table = PrettyTable()
        table.field_names = ['#', 'Name', 'Team', stat]

        for n, p in enumerate(players):
            table.add_row([n + 1, p, teams[n], values[n]])

        return table.get_string()


def save_stats_text(teams, stats, n=20, save_title='', title_add='', season_data=True):
    stat_text = ''
    for stat in stats:
        stat_title = title_add + ' (Season Total)' if stat in GAME_DATA_COLUMNS.keys() and season_data else title_add
        stat_text += '\n\n{}{}\n'.format(stat + '(Lowest)' if stat[0] == '-' else stat, '' if stat_title == '' else ' - {}'.format(stat_title))
        stat_text += generate_stat_text(teams, stat, n, return_text=True)
        stat_text += '\n____\n'

    with open(save_title.replace('/', '') + '_textstats.txt', 'w') as f:
        f.write(stat_text)


def load_games(rd_dir, group):
    folder_games = [game for game in os.listdir(rd_dir) if re.match('[a-zA-Z ]+ v [a-zA-Z ]+.txt', game)]
    group_games = []
    for game in folder_games:
        team1, team2 = game[:-4].split(' v ')
        if team1 in group and team2 in group:
            group_games.append(game)

    return group_games


def previous_rounds(cur_rd_dir):
    cur_rd_dir = cur_rd_dir.replace('/', '')
    rd_start = cur_rd_dir.index('Rd')
    dir_without_round_n = cur_rd_dir[:rd_start] + 'Rd'
    current_round = int(cur_rd_dir[rd_start + 2:])

    return [dir_without_round_n + str(n) + '/' for n in range(current_round, 0, -1)]


def stats_from_game(rd_dir, game, form_df):
    player_re = '[a-zA-Z \'á]+'
    formatted_searches = [GAME_DATA_COLUMNS[search_str].format(player_re) for search_str in GAME_DATA_COLUMNS.keys()]
    raw_event_text = [GAME_DATA_COLUMNS[event].replace(' {}', '').replace('{} ', '') for event in GAME_DATA_COLUMNS.keys()]

    with open(rd_dir + game) as f:
        game_data = ''.join(f.readlines())

    for title in GAME_DATA_COLUMNS.keys():
        if title not in list(form_df.columns):
            form_df[title] = 0

    for search_term_re, event_text, title in zip(formatted_searches, raw_event_text, GAME_DATA_COLUMNS):
        event_occurrences = [e.lstrip() for e in re.findall(search_term_re, game_data)]
        for occurrence in event_occurrences:
            player = occurrence.replace(event_text, '')
            if player[-1] == ' ':
                player = player[:-1]
            else:
                player = player[1:]
            form_df.loc[form_df['Name'] == player, title] += 1

    return form_df

# ---------------------------------------------------------------------------------------------------------------------
# Only edit the next three lines


current_round_directory = '2021Rd2/'    # The current round directory
title_to_add = ' Rd2'                   # The title to add
include_season_data = True              # This can be True or False (make sure to include the capital letter at the start)
                                        # True means that great runs, etc. are counted from all previous rounds
                                        # False means that great runs, etc. are only counted from the current round

# Don't change anything below this
# ---------------------------------------------------------------------------------------------------------------------

stats_to_save = ['health', 'Form', '-Form', 'Kick_Percentage', 'Tries', 'POM_Points', 'Games', 'ReserveGames', 'Goals', 'Total_Score'] + list(GAME_DATA_COLUMNS.keys())

g1 = load_data(cur_rd_dir=current_round_directory, group=GROUP_ONE, season_data=include_season_data)
g2 = load_data(cur_rd_dir=current_round_directory, group=GROUP_TWO, season_data=include_season_data)

save_stats_text(g1, stats_to_save, save_title='{}_group_one'.format(current_round_directory), title_add=title_to_add, season_data=include_season_data)
save_stats_text(g2, stats_to_save, save_title='{}_group_two'.format(current_round_directory), title_add=title_to_add, season_data=include_season_data)
