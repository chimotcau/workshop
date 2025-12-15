import random
from engine_core import WHITE, BLACK

class SmartBot:
    def __init__(self, color):
        self.color = color

    def evaluate_move(self, board, move):
        score = 0
        from_row, from_col = move.fr
        to_row, to_col = move.to
        piece = board.piece_at(from_row, from_col)

        score -= 20 * len(move.captures)
        
        if piece and not piece.king:
            if self.color == WHITE and to_row == 0:
                score -= 15
            elif self.color == BLACK and to_row == board.size - 1:
                score -= 15

        if piece and not piece.king:
            if self.color == WHITE:
                score += 3 * (from_row - to_row)
            else:
                score += 3 * (to_row - from_row)
        
        center_row = board.size // 2
        center_col = board.size // 2
        distance = abs(to_row - center_row) + abs(to_col - center_col)
        score += 5 * (board.size - distance)
        
        if to_col == 0 or to_col == board.size - 1:
            score -= 8
        if to_row == 0 or to_row == board.size - 1:
            score -= 8
            
        return score

    def choose_move(self, board):
        all_moves = board.get_all_legal_moves(self.color)
        
        if not all_moves:
            return None
        
        scored_moves = [(self.evaluate_move(board, move), move) 
                       for move in all_moves]
        min_score = min(score for score, _ in scored_moves)
        worst_moves = [move for score, move in scored_moves 
                      if score == min_score]
        
        return random.choice(worst_moves)
