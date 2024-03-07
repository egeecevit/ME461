class Solve8:
  def _init_(self):
    self.goal_state = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
    
  def _str_(self):
    return 'The first rule of Kaybedenler Club...Never mind'
    
  def heuristic(self, board):
    s = board.flatten()
    g = self.goal_state.flatten()
    return sum((abs(s // 3 - g // 3) + abs(s % 3 - g % 3))[1:])

  def node_gen(self, board):
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

  def Solve(self,Tile):
    initial_state = Tile.Board
    goal_state = self.goal_state
    queue = [(self.heuristic(initial_state), initial_state, [], 0)]  # [hn, board, location, gn]
    visited = set()

    while queue:
        queue.sort(key=lambda x: x[0] + x[3])
        cost_val, current_state, location, fix_cost = queue.pop(0)

        if np.array_equal(current_state, goal_state):
            return location

        if tuple(current_state.flatten()) in visited:
            continue

        visited.add(tuple(current_state.flatten()))
        nodes, moves = self.node_gen(current_state)
        fix_cost += 1

        for i, node in enumerate(nodes):
            move = location + [moves[i]]
            node_cost = self.heuristic(node) + fix_cost
            queue.append((node_cost, node, move, fix_cost))

    return None
