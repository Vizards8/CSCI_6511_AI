import time


# create a class for the game board
class Board:
    def __init__(self, n, m):
        self.n = n
        self.m = m
        self.board = [[0 for _ in range(n)] for _ in range(n)]
        self.pos_score = [[n // 2 - max(abs(i - n // 2), abs(j - n // 2)) for j in range(n)] for i in range(n)]

    def is_valid_move(self, row, col):
        if not (0 <= row < self.n and 0 <= col < self.n):
            return False
        return self.board[row][col] == 0

    def has_neighbors(self, row, col):
        for i in range(max(0, row - 1), min(self.n, row + 2)):
            for j in range(max(0, col - 1), min(self.n, col + 2)):
                if i == row and j == col:
                    continue
                if self.board[i][j] != 0:
                    return True
        return False

    def is_win(self, player):
        # check rows
        for i in range(self.n):
            for j in range(self.n - self.m + 1):
                curr = [self.board[i][k] for k in range(j, j + self.m)]
                if curr == [player] * self.m:
                    return True

        # check columns
        for i in range(self.n - self.m + 1):
            for j in range(self.n):
                curr = [self.board[k][j] for k in range(i, i + self.m)]
                if curr == [player] * self.m:
                    return True

        # check 135 degree diagonal
        for i in range(self.n - self.m + 1):
            for j in range(self.n - self.m + 1):
                curr = [self.board[i + k][j + k] for k in range(self.m)]
                if curr == [player] * self.m:
                    return True

        # check 45 degree diagonal
        for i in range(self.m - 1, self.n):
            for j in range(self.n - self.m + 1):
                curr = [self.board[i - k][j + k] for k in range(self.m)]
                if curr == [player] * self.m:
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
        depth = 6
        _, row, col, _ = self.alphabeta(board, 0, self.symbol, float('-inf'), float('inf'), depth, start + 3000, [])
        print(f'Player {self.symbol} makes a move at [{row}, {col}]')
        print(f"Time cost: {'{:.2f}'.format(time.time() - start)} s")
        return row, col

    def alphabeta(self, board, depth, player, alpha, beta, max_depth, max_time, path):
        start = time.time()
        # check if the game is over or the maximum depth is reached
        if depth >= max_depth or time.time() > max_time:
            return None, None, None, path

        # create a list of possible moves and sort them based on the heuristic function
        moves = []
        for i in range(board.n):
            for j in range(board.n):
                if board.is_valid_move(i, j) and board.has_neighbors(i, j):
                    board.board[i][j] = player
                    score = self.heuristic(board, i, j, player)

                    if (self.symbol == player and score == float('inf')) or (
                            self.symbol == 3 - player and score == float('-inf')):
                        board.board[i][j] = 0
                        return score, i, j, path + [[i, j]]

                    board.board[i][j] = 0
                    moves.append((score, i, j))
        if player == self.symbol:
            moves.sort(reverse=True)
        else:
            moves.sort()

        if not moves:
            return None, board.n // 2, board.n // 2, None

        # print(f"depth: {depth}, time_cost: {time.time() - start}")

        # recursively evaluate all possible moves and choose the best one
        best_score = float('-inf') if player == self.symbol else float('inf')
        best_row, best_col = None, None
        best_path = []

        for id, (h_score, i, j) in enumerate(moves):
            board.board[i][j] = player
            score, _, _, move_path = self.alphabeta(board, depth + 1, 3 - player, alpha, beta, max_depth, max_time,
                                                    path + [[i, j]])
            if not score:
                score = h_score
            if depth == 0:
                print(
                    f"{id + 1}/{len(moves)} Player {player} tries ({i}, {j}), score: {score}, h_score: {h_score}, moves: {move_path}")
            # if depth == 1:
            #     print(
            #         f"depth{depth} {id + 1}/{len(moves)} Player {player} tries ({i}, {j}), score: {score}, h_score: {h_score}, moves: {move_path}")
            #     print(f"time cost: {time.time() - start}")
            board.board[i][j] = 0

            if player == self.symbol:
                if score == float('inf'):
                    return score, i, j, move_path

                if score > best_score:
                    best_score = score
                    best_row = i
                    best_col = j
                    best_path = move_path
                    alpha = max(alpha, score)
                    if beta <= alpha:
                        # if depth <= 1:
                        #     print(f"depth{depth} {id}/{len(moves)} alpha-beta")
                        break
            else:
                if score == float('-inf'):
                    return score, i, j, move_path

                if score < best_score:
                    best_score = score
                    best_row = i
                    best_col = j
                    best_path = move_path
                    beta = min(beta, score)
                    if beta <= alpha:
                        # if depth <= 1:
                        #     print(f"depth{depth} {id}/{len(moves)} alpha-beta")
                        break

        # if all moves will fail, just pick one
        if not best_row and not best_col:
            best_score, best_row, best_col, best_path = score, i, j, move_path

        # print(f"depth: {depth}, time_cost: {time.time() - start}")

        return best_score, best_row, best_col, best_path

    def heuristic(self, board, row, col, player):
        # count the number of consecutive symbols in each direction (horizontally, vertically, diagonally)
        win_length = board.m - 1
        map = {i: 0 for i in range(board.n + 1)}

        # horizontal direction
        curr = 1
        for k in range(1, win_length + 1):
            if 0 <= col - k < board.n and board.board[row][col - k] == player:
                curr += 1
            else:
                break
        for k in range(1, win_length + 1):
            if 0 <= col + k < board.n and board.board[row][col + k] == player:
                curr += 1
            else:
                break
        map[curr] += 1

        # vertical direction
        curr = 1
        for k in range(1, win_length + 1):
            if 0 <= row - k < board.n and board.board[row - k][col] == player:
                curr += 1
            else:
                break
        for k in range(1, win_length + 1):
            if 0 <= row + k < board.n and board.board[row + k][col] == player:
                curr += 1
            else:
                break
        map[curr] += 1

        # diagonal direction (top-left to bottom-right)
        curr = 1
        for k in range(1, win_length + 1):
            if 0 <= row - k < board.n and 0 <= col - k < board.n and board.board[row - k][col - k] == player:
                curr += 1
            else:
                break
        for k in range(1, win_length + 1):
            if 0 <= row + k < board.n and 0 <= col + k < board.n and board.board[row + k][col + k] == player:
                curr += 1
            else:
                break
        map[curr] += 1

        # diagonal direction (bottom-left to top-right)
        curr = 1
        for k in range(1, win_length + 1):
            if 0 <= row + k < board.n and 0 <= col - k < board.n and board.board[row + k][col - k] == player:
                curr += 1
            else:
                break
        for k in range(1, win_length + 1):
            if 0 <= row - k < board.n and 0 <= col + k < board.n and board.board[row - k][col + k] == player:
                curr += 1
            else:
                break
        map[curr] += 1

        # calculate the score based on the number of consecutive symbols in each direction
        for i in range(board.m, board.n + 1):
            if map[i] > 0:
                return float('inf') if self.symbol == player else float('-inf')

        score = sum([(10 ** c) * map[c] for c in range(2, board.m)])

        return score if self.symbol == player else -score

    def heuristic_line(self, line, target, player, map):
        '''
        Find pattern:
        'XXX' block = 0, count = 3
        'OXXX' block = 1, count = 3
        '''
        opponent = 3 - player
        line = [opponent] + line + [opponent]
        n = len(line)
        i = 0

        while i < n:
            block = 0
            count = 0
            while i < n and line[i] != player:
                i += 1
            if i == 0 or line[i - 1] == opponent:
                block += 1
            while i < n and line[i] == player:
                count += 1
                i += 1
            if i == n or line[i] == opponent:
                block += 1
            if count != 0:
                key = str(count) + ',' + str(block)
                if not key in map:
                    map[key] = 0
                map[key] += 1

        return


# create the game loop
def play_game(n, m):
    board = Board(n, m)
    players = [Player(1), Player(2)]
    current_player = 0

    # # debug
    # board.board = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #                [0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0],
    #                [0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0],
    #                [0, 0, 0, 0, 0, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0],
    #                [0, 0, 0, 0, 0, 0, 2, 1, 2, 2, 0, 0, 0, 0, 0],
    #                [0, 0, 0, 0, 0, 0, 0, 1, 2, 0, 1, 0, 0, 0, 0],
    #                [0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 0, 1, 0, 0, 0],
    #                [0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0],
    #                [0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 1, 0, 0, 0],
    #                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

    # show initial board
    print(f'Initial board:')
    board.print_board()

    while True:
        print(f"Player {players[current_player].symbol}'s turn to make a move:")
        row, col = players[current_player].get_move(board)
        board.board[row][col] = players[current_player].symbol
        board.print_board()

        if board.is_win(players[current_player].symbol):
            print(f"Player {players[current_player].symbol} wins!")
            return

        if board.is_draw():
            print("It's a draw.")
            return

        current_player = 1 - current_player


if __name__ == '__main__':
    # example usage
    play_game(12, 6)
