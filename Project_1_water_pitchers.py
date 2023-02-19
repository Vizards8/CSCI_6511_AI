import heapq
import math
import time


def read_file(filename):
    with open(filename, 'r') as f:
        curr = f.readline().strip()
        capacities = [int(i) for i in curr.split(',')]
        curr = f.readline().strip()
        target = int(curr)
    return capacities, target


def A_star(capacities, target):
    # calculate h(n)
    def heuristic(state):
        remain = abs(target - state)
        h = math.ceil(remain / max_capacity)
        return h

    # corner case
    # if gcd is not divisible by target, return -1
    gcd_ = capacities[0]
    for i in capacities:
        gcd_ = math.gcd(gcd_, i)
    if target % gcd_ != 0:
        return -1, None

    max_capacity = max(capacities)
    n = len(capacities)
    ini_state = 0
    visited = set()
    visited.add(ini_state)
    waters = [0 for _ in range(n)]
    heap = [(heuristic(ini_state), 0, heuristic(ini_state), waters, ini_state, [])]

    while heap:
        f, g, h, curr_water, curr_state, curr_path = heapq.heappop(heap)

        # deque the answer, return
        if curr_state == target:
            return g, curr_path

        # pour any water pitcher -> the infinite one
        for i in range(n):
            # if the new state is visited, just skip
            if curr_state + capacities[i] in visited:
                continue
            new_water = curr_water[:]
            if new_water[i]:
                new_water[i] = 0
                new_g = g + 1
            else:
                new_g = g + 2
            # calculate the new state related variables
            new_path = curr_path[:]
            new_path.append(capacities[i])
            new_state = curr_state + capacities[i]
            new_h = heuristic(new_state)
            new_f = new_g + new_h
            visited.add(new_state)
            heapq.heappush(heap, (new_f, new_g, new_h, new_water, new_state, new_path))

        # pour the infinite one -> any water pitcher
        for i in range(n):
            # if the new state is invalid or visited, just skip
            if curr_state - capacities[i] < 0:
                continue
            if curr_state - capacities[i] in visited:
                continue
            new_water = curr_water[:]
            if new_water[i]:
                new_g = g + 2
            else:
                new_water[i] = 1
                new_g = g + 1
            # calculate the new state related variables
            new_path = curr_path[:]
            new_path.append(-capacities[i])
            new_state = curr_state - capacities[i]
            new_h = heuristic(new_state)
            new_f = new_g + new_h
            visited.add(new_state)
            heapq.heappush(heap, (new_f, new_g, new_h, new_water, new_state, new_path))
    return -1, None


# some test cases
def test(file_names):
    for file_name in file_names:
        start = time.time()
        capacities, target = read_file(file_name)
        print(f"file name: {file_name}")
        print(f"capacities: {capacities}")
        print(f"target: {target}")
        steps, path = A_star(capacities, target)
        end = time.time()
        print(f"steps: {steps}")
        print(f"path: {path}")
        print(f"time cost: {format(end - start, '.3f')}s\n")


# main function
if __name__ == '__main__':
    file_names = ['input.txt', 'input1.txt', 'input2.txt', 'input3.txt', 'input4.txt']
    test(file_names)
