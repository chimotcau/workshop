WHITE='White'
BLACK='Black'
EMPTY=None
class Piece:
    def __init__(self,color,king=False):
        self.color=color
        self.king=king
    def __repr__(self):
        return f"{'W'if self.color==WHITE else 'B'}{'K'if self.king==1 else''}"
class Move:
    def __init__(self,current,next,captures):
        captures=None
        self.current=current
        self.next=next
        self.captures=captures or []
    def __repr__(self):
        return f"From {self.current} To {self.next}, Captures{self.captures}"
class Board:
    def __init__(self,size):
        size=8
        self.size=size
        self.grid=[[EMPTY]*size for i in range(size)]
        self.reset()    
    def reset(self):
        s=self.size
        self.grid=[[EMPTY]*s for i in range(s)]
        for i in range(3):
            for j in range(s):
                if((i+j)%2==1):
                    self.grid[i][j]=Piece(BLACK)
        for i in range(s-3,s):
            for j in range(s):
                if((i+j)%2==1):
                    self.grid[i][j]=Piece(WHITE)
    
   
    
    
    
   

           




      
        
