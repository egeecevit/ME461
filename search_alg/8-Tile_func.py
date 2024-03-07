def heuristic(s):
  s = s.flatten()
  g = np.array(([1, 2, 3], [4, 5, 6], [7, 8, 0])).flatten()
  return sum((abs(s // 3 - g // 3) + abs(s % 3 - g % 3))[1:])

def node_gen(board):
  nodes = []
  moves = []
  zero_positions = np.argwhere(board == 0)
  row, col = zero_positions[0]
  mvs2apply = [[-1, 0], [1, 0], [0, -1], [0, 1]]

  for move in mvs2apply:
      node_col, node_row = col + move[1], row + move[0]
      if 0 <= node_row <= 2 and 0 <= node_col <= 2:
          node = board.copy()
          node[row, col], node[node_row, node_col] = node[node_row, node_col], 0
          nodes.append(node)
          moves.append(move)

  return nodes, moves

def aStar(Tile):
  board = Tile.Board
  goal_state = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
  queue = [(0, board, [], 0)]  # [hn, board, location, gn]
  visited = {}

  while queue:
      queue.sort(key=lambda x: x[0] + x[3])
      cost_val, current_state, location, fix_cost = queue.pop(0)

      if np.array_equal(current_state, goal_state):
          print('here')
          print(current_state)
          return location

      if visited.setdefault(tuple(current_state.flatten()), False):
          continue

      visited[tuple(current_state.flatten())] = True
      nodes, moves = node_gen(current_state)
      fix_cost += 1

      for i, node in enumerate(nodes):
          move = location + [moves[i]]
          node_cost = heuristic(node)
          queue.append((node_cost, node, move, fix_cost))
