import random
from engine_core import WHITE, BLACK

class RandomBot:
    def __init__(self, color):
        self.color = color

    def choose_move(self, board):
        all_moves = []
        for r in range(board.size):
            for c in range(board.size):
                p = board.piece_at(r, c)
                if p and p.color == self.color:
                    all_moves += board._piece_moves(r, c, p)
        if not all_moves:
            return None
        return random.choice(all_moves)
