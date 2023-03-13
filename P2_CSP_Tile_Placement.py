import os
import time
from collections import deque


def load_data(file_name):
    print('------ Analyze File ------')
    print(f'file name: {file_name}')

    # read the file
    with open(file_name, 'r') as f:
        # initialize the landscape
        while not f.readline().startswith('# Landscape'):
            pass
        landscape = []
        line = f.readline()
        while line != '\n':
            curr = []
            i = 0
            while i < len(line) - 1:
                curr.append(int(line[i]) if line[i] != ' ' else 0)
                i += 2
            landscape.append(curr[:])
            line = f.readline()
        print('------ Landscape ------')
        for i in landscape:
            print(i)

        # initialize the tiles
        while not f.readline().startswith('# Tiles'):
            pass
        tiles = dict()
        line = f.readline().strip()[1:-1].split(',')
        for i in line:
            curr = i.strip().split('=')
            tiles[curr[0]] = int(curr[1])
        print('------ Tiles ------')
        print(tiles)

        # initialize the targets
        while not f.readline().startswith('# Targets'):
            pass
        targets = []
        for _ in range(4):
            line = f.readline().strip()
            targets.append(int(line.split(':')[1]))
        print('------ Targets ------')
        print(targets)
    return landscape, tiles, targets


def forward_checking(landscape, tiles, targets, visible_bushes, curr_tiles, curr_targets, combo):
    '''
    :param curr_tiles: number of tiles used so far
    :param curr_targets: number of bushes visible so far
    :param combo: [[i, type]...], put 'type' tile to the position 'i'
    :return: true, if nothing violates the constraints, and vice versa
    '''
    n = len(landscape)
    num_per_row = n // 4

    for id, type in combo:
        curr_tiles[type] += 1
        for i in range(4):
            curr_targets[i] += visible_bushes[id][type][i]

    for i in range(4):
        if curr_targets[i] > targets[i]:
            return False
    for i in curr_tiles:
        if curr_tiles[i] > tiles[i]:
            return False
    return True


def AC_3(landscape, tiles, targets, visible_bushes, curr_tiles, curr_targets, domains):
    '''
    Applying AC-3: find all pairs first and apply remove_inconsistent_values() to every pair
    '''
    queue = deque([])
    for xi in domains:
        for xj in domains:
            if xi == xj:
                continue
            queue.append([xi, xj])
    while queue:
        xi, xj = queue.popleft()
        if remove_inconsistent_values(landscape, tiles, targets, visible_bushes, curr_tiles.copy(), curr_targets.copy(),
                                      xi, xj,
                                      domains):
            for xj in domains:
                if xi == xj or [xi, xj] in queue:
                    continue
                queue.append([xi, xj])


def remove_inconsistent_values(landscape, tiles, targets, visible_bushes, curr_tiles, curr_targets, xi, xj, domains):
    '''
    remove all inconsistent values in xi
    '''
    removed = False
    for value_i in domains[xi]:
        flag = False
        for value_j in domains[xj]:
            combo = [[xi, value_i], [xj, value_j]]
            if forward_checking(landscape, tiles, targets, visible_bushes, curr_tiles.copy(), curr_targets.copy(),
                                combo):
                flag = True
                break
        if not flag:
            domains[xi].remove(value_i)
            removed = True
    return removed


def backtrack(landscape, tiles, targets, visible_bushes, domains, id, res, curr_tiles, curr_targets):
    n = len(landscape)
    num_per_row = n // 4
    n_tiles = num_per_row * num_per_row

    # base case
    if id == n_tiles:
        if curr_targets == targets and curr_tiles == tiles:
            return res
        return

    # MRV: minimum remaining values
    mrv_orders = []
    for i in domains:
        curr = 9 - sum(visible_bushes[i]['EL_SHAPE'])
        mrv_orders.append([i, domains[i], len(domains[i]), curr])
    mrv_orders.sort(key=lambda x: (x[2], x[3]))
    curr_var = mrv_orders[0][0]
    curr_values = mrv_orders[0][1]
    domains.pop(curr_var)

    # LCV: least constraining value
    lcv_orders = []
    for value in curr_values:
        n_constrain = 0
        for i in range(n_tiles):
            if i == curr_var or res[i] != None:
                continue
            for j in domains[i]:
                combo = [[curr_var, value], [i, j]]
                if not forward_checking(landscape, tiles, targets, visible_bushes, curr_tiles.copy(),
                                        curr_targets.copy(), combo):
                    n_constrain += 1
        lcv_orders.append([value, n_constrain])
    lcv_orders.sort(key=lambda x: x[1])
    curr_values = [i[0] for i in lcv_orders]

    # try to assign a value to current variable
    for value in curr_values:
        res[curr_var] = value
        combo = [[curr_var, value]]
        curr_curr_tiles = curr_tiles.copy()
        curr_curr_targets = curr_targets.copy()
        curr_domains = {i: domains[i][:] for i in domains}
        if forward_checking(landscape, tiles, targets, visible_bushes, curr_curr_tiles, curr_curr_targets, combo):
            # Arc Consistency: AC-3
            AC_3(landscape, tiles, targets, visible_bushes, curr_curr_tiles.copy(), curr_curr_targets.copy(),
                 curr_domains)
            if [] in curr_domains.values():
                continue

            res1 = backtrack(landscape, tiles, targets, visible_bushes, curr_domains, id + 1, res, curr_curr_tiles,
                             curr_curr_targets)
            if res1:
                return res1
        res[curr_var] = None
    return


