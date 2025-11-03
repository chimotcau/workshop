import pygame, sys
import time
from engine_core import Board, WHITE, BLACK
from bot import RandomBot

CELL = 80
BG1 = (238, 238, 210)
BG2 = (118, 150, 86)
HIGHLIGHT = (255, 180, 0)

def draw_board(screen, board, selected, targets,
               white_img, black_img, white_king_img, black_king_img):
    s = board.size
    for r in range(s):
        for c in range(s):
            rect = pygame.Rect(c * CELL, r * CELL, CELL, CELL)
            pygame.draw.rect(screen, BG1 if (r + c) % 2 == 0 else BG2, rect)
            p = board.piece_at(r, c)
            if p:
                img = white_king_img if (p.color == WHITE and p.king) else \
                      black_king_img if (p.color == BLACK and p.king) else \
                      white_img if p.color == WHITE else black_img
                img_rect = img.get_rect(center=rect.center)
                screen.blit(img, img_rect)

    if selected:
        r, c = selected
        pygame.draw.rect(screen, HIGHLIGHT, pygame.Rect(c * CELL, r * CELL, CELL, CELL), 3)
    for t in targets:
        pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(t[1] * CELL, t[0] * CELL, CELL, CELL), 3)

def pos_from_mouse(pos):
    return (pos[1] // CELL, pos[0] // CELL)

def draw_menu(screen, buttons, font):
    screen.fill((40, 40, 40))
    title_font = pygame.font.SysFont(None, 80)
    title = title_font.render("CHECKERS", True, (255, 255, 255))
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 80))

    for text, rect in buttons.items():
        pygame.draw.rect(screen, (90, 90, 90), rect, border_radius=15)
        label = font.render(text, True, (255, 255, 255))
        screen.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))

def main():
    pygame.init()
    size = 8
    screen = pygame.display.set_mode((size * CELL, size * CELL))
    pygame.display.set_caption("CHECKERS")
    clock = pygame.time.Clock()

    white_img = pygame.image.load("assets/white_piece.png")
    black_img = pygame.image.load("assets/black_piece.png")
    white_king_img = pygame.image.load("assets/white_king.png")
    black_king_img = pygame.image.load("assets/black_king.png")
    white_img = pygame.transform.smoothscale(white_img, (CELL - 10, CELL - 10))
    black_img = pygame.transform.smoothscale(black_img, (CELL - 10, CELL - 10))
    white_king_img = pygame.transform.smoothscale(white_king_img, (CELL - 10, CELL - 10))
    black_king_img = pygame.transform.smoothscale(black_king_img, (CELL - 10, CELL - 10))

    for img in [white_img, black_img, white_king_img, black_king_img]:
        img = pygame.transform.smoothscale(img, (CELL - 10, CELL - 10))

    mode = "menu" 
    current = WHITE
    selected = None
    targets = []
    bot = None
    board = None

    font = pygame.font.SysFont(None, 50)
    buttons = {
        "Play PvP": pygame.Rect(160, 250, 340, 60),
        "Play PvB": pygame.Rect(160, 330, 340, 60),
        "Quit": pygame.Rect(160, 410, 340, 60)
    }

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if mode == "menu":
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    for text, rect in buttons.items():
                        if rect.collidepoint(mx, my):
                            if text == "Play PvP":
                                mode = "pvp"
                                board = Board()
                                current = WHITE
                            elif text == "Play PvB":
                                mode = "pvb"
                                board = Board()
                                bot = RandomBot(BLACK)
                                current = WHITE
                            elif text == "Quit":
                                pygame.quit()
                                sys.exit()

            elif mode in ("pvp", "pvb"):
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    if mode == "pvb" and bot and current == bot.color:
                        continue  

                    r, c = pos_from_mouse(pygame.mouse.get_pos())
                    if not board.in_bounds(r, c): continue
                    p = board.piece_at(r, c)

                    if selected is None:
                        if p and p.color == current:
                            selected = (r, c)
                            targets = [m.to for m in board._piece_moves(r, c, p)]
                    else:
                        chosen = None
                        moves = board._piece_moves(selected[0], selected[1], board.piece_at(selected[0], selected[1]))
                        for m in moves:
                            if m.to == (r, c): chosen = m; break
                        if chosen:
                            board.move_piece(chosen)
                            if board.is_terminal():
                                winner = board.winner()
                                print(f"Game Over! Winner: {winner}")
                                time.sleep(2)
                                mode = "menu"
                            else:
                                current = BLACK if current == WHITE else WHITE
                        selected = None
                        targets = []

        if mode == "pvb" and bot and current == bot.color and not board.is_terminal():
            pygame.time.delay(400)
            mv = bot.choose_move(board)
            if mv:
                board.move_piece(mv)
            if board.is_terminal():
                winner = board.winner()
                print(f"Game Over! Winner: {winner}")
                time.sleep(2)
                mode = "menu"
            else:
                current = WHITE if current == BLACK else BLACK

        screen.fill((0, 0, 0))
        if mode == "menu":
            draw_menu(screen, buttons, font)
        elif mode in ("pvp", "pvb"):
            draw_board(screen, board, selected, targets,
                       white_img, black_img, white_king_img, black_king_img)

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
