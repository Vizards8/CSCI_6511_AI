import heapq


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
        curr = state[-1]
        if (target - curr) % max_capacity == 0:
            h = (target - curr) // max_capacity
        else:
            h = (target - curr) // max_capacity + 1
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


# Here is for the test
if __name__ == '__main__':
    capacities, target = read_file('input.txt')
    res = A_star(capacities, target)
    print(f"res: {res}")
