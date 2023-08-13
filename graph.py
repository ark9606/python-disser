import json
import numpy as np
from queue import PriorityQueue
import constants as const

from blocks import Rock, Ore
from dump_truck import DumpTruck


class Graph:
  def __init__(self):
    self.adj_list = { }

  def __repr__(self):
    return json.dumps(self.adj_list, indent=2)

  def add_vertex(self, vertex_name):
    if vertex_name not in self.adj_list:
      self.adj_list[vertex_name] = { }

  def add_edge(self, vertex1, vertex2, weight):
    if vertex1 in self.adj_list and vertex2 in self.adj_list:
      self.adj_list[vertex1][vertex2] = weight
      self.adj_list[vertex2][vertex1] = weight

  def shortest_path(self, start_vert, env_vert):
    # distances from startVert to all others
    distances = { }

    # store vertices with distances to it from start vertex as priorities
    queue = PriorityQueue()

    # previous vertex for each vertex to get to the end
    previous = { }

    # build up initial state
    for vertex in self.adj_list:
      # init, as we did not go any vertex yet
      previous[vertex] = None

      if vertex == start_vert:
        # distance to same vertex is 0
        distances[vertex] = 0
        # to begin with start_vertex
        queue.put((0, vertex))
        continue

      # set the max possible distance to every vertex
      distances[vertex] = np.inf
      queue.put((np.inf, vertex))


    visited = {}
    # as long as there is something to visit
    while queue.qsize() > 0:
      # vertex with the smallest distance
      curr_vert = queue.get()[1]

      if curr_vert == env_vert:
        break

      # loop through all its neighbors
      for neighbour in self.adj_list[curr_vert]:
        if neighbour in visited:
          continue

        # distance from the very start to curr-neighbor/next-node
        total_dist = distances[curr_vert] + self.adj_list[curr_vert][neighbour]
        if total_dist < distances[neighbour]:
          # updating new smallest distance to neighbor
          distances[neighbour] = total_dist

          # updating previous - How we got to neighbor
          previous[neighbour] = curr_vert

          # add to queue with new (smallest - high) priority
          queue.put((total_dist, neighbour))

      visited[curr_vert] = True

    # go from end vertex to start vertex
    path = []
    temp = env_vert

    while temp:
      path.append(temp)
      # temp = previous[temp] if temp in previous else None
      temp = previous[temp]
    path.reverse()
    return path


graph = Graph()

graph.add_vertex('A')
graph.add_vertex('B')
graph.add_vertex('C')
graph.add_vertex('D')
graph.add_vertex('E')
graph.add_vertex('F')

graph.add_edge('A', 'B', 4)
graph.add_edge('A', 'C', 2)
graph.add_edge('B', 'E', 3)
graph.add_edge('C', 'D', 2)
graph.add_edge('C', 'F', 4)
graph.add_edge('D', 'F', 1)
graph.add_edge('D', 'E', 3)
graph.add_edge('E', 'F', 1)

# print('\nGraph:')
# print(graph)

# print('\nShortest path from A to E:')
# print(graph.shortest_path('A', 'E'))

# print('\nShortest path from A to F:')
# print(graph.shortest_path('A', 'F'))

# print('\nShortest path from B to D:')
# print(graph.shortest_path('B', 'D'))


# test graph
SIZE = 5
cell_map = []
for i in range(SIZE):
  row = []
  for k in range(SIZE):
    row.append(None)
  cell_map.append(row)

cell_map[1][4] = Rock(1, 4)
cell_map[2][3] = Rock(2, 3)
cell_map[3][2] = Rock(3, 2)
cell_map[3][4] = Ore(2, 1)
cell_map[0][0] = DumpTruck(0, 0)

# generate graph from map
map_graph = Graph()
for r in range(SIZE):
  for c in range(SIZE):
    map_graph.add_vertex(str(r) + '.' + str(c))

for r in range(SIZE):
  for c in range(SIZE):
    if cell_map[r][c] and cell_map[r][c].get_code() == const.GRID_CODE_ROCK:
      continue
    curr_vertex = str(r) + '.' + str(c)
    right_vertex = str(r) + '.' + str(c + 1) if c < SIZE - 1 else None
    down_vertex = str(r + 1) + '.' + str(c) if r < SIZE - 1 else None
    if right_vertex:
      if cell_map[r][c+1] is None or cell_map[r][c+1].get_code() == const.GRID_CODE_ORE:
        map_graph.add_edge(curr_vertex, right_vertex, 1)

    if down_vertex:
      if cell_map[r+1][c] is None or cell_map[r+1][c].get_code() == const.GRID_CODE_ORE:
        map_graph.add_edge(curr_vertex, down_vertex, 1)


print(map_graph)
print(map_graph.shortest_path('0.0', '3.4'))
