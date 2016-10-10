import os, datetime
directory = r'Games\\'
if not os.path.exists(directory):
    print('Games folder created!')
    os.makedirs(directory)
data = []
for file in os.listdir(directory):
    f = open(directory + file, 'r')
    for line in [line.split(',') for line in f.readlines()][4:]:
        data.append(line + [file[:file.index('form')-1]])


info_points = ['pos', 'pstn', 'att', 'def', 'kick', 'gkick', 'temp', 'health', 'Form', 'Games', 'ReserveGames', 'Tries', 'Goals', 'Attempts', 'Drop_Goals', 'POM_Points', 'Salary', 'Player_Code', 'Team', 'conver_rate']
stats = {}

for player in data[1:]:
    playerinfo = {}
    for info in enumerate(player[1:]):
        try:
            playerinfo[info_points[info[0]]] = int(info[1])
        except ValueError:
            playerinfo[info_points[info[0]]] = info[1]
    playerinfo['conver_rate'] = playerinfo['Goals'] / playerinfo['Attempts'] * 100 if playerinfo['Goals'] > 0 and playerinfo['Attempts'] > 0 else 0
    stats[player[0]] = playerinfo

                                     
def sort_stat(s, sorting_method):
    i = []
    for player in stats.keys():
        i.append([player, stats[player][s], stats[player]['Team']])

    sorting = 1 if sorting_method == '+' else -1
    players = []
    for x in [x for x in enumerate(sorted(i, key = lambda x : x[1]))][::sorting]:
        players.append('{}. {}: {} [{}]'.format(abs(len(stats.keys()) - x[0]) if sorting_method == '+' else x[0]+1, x[1][0], x[1][1], x[1][2]))
    return players

def player_info(identifier):
    for data in info_points:
          print('{}: {}'.format(data, stats[identifier][data]))

def create_stats_file(stats_file_max):
        file = open('stats.txt', 'w')
        file.write(str(datetime.datetime.now())+'\n')
        file.write('Sorting method: ' + 'ascending\n' if sorting_method == '+' else 'descending\n')
        for stat in info_points:
            file.write(stat+'\n')
            for player in sort_stat(stat, sorting_method)[-1 * stats_file_max:][::-1]:
                file.write('\t' + player+'\n')
        file.close()

stats_file_max = 10
sorting_method = '+'
while True:
    print('____________________\n[Type \'help\' for a list of valid commands]')
    inp = input('Please enter a player\'s name or ID, or enter a stat to rank players: ')
    if inp == '':
        break
    elif inp == 'help':
        while True:
            print('\nValid Commands:')
            commands = ['[stat name]', '[player name]', 'change_sorting_method', 'change_file_max', 'create_stats_file']
            for command in commands:
                print('\t' + command)
            x = input('Press enter to return to the program, or type a command for more information: ')
            if x == '':
                break
            elif x == 'stat name':
                for x in info_points:
                    print(x)
            elif x == 'player name':
                for player in stats.keys():
                    print(player)
            elif x == 'change_sorting_method':
                print('\nToggles the sorting method between high->low and low->high\n')
            elif x == 'change_file_max':
                print('\nChanges the amount of players listed per stat when creating an output file.\n')
            elif x == 'create_stats_file':
                print('\nCreates a file ranking the top 10 players of each stat. Uses the selected sorting method.')
            else:
                print('Invalid Input')
    elif inp == 'change_sorting_method':
        if sorting_method == '+':
            sorting_method = '-'
            print('Sorting stats from highest to lowest...')
        else:
            sorting_method = '+'
            print('Sorting stats from lowest to highest...')
    elif inp == 'change_file_max':
        new_max = input('The current max is {}. Please enter a new max: '.format(stats_file_max))
        try:
            stats_file_max = int(new_max)
        except:
            print('Invalid input!')
    elif inp in stats.keys():
        print(inp + '\n')
        player_info(inp)
    elif inp in info_points:
        for stat in sort_stat(inp, sorting_method):
            print(stat)
    elif inp == 'create_stats_file':
        create_stats_file(stats_file_max)
    else:
        print('Invalid Input')
    print('\nRestarting...')
