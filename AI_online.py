import json
import time

import requests


# create a class for the game board
class Board:
    def __init__(self, n, m):
        self.n = n
        self.m = m
        self.board = [[0 for _ in range(n)] for _ in range(n)]

    def is_valid_move(self, row, col):
        if not (0 <= row < self.n and 0 <= col < self.n):
            return False
        if self.board[row][col] == 0:
            return True
        return False

    def make_move(self, row, col, player):
        if self.is_valid_move(row, col):
            self.board[row][col] = player
            return True
        return False

    def is_win(self, player):
        # check rows
        for i in range(self.n):
            for j in range(self.n - self.m + 1):
                curr = [self.board[i][k] for k in range(j, j + self.m)]
                if all(k == player for k in curr):
                    return True

        # check columns
        for i in range(self.n - self.m + 1):
            for j in range(self.n):
                curr = [self.board[k][j] for k in range(i, i + self.m)]
                if all(k == player for k in curr):
                    return True

        # check 135 degree diagonal
        for i in range(self.n - self.m + 1):
            for j in range(self.n - self.m + 1):
                curr = [self.board[i + k][j + k] for k in range(self.m)]
                if all(k == player for k in curr):
                    return True

        # check 45 degree diagonal
        for i in range(self.m - 1, self.n):
            for j in range(self.n - self.m + 1):
                curr = [self.board[i - k][j + k] for k in range(self.m)]
                if all(k == player for k in curr):
                    return True

        return False

    def is_draw(self):
        for row in self.board:
            if 0 in row:
                return False
        return True

    def print_board(self):
        print(' ' * 4, end='')
        for i in range(self.n):
            print('{:<3d}'.format(i), end='')
        print()
        for id, row in enumerate(self.board):
            print('{:2d}'.format(id), row)


