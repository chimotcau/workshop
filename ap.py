import pygame, sys
from engine_core import Board, WHITE, BLACK

# === CONFIG ===
CELL = 80
BG1 = (238, 238, 210)
BG2 = (118, 150, 86)
HIGHLIGHT = (255, 180, 0)

# === UI FUNCTIONS ===
def draw(screen, board, selected, targets,
         white_img, black_img, white_king_img, black_king_img):
    s = board.size
    for r in range(s):
        for c in range(s):
            rect = pygame.Rect(c * CELL, r * CELL, CELL, CELL)
            pygame.draw.rect(screen, BG1 if (r + c) % 2 == 0 else BG2, rect)

            p = board.piece_at(r, c)
            if p:
                if p.color == WHITE:
                    img = white_king_img if p.king else white_img
                else:
                    img = black_king_img if p.king else black_img
                img_rect = img.get_rect(center=rect.center)
                screen.blit(img, img_rect)

    if selected:
        r, c = selected
        pygame.draw.rect(screen, HIGHLIGHT, pygame.Rect(c * CELL, r * CELL, CELL, CELL), 3)

    for t in targets:
        pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(t[1] * CELL, t[0] * CELL, CELL, CELL), 3)


def pos_from_mouse(pos):
    return (pos[1] // CELL, pos[0] // CELL)


def draw_overlay(screen, text):
    """Draws a semi-transparent overlay with winner text."""
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))  # black transparent layer

    font = pygame.font.SysFont(None, 72, bold=True)
    label = font.render(text, True, (255, 255, 255))
    rect = label.get_rect(center=screen.get_rect().center)
    overlay.blit(label, rect)

    sub_font = pygame.font.SysFont(None, 36)
    sub_label = sub_font.render("Press ESC to quit", True, (220, 220, 220))
    sub_rect = sub_label.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 60))
    overlay.blit(sub_label, sub_rect)

    screen.blit(overlay, (0, 0))


# === MAIN LOOP ===
def main():
    pygame.init()
    size = 8
    board = Board(size=size)
    screen = pygame.display.set_mode((size * CELL, size * CELL))
    pygame.display.set_caption("Checkers")
    clock = pygame.time.Clock()

    # Load assets
    white_img = pygame.image.load("assets/white_piece.png")
    black_img = pygame.image.load("assets/black_piece.png")
    white_king_img = pygame.image.load("assets/white_king.png")
    black_king_img = pygame.image.load("assets/black_king.png")

    # Resize
    white_img = pygame.transform.smoothscale(white_img, (CELL - 10, CELL - 10))
    black_img = pygame.transform.smoothscale(black_img, (CELL - 10, CELL - 10))
    white_king_img = pygame.transform.smoothscale(white_king_img, (CELL - 10, CELL - 10))
    black_king_img = pygame.transform.smoothscale(black_king_img, (CELL - 10, CELL - 10))

    current = WHITE
    selected = None
    targets = []
    winner = None  # track winner

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if winner is not None:
                # Ignore moves when game ended
                continue

            if ev.type == pygame.MOUSEBUTTONDOWN:
                r, c = pos_from_mouse(pygame.mouse.get_pos())
                if not board.in_bounds(r, c):
                    continue

                p = board.piece_at(r, c)
                if selected is None:
                    # select your own piece
                    if p and p.color == current:
                        selected = (r, c)
                        targets = [m.to for m in board._piece_moves(r, c, p)]
                else:
                    # move or cancel
                    chosen = None
                    moves = board._piece_moves(selected[0], selected[1],
                                               board.piece_at(selected[0], selected[1]))
                    for m in moves:
                        if m.to == (r, c):
                            chosen = m
                            break
                    if chosen:
                        board.move_piece(chosen)
                        if board.is_terminal():
                            result = board.winner()
                            if result == WHITE:
                                winner = "White Wins!"
                            elif result == BLACK:
                                winner = "Black Wins!"
                            else:
                                winner = "Draw!"
                        else:
                            current = BLACK if current == WHITE else WHITE
                    selected = None
                    targets = []

        # draw board
        screen.fill((0, 0, 0))
        draw(screen, board, selected, targets, white_img, black_img, white_king_img, black_king_img)

        # draw overlay if ended
        if winner:
            draw_overlay(screen, winner)

        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()
