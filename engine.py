from copy import deepcopy

WHITE='White'
BLACK='Black'
EMPTY=None

class Piece:
    def __init__(self,color,king):
        king=False
        self.color = color
        self.king = king
    def __repr__(self):
        return f"{'W'if self.color==WHITE else 'B'}{'K'if self.king==1 else''}"
p = Piece(WHITE,king=True)
print('W' if p.color==WHITE else 'B')  # W


      
        
