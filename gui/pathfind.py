import collections


class Queue:
    def __init__(self):
        self.elements = collections.deque()

    def empty(self):
        return len(self.elements) == 0

    def put(self, x):
        self.elements.append(x)

    def get(self):
        return self.elements.popleft()


class Graph:
    def __init__(self, collisions):
        self.collisions = collisions
        self.width = len(collisions[0])
        self.height = len(collisions)

    def walkable(self, coor):
        x, y = coor
        if x < 0 or x > self.width - 1:
            return False
        if y < 0 or y > self.height - 1:
            return False
        if self.collisions[self.height - y - 1][x] > 0:
            return False
        return True

    def neighbors(self, coor):
        n = []
        x, y = coor

        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx = x + dx
            ny = y + dy
            if self.walkable((nx, ny)):
                n.append((nx, ny))

        for dx, dy in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            nx = x + dx
            ny = y + dy
            if (self.walkable((nx, ny)) and
                    self.walkable((nx, y)) and
                    self.walkable((x, ny))):
                n.append((nx, ny))

        return n


def breadth_first_search(collisions, start, goal):
    graph = Graph(collisions)
    frontier = Queue()
    frontier.put(start)
    came_from = {}
    came_from[start] = None

    while not frontier.empty():
        current = frontier.get()

        if current == goal:
            break

        for next in graph.neighbors(current):
            if next not in came_from:
                frontier.put(next)
                came_from[next] = current

    current = goal
    path = [current]
    while current != start:
        current = came_from[current]
        path.append(current)
    path.reverse()

    # simplify path
    spath = path[:1]
    for i in range(1, len(path) - 1):
        px, py = path[i - 1]
        cx, cy = path[i]
        nx, ny = path[i + 1]
        if nx - cx == cx - px and ny - cy == cy - py:
            continue
        spath.append(path[i])
    spath.append(path[-1])

    return spath