# create a class for the player
class Player:
    def __init__(self, symbol):
        self.symbol = symbol

    def get_move(self, board):
        print('Finding the best move...')
        start = time.time()

        # use iterative deepening search with move ordering to determine the best move
        depth = 4
        while True:
            _, row, col, _ = self.alphabeta(board, 0, self.symbol, float('-inf'), float('inf'), depth, start + 30, [])
            if row is not None and col is not None:
                print(f'Player {self.symbol} makes a move at [{row}, {col}]')
                print(f"Time cost: {'{:.2f}'.format(time.time() - start)} s")
                return row, col
            depth += 1

    def alphabeta(self, board, depth, player, alpha, beta, max_depth, max_time, path):
        # check if the game is over or the maximum depth is reached
        if board.is_win(self.symbol):
            return 1, None, None, path
        elif board.is_win(3 - self.symbol):
            return -1, None, None, path
        elif board.is_draw() or depth >= max_depth or time.time() > max_time:
            return 0, None, None, path

        # Check for immediate wins and defensive play
        if self.symbol == player:
            win_score = 1
            opponent_win_score = -1
        else:
            win_score = -1
            opponent_win_score = 1

        for i in range(board.n):
            for j in range(board.n):
                if board.is_valid_move(i, j):
                    board.make_move(i, j, player)
                    if board.is_win(player):
                        board.board[i][j] = 0
                        return win_score, i, j, path + [[i, j]]
                    board.board[i][j] = 0

        for i in range(board.n):
            for j in range(board.n):
                if board.is_valid_move(i, j):
                    board.make_move(i, j, 3 - player)
                    if board.is_win(3 - player):
                        board.board[i][j] = 0
                        # Make the defensive move to prevent the opponent from winning
                        board.make_move(i, j, player)
                        score, _, _, move_path = self.alphabeta(board, depth + 1, 3 - player, alpha, beta, max_depth,
                                                                max_time, path + [[i, j]])
                        board.board[i][j] = 0
                        return score, i, j, move_path
                    board.board[i][j] = 0

        # create a list of possible moves and sort them based on the heuristic function
        moves = []
        for i in range(board.n):
            for j in range(board.n):
                if board.is_valid_move(i, j):
                    # restrict the search of row and col
                    curr = []
                    for row in range(max(0, i - 1), min(board.n, i + 2)):
                        for col in range(max(0, j - 1), min(board.n, j + 2)):
                            curr.append(board.board[row][col])
                    if all(k == 0 for k in curr):
                        continue

                    score = self.heuristic(board, i, j, player)
                    moves.append((score, i, j))
        moves.sort(reverse=True)
        if not moves:
            moves.append((None, board.n // 2, board.n // 2))

        # recursively evaluate all possible moves and choose the best one
        best_score = float('-inf') if player == self.symbol else float('inf')
        best_row, best_col = None, None
        best_path = []

        for id, (_, i, j) in enumerate(moves):
            board.make_move(i, j, player)
            score, _, _, move_path = self.alphabeta(board, depth + 1, 3 - player, alpha, beta, max_depth, max_time,
                                                    path + [[i, j]])
            if depth == 0:
                print(f"{id + 1}/{len(moves)} Player {player} tries ({i}, {j}), score: {score}, paths: {move_path}")
            board.board[i][j] = 0

            if player == self.symbol:
                if score == 1:
                    return score, i, j, move_path

                if score > best_score:
                    best_score = score
                    best_row = i
                    best_col = j
                    best_path = move_path
                    alpha = max(alpha, score)
                    if beta <= alpha:
                        break
            else:
                if score == -1:
                    return score, i, j, move_path

                if score < best_score:
                    best_score = score
                    best_row = i
                    best_col = j
                    best_path = move_path
                    beta = min(beta, score)
                    if beta <= alpha:
                        break

        return best_score, best_row, best_col, best_path

    def heuristic(self, board, row, col, player):
        board.make_move(row, col, player)

        # # return a score for a given move based on its position on the board
        # score = 0
        # for i in range(max(0, row - 1), min(row + 2, board.n)):
        #     for j in range(max(0, col - 1), min(col + 2, board.n)):
        #         if board.board[i][j] == self.symbol:
        #             score += 1

        # count the number of consecutive symbols in each direction (horizontally, vertically, diagonally)
        win_length = max(0, board.m - 2)
        consecutives = [0] * 4

        # horizontal direction
        for i in range(max(0, col - win_length), min(board.n - win_length + 1, col + 1)):
            window = board.board[row][i:i + win_length]
            consecutives[0] += self.count_consecutives(window, player)

        # vertical direction
        for i in range(max(0, row - win_length), min(board.n - win_length + 1, row + 1)):
            window = [board.board[i + k][col] for k in range(win_length)]
            consecutives[1] += self.count_consecutives(window, player)

        # diagonal direction (top-left to bottom-right)
        for i in range(max(0, row - win_length), min(board.n - win_length + 1, row + 1)):
            for j in range(max(0, col - win_length), min(board.n - win_length + 1, col + 1)):
                window = [board.board[i + k][j + k] for k in range(win_length)]
                consecutives[2] += self.count_consecutives(window, player)

        # diagonal direction (bottom-left to top-right)
        for i in range(max(win_length - 1, row), min(board.n, row + win_length + 1)):
            for j in range(max(0, col - win_length), min(board.n - win_length + 1, col + 1)):
                window = [board.board[i - k][j + k] for k in range(win_length)]
                consecutives[3] += self.count_consecutives(window, player)

        # calculate the score based on the number of consecutive symbols in each direction
        score = sum([c ** 2 for c in consecutives])

        board.board[row][col] = 0

        return score

    def count_consecutives(self, window, player):
        consecutive_count = 0
        max_consecutive_count = 0

        for i in window:
            if i == player:
                consecutive_count += 1
                max_consecutive_count = max(max_consecutive_count, consecutive_count)
            else:
                consecutive_count = 0

        return max_consecutive_count


# create the game loop
def play_game(gameId, current_player):
    board, board_str, player_turn = get_board_online(gameId)
    players = [Player(1), Player(2)]

    # check if the game ends
    if board.is_win(players[current_player].symbol):
        print(f"Player {players[current_player].symbol} wins!")
        return False

    if board.is_win(players[1 - current_player].symbol):
        print(f"Player {players[1 - current_player].symbol} wins!")
        return False

    if board.is_draw():
        print("It's a draw.")
        return False

    if player_turn == current_player:
        # Print current board
        print(f"\nCurrent board:")
        print(board_str)

        print(f"Player {players[current_player].symbol}'s turn to make a move:")
        row, col = players[current_player].get_move(board)
        board.make_move(row, col, players[current_player].symbol)
        board.print_board()

        make_move_online(gameId, row, col)

    else:
        print(f"\rNot my turn", end='')
    return True


# create the game loop
def play_game_auto(gameId, current_player):
    while True:
        is_continue = play_game(gameId, current_player)
        if not is_continue:
            break
        time.sleep(2)


def create_game(teamId, boardSize=None, target=None):
    url = 'https://www.notexponential.com/aip2pgaming/api/index.php'
    headers = {'x-api-key': 'ea5f9601f61e077fda12', 'userid': '1165', 'User-Agent': 'PostmanRuntime/7.31.3'}
    data = {'type': 'game', 'gameType': 'TTT', 'teamId1': '1339', 'teamId2': teamId, 'boardSize': boardSize,
            'target': target}
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        response_dict = json.loads(response.text)
        gameId = response_dict['gameId']
        print(f'gameId: {gameId}')
    else:
        print('Error:', response.status_code)
    return


def get_board_online(gameId):
    url = 'https://www.notexponential.com/aip2pgaming/api/index.php'
    headers = {'x-api-key': 'ea5f9601f61e077fda12', 'userid': '1165', 'User-Agent': 'PostmanRuntime/7.31.3'}
    params = {'type': 'boardString', 'gameId': gameId}
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        response_dict = json.loads(response.text)
        board_str = response_dict['output']
        board_arr = board_str.split()
    else:
        print('Error:', response.status_code)
        return None

    n, m = len(board_arr), response_dict['target']
    board = Board(n, m)
    player1 = player2 = 0
    for i in range(n):
        for j in range(n):
            if board_arr[i][j] == 'O':
                board.board[i][j] = 1
                player1 += 1
            elif board_arr[i][j] == 'X':
                board.board[i][j] = 2
                player2 += 1
    if player1 == player2:
        player_turn = 0
    else:
        player_turn = 1

    return board, board_str, player_turn


def make_move_online(gameId, row, col):
    url = 'https://www.notexponential.com/aip2pgaming/api/index.php'
    headers = {'x-api-key': 'ea5f9601f61e077fda12', 'userid': '1165', 'User-Agent': 'PostmanRuntime/7.31.3'}
    data = {'type': 'move', 'teamId': '1339', 'gameId': gameId, 'move': f'{row},{col}'}
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        print(response.content)
    else:
        print('Error:', response.status_code)
    return


if __name__ == '__main__':
    # teamId2 = '1340'
    # boardSize = 12
    # target = 5
    # create_game(teamId2, boardSize, target)

    gameId = '3728'
    current_player = 0
    play_game_auto(gameId, current_player)
