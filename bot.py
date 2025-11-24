import random
from engine_core import WHITE, BLACK

class SmartBot:
    def __init__(self, color):
        self.color = color

    def evaluate_move(self, board, move):
        
        score = 0
        fr_r, fr_c = move.fr
        to_r, to_c = move.to
        piece = board.piece_at(fr_r, fr_c)

        score += 10 * len(move.captures)
        
        if piece and not piece.king:
            if self.color == WHITE and to_r == 0:
                score += 5
            elif self.color == BLACK and to_r == board.size - 1:
                score += 5

        if piece and not piece.king:
            if self.color == WHITE:
                score += fr_r - to_r  
            else:
                score += to_r - fr_r  

        return score

    def choose_move(self, board):
        all_moves = []
        for r in range(board.size):
            for c in range(board.size):
                p = board.piece_at(r, c)
                if p and p.color == self.color:
                    all_moves += board._piece_moves(r, c, p)

        if not all_moves:
            return None

        scored_moves = [(self.evaluate_move(board, m), m) for m in all_moves]
        max_score = max(score for score, _ in scored_moves)
        best_moves = [m for score, m in scored_moves if score == max_score]

        return random.choice(best_moves)
