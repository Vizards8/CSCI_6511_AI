import heapq
import math
import time


def read_file(filename):
    # read input file
    with open(filename, 'r') as f:
        curr = f.readline().strip()
        capacities = [int(i) for i in curr.split(',')]
        curr = f.readline().strip()
        target = int(curr)
    return capacities, target


def A_star(capacities, target):
    # calculate h(n)
    def heuristic(state):
        remain = target - state[-1]

        h = 0
        for i in state[:-1][::-1]:
            if not i or remain - i < 0:
                continue
            h_old = math.ceil(remain / max_capacity)
            h_new = math.ceil((remain - i) / max_capacity) + 1
            if h_new <= h_old:
                remain -= i
                h += 1

        h += math.ceil(remain / max_capacity) * 2
        return h

    max_capacity = max(capacities)
    capacities.append(float('inf'))
    n = len(capacities)
    ini_state = tuple([0 for _ in range(n)])
    # use a set to store closed list
    visited = set()
    visited.add(ini_state)
    # use a heap to store open list
    heap = [(heuristic(ini_state), 0, heuristic(ini_state), ini_state)]
    while heap:
        f, g, h, curr_state = heapq.heappop(heap)

        # Find the answer, return total steps
        if curr_state[-1] == target:
            return g

        # Fill one water pitcher
        for i in range(n - 1):
            new_state = list(curr_state)
            new_state[i] = capacities[i]
            new_g, new_h = g + 1, heuristic(new_state)
            new_f = new_g + new_h
            new_state = tuple(new_state)
            # check the new state is not visited
            if not new_state in visited:
                visited.add(new_state)
                heapq.heappush(heap, (new_f, new_g, new_h, new_state))

        # Empty one water pitcher
        for i in range(n - 1):
            new_state = list(curr_state)
            new_state[i] = 0
            new_g, new_h = g + 1, heuristic(new_state)
            new_f = new_g + new_h
            new_state = tuple(new_state)
            # check the new state is not visited
            if not new_state in visited:
                visited.add(new_state)
                heapq.heappush(heap, (new_f, new_g, new_h, new_state))

        # Pour ith water pitcher -> jth water pitcher
        # or ith water pitcher <- jth water pitcher
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue

                new_state = list(curr_state)

                # ith water pitcher -> jth water pitcher
                if new_state[i] + new_state[j] > capacities[j]:
                    new_state[i] = new_state[i] + new_state[j] - capacities[j]
                    new_state[j] = capacities[j]
                else:
                    new_state[j] = new_state[i] + new_state[j]
                    new_state[i] = 0
                new_g, new_h = g + 1, heuristic(new_state)
                new_f = new_g + new_h
                new_state = tuple(new_state)
                # check the new state is not visited
                if new_state[-1] <= target and not new_state in visited:
                    visited.add(new_state)
                    heapq.heappush(heap, (new_f, new_g, new_h, new_state))

                # ith water pitcher <- jth water pitcher
                new_state = list(curr_state)
                if new_state[i] + new_state[j] > capacities[i]:
                    new_state[j] = new_state[i] + new_state[j] - capacities[i]
                    new_state[i] = capacities[i]
                else:
                    new_state[j] = 0
                    new_state[i] = new_state[i] + new_state[j]
                new_g, new_h = g + 1, heuristic(new_state)
                new_f = new_g + new_h
                new_state = tuple(new_state)
                # check the new state is not visited
                if new_state[-1] <= target and not new_state in visited:
                    visited.add(new_state)
                    heapq.heappush(heap, (new_f, new_g, new_h, new_state))
    return -1


# some test cases
def test(file_names):
    for file_name in file_names:
        start = time.time()
        capacities, target = read_file(file_name)
        print(f"file name: {file_name}")
        print(f"capacities: {capacities}")
        print(f"target: {target}")
        res = A_star(capacities, target)
        end = time.time()
        print(f"res: {res}")
        print(f"time cost: {format(end - start, '.3f')}s\n")


# main function
if __name__ == '__main__':
    file_names = ['input.txt', 'input1.txt', 'input2.txt', 'input3.txt']
    test(file_names)
