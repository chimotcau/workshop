from copy import deepcopy

WHITE = 'white'
BLACK = 'black'
EMPTY = None

class Piece:
    def __init__(self, color, king=False):
        self.color = color
        self.king = king

    def __repr__(self):
        return f"{'W' if self.color == WHITE else 'B'}{'K' if self.king else ''}"

class Move:
    def __init__(self, fr, to, captures=None):
        self.fr = fr
        self.to = to
        self.captures = captures or []

    def __repr__(self):
        return f"Move({self.fr}->{self.to}, caps={self.captures})"

class Board:
    def __init__(self, size=8):
        self.size = size
        self.grid = [[EMPTY] * size for _ in range(size)]
        self.reset()

    def reset(self):
        board_size = self.size
        self.grid = [[EMPTY] * board_size for _ in range(board_size)]
        
        for row in range(3):
            for col in range(board_size):
                if (row + col) % 2 == 1:
                    self.grid[row][col] = Piece(BLACK)
        
        for row in range(board_size - 3, board_size):
            for col in range(board_size):
                if (row + col) % 2 == 1:
                    self.grid[row][col] = Piece(WHITE)
                    
    def in_bounds(self, row, col):
        return 0 <= row < self.size and 0 <= col < self.size

    def piece_at(self, row, col):
        return self.grid[row][col]

    def move_piece(self, move):
        from_row, from_col = move.fr
        to_row, to_col = move.to
        piece = self.grid[from_row][from_col]
        
        if not piece:
            return False
            
        self.grid[from_row][from_col] = EMPTY
        self.grid[to_row][to_col] = piece

        for cap_row, cap_col in move.captures:
            self.grid[cap_row][cap_col] = EMPTY

        if not piece.king:
            if piece.color == WHITE and to_row == 0:
                piece.king = True
            elif piece.color == BLACK and to_row == self.size - 1:
                piece.king = True
                
        return True

    def players_pieces(self, color):
        positions = []
        for row in range(self.size):
            for col in range(self.size):
                piece = self.grid[row][col]
                if piece and piece.color == color:
                    positions.append((row, col))
        return positions

    def get_all_legal_moves(self, color):
        all_moves = []
        has_captures = False
        
        for row in range(self.size):
            for col in range(self.size):
                piece = self.grid[row][col]
                if not piece or piece.color != color:
                    continue
                    
                moves = self.get_piece_moves(row, col)
                for move in moves:
                    if move.captures:
                        has_captures = True
                        all_moves.append(move)
                    elif not has_captures:
                        all_moves.append(move)
        
        if has_captures:
            return [move for move in all_moves if move.captures]
        
        return all_moves

    def get_piece_moves(self, row, col):
        piece = self.grid[row][col]
        if not piece:
            return []

        moves = []

        if piece.king:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        elif piece.color == WHITE:
            directions = [(-1, -1), (-1, 1)]
        else:
            directions = [(1, -1), (1, 1)]

        for delta_row, delta_col in directions:
            new_row = row + delta_row
            new_col = col + delta_col
            if (self.in_bounds(new_row, new_col) and 
                self.grid[new_row][new_col] is EMPTY):
                moves.append(Move((row, col), (new_row, new_col), []))

        capture_chains = []

        def dfs(current_row, current_col, grid, captured, current_piece):
            found = False
            
            if current_piece.king:
                jump_dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            elif current_piece.color == WHITE:
                jump_dirs = [(-1, -1), (-1, 1)]
            else:
                jump_dirs = [(1, -1), (1, 1)]

            for delta_row, delta_col in jump_dirs:
                middle_row = current_row + delta_row
                middle_col = current_col + delta_col
                land_row = current_row + 2 * delta_row
                land_col = current_col + 2 * delta_col
                
                if not (self.in_bounds(middle_row, middle_col) and 
                        self.in_bounds(land_row, land_col)):
                    continue
                    
                middle_piece = grid[middle_row][middle_col]
                if (middle_piece and middle_piece.color != current_piece.color and 
                    grid[land_row][land_col] is EMPTY and
                    (middle_row, middle_col) not in captured):
                    
                    found = True
                    new_grid = deepcopy(grid)
                    new_grid[current_row][current_col] = EMPTY
                    
                    new_piece = Piece(current_piece.color, current_piece.king)
                    if not new_piece.king:
                        if new_piece.color == WHITE and land_row == 0:
                            new_piece.king = True
                        elif new_piece.color == BLACK and land_row == self.size - 1:
                            new_piece.king = True
                    
                    new_grid[land_row][land_col] = new_piece
                    new_grid[middle_row][middle_col] = EMPTY
                    
                    dfs(land_row, land_col, new_grid, 
                        captured + [(middle_row, middle_col)], new_piece)
            
            if not found and captured:
                capture_chains.append(
                    Move((row, col), (current_row, current_col), captured.copy())
                )

        dfs(row, col, self.grid, [], piece)
        moves.extend(capture_chains)
        
        return moves

    def is_terminal(self):
        white_moves = self.get_all_legal_moves(WHITE)
        black_moves = self.get_all_legal_moves(BLACK)
        return not white_moves or not black_moves

    def winner(self):
        white_moves = self.get_all_legal_moves(WHITE)
        black_moves = self.get_all_legal_moves(BLACK)
        
        if not white_moves and not black_moves:
            return 'draw'
        if not white_moves:
            return WHITE
        if not black_moves:
            return BLACK
        
        return None
