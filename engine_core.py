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
        s = self.size
        self.grid = [[EMPTY] * s for _ in range(s)]
        for r in range(3):
            for c in range(s):
                if (r + c) % 2 == 1:
                    self.grid[r][c] = Piece(BLACK)
        for r in range(s - 3, s):
            for c in range(s):
                if (r + c) % 2 == 1:
                    self.grid[r][c] = Piece(WHITE)
                    
    def in_bounds(self, r, c):
        return 0 <= r < self.size and 0 <= c < self.size

    def piece_at(self, r, c):
        return self.grid[r][c]

    def clone(self):
        return deepcopy(self)

    def move_piece(self, move: Move):
        fr = move.fr
        to = move.to
        p = self.grid[fr[0]][fr[1]]
        self.grid[fr[0]][fr[1]] = EMPTY
        self.grid[to[0]][to[1]] = p

        for cap in move.captures:
            self.grid[cap[0]][cap[1]] = EMPTY

        if p and not p.king:
            if p.color == WHITE and to[0] == 0:
                p.king = True
            elif p.color == BLACK and to[0] == self.size - 1:
                p.king = True

    def players_pieces(self, color):
        return [
            (r, c)
            for r in range(self.size)
            for c in range(self.size)
            if self.grid[r][c] and self.grid[r][c].color == color
        ]

    def get_all_legal_moves(self, color):
        normal_moves = []
        capture_moves = []
        for r in range(self.size):
            for c in range(self.size):
                p = self.grid[r][c]
                if not p or p.color != color:
                    continue
                for m in self._piece_moves(r, c, p):
                    if m.captures:
                        capture_moves.append(m)
                    else:
                        normal_moves.append(m)
        if capture_moves:
            maxlen = max(len(m.captures) for m in capture_moves)
            return [m for m in capture_moves if len(m.captures) == maxlen]
        return normal_moves

    def _piece_moves(self, r, c, piece):
        moves = []

        if piece.king:
            simple_dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        elif piece.color == WHITE:
            simple_dirs = [(-1, -1), (-1, 1)]  
        else:  
            simple_dirs = [(1, -1), (1, 1)]   

        for dr, dc in simple_dirs:
            nr, nc = r + dr, c + dc
            if self.in_bounds(nr, nc) and self.grid[nr][nc] is EMPTY:
                moves.append(Move((r, c), (nr, nc), []))

        capture_chains = []

        def dfs(cr, cc, grid_snapshot, captured):
            found = False
            
            if piece.king:
                jump_dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            elif piece.color == WHITE:
                jump_dirs = [(-1, -1), (-1, 1)]
            else:
                jump_dirs = [(1, -1), (1, 1)]

            for dr, dc in jump_dirs:
                mr, mc = cr + dr, cc + dc       
                lr, lc = cr + 2 * dr, cc + 2 * dc  
                if not (self.in_bounds(mr, mc) and self.in_bounds(lr, lc)):
                    continue
                mid_piece = grid_snapshot[mr][mc]
                if (
                    mid_piece
                    and mid_piece.color != piece.color
                    and grid_snapshot[lr][lc] is EMPTY
                    and (mr, mc) not in captured
                ):
                    found = True
                    new_grid = deepcopy(grid_snapshot)
                    new_grid[cr][cc] = EMPTY
                    new_grid[lr][lc] = piece
                    new_grid[mr][mc] = EMPTY
                    dfs(lr, lc, new_grid, captured + [(mr, mc)])
            if not found and captured:
                capture_chains.append(Move((r, c), (cr, cc), captured.copy()))

        dfs(r, c, self.grid, [])
        moves.extend(capture_chains)
        return moves

    def is_terminal(self):
        white_pieces = self.players_pieces(WHITE)
        black_pieces = self.players_pieces(BLACK)

        if not white_pieces or not black_pieces:
            return True

        white_moves = self.get_all_legal_moves(WHITE)
        black_moves = self.get_all_legal_moves(BLACK)

        if not white_moves or not black_moves:
            return True

        return False

    def winner(self):
        if not self.is_terminal():
            return None

        white_pieces = self.players_pieces(WHITE)
        black_pieces = self.players_pieces(BLACK)
        white_moves = self.get_all_legal_moves(WHITE)
        black_moves = self.get_all_legal_moves(BLACK)

        if not white_pieces and not black_pieces:
            return 'draw'
        if not white_pieces:
            return BLACK
        if not black_pieces:
            return WHITE

        if not white_moves and not black_moves:
            return 'draw'
        if not white_moves:
            return BLACK
        if not black_moves:
            return WHITE

        return 'draw'