def CSP(landscape, tiles, targets):
    n = len(landscape)
    num_per_row = n // 4
    n_tiles = num_per_row * num_per_row

    # initial variables
    res = [None for _ in range(n_tiles)]

    # initial domains
    domains = dict()
    for i in range(n_tiles):
        if res[i] == None:
            if tiles['EL_SHAPE'] <= tiles['OUTER_BOUNDARY']:
                domains[i] = ['EL_SHAPE', 'OUTER_BOUNDARY', 'FULL_BLOCK']
            else:
                domains[i] = ['OUTER_BOUNDARY', 'EL_SHAPE', 'FULL_BLOCK']

    # initial tiles and targets
    curr_tiles = {'FULL_BLOCK': 0, 'OUTER_BOUNDARY': 0, 'EL_SHAPE': 0}
    curr_targets = [0, 0, 0, 0]

    # calculate the visible bushes for every case (position: tile)
    visible_bushes = dict()
    for id in range(n_tiles):
        visible_bushes[id] = {'FULL_BLOCK': [0, 0, 0, 0], 'OUTER_BOUNDARY': [0, 0, 0, 0], 'EL_SHAPE': [0, 0, 0, 0]}
        # this tile covers [x][y] to [x + 3][y + 3]
        x, y = id % num_per_row * 4, id // num_per_row * 4
        # EL_SHAPE
        for i in range(x + 1, x + 4):
            for j in range(y + 1, y + 4):
                if landscape[i][j] != 0:
                    visible_bushes[id]['EL_SHAPE'][landscape[i][j] - 1] += 1
        # OUTER_BOUNDARY
        for i in range(x + 1, x + 3):
            for j in range(y + 1, y + 3):
                if landscape[i][j] != 0:
                    visible_bushes[id]['OUTER_BOUNDARY'][landscape[i][j] - 1] += 1

    # backtrack begins
    res = backtrack(landscape, tiles, targets, visible_bushes, domains, 0, res, curr_tiles, curr_targets)

    # output result
    print('------ Find Result ------')
    for i, type in enumerate(res):
        print(f'{i} 4 {type}')
    return res


def check_result(landscape, res, targets):
    '''
    Put the result back to check if it is correct
    Cause this problem may have multiple solutions
    '''
    print('------ Check Result ------')
    n = len(landscape)
    num_per_row = n // 4

    # calculate the visible bushes
    visible = [0, 0, 0, 0]
    for id in range(len(res)):
        # this tile covers [x][y] to [x + 3][y + 3]
        x, y = id % num_per_row * 4, id // num_per_row * 4
        if res[id] == 'FULL_BLOCK':
            continue
        elif res[id] == 'OUTER_BOUNDARY':
            for i in range(x + 1, x + 3):
                for j in range(y + 1, y + 3):
                    if landscape[i][j] != 0:
                        visible[landscape[i][j] - 1] += 1
        elif res[id] == 'EL_SHAPE':
            for i in range(x + 1, x + 4):
                for j in range(y + 1, y + 4):
                    if landscape[i][j] != 0:
                        visible[landscape[i][j] - 1] += 1

    # check
    if visible == targets:
        print('PASS!')
    else:
        print('FAIL!')
    return


if __name__ == '__main__':
    file_name = 'test_cases/tilesproblem_1326658913086500.txt'

    # load data
    landscape, tiles, targets = load_data(file_name)

    # CSP
    start = time.time()
    res = CSP(landscape, tiles, targets)
    end = time.time()
    print(f"time cost: {format(end - start, '.3f')}s")

    # check the result
    check_result(landscape, res, targets)
