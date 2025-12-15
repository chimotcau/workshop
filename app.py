import pygame
import sys
from engine_core import Board, WHITE, BLACK
from bot import SmartBot
from utils import opponent
from config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from config import BG_LIGHT, BG_DARK, HIGHLIGHT_COLOR, TARGET_COLOR
from config import MENU_BG, BUTTON_COLOR, TEXT_COLOR, BOT_DELAY_MS

def load_images():
    images = {}
    files = {
        'white': 'assets/white_piece.png',
        'black': 'assets/black_piece.png',
        'white_king': 'assets/white_king.png',
        'black_king': 'assets/black_king.png'
    }
    
    try:
        for key, filename in files.items():
            image = pygame.image.load(filename)
            scaled = pygame.transform.smoothscale(image, (CELL_SIZE - 10, CELL_SIZE - 10))
            images[key] = scaled
    except pygame.error:
        pygame.quit()
        sys.exit()
    
    return images

def mouse_to_board(mouse_position):
    mouse_x, mouse_y = mouse_position
    board_row = mouse_y // CELL_SIZE
    board_col = mouse_x // CELL_SIZE
    return board_row, board_col

def draw_board(screen, board, selected, targets, images):
    board_size = board.size
    
    for row in range(board_size):
        for col in range(board_size):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, 
                             CELL_SIZE, CELL_SIZE)
            if (row + col) % 2 == 0:
                color = BG_LIGHT
            else:
                color = BG_DARK
            pygame.draw.rect(screen, color, rect)
            
            piece = board.piece_at(row, col)
            if piece:
                if piece.color == WHITE:
                    if piece.king:
                        image_key = 'white_king'
                    else:
                        image_key = 'white'
                else:
                    if piece.king:
                        image_key = 'black_king'
                    else:
                        image_key = 'black'
                
                image = images[image_key]
                image_rect = image.get_rect(center=rect.center)
                screen.blit(image, image_rect)

    if selected:
        select_row, select_col = selected
        highlight = pygame.Rect(select_col * CELL_SIZE, select_row * CELL_SIZE,
                              CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, highlight, 3)
    
    for target in targets:
        target_row, target_col = target
        target_rect = pygame.Rect(target_col * CELL_SIZE, target_row * CELL_SIZE,
                                CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, TARGET_COLOR, target_rect, 3)

def draw_menu(screen, buttons, font):
    screen.fill(MENU_BG)
    title_font = pygame.font.SysFont(None, 80)
    title = title_font.render("PODDAVKI", True, TEXT_COLOR)
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 80))
    
    for text, rect in buttons.items():
        pygame.draw.rect(screen, BUTTON_COLOR, rect, border_radius=15)
        label = font.render(text, True, TEXT_COLOR)
        label_x = rect.centerx - label.get_width() // 2
        label_y = rect.centery - label.get_height() // 2
        screen.blit(label, (label_x, label_y))

def get_legal_moves_for_piece(board, row, col, color):
    all_moves = board.get_all_legal_moves(color)
    return [move for move in all_moves if move.fr == (row, col)]

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("PODDAVKI - Giveaway Checkers")
    clock = pygame.time.Clock()

    images = load_images()
    
    game_mode = "menu"
    current_player = WHITE
    selected_position = None
    target_positions = []
    game_bot = None
    game_board = None
    last_bot_time = 0

    font = pygame.font.SysFont(None, 50)
    buttons = {
        "Play PvP": pygame.Rect(160, 250, 340, 60),
        "Play PvB": pygame.Rect(160, 330, 340, 60),
        "Quit": pygame.Rect(160, 410, 340, 60)
    }

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if game_mode == "menu":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    for text, rect in buttons.items():
                        if rect.collidepoint(mouse_x, mouse_y):
                            if text == "Play PvP":
                                game_mode = "pvp"
                                game_board = Board()
                                current_player = WHITE
                            elif text == "Play PvB":
                                game_mode = "pvb"
                                game_board = Board()
                                game_bot = SmartBot(BLACK)
                                current_player = WHITE
                            elif text == "Quit":
                                pygame.quit()
                                sys.exit()

            elif game_mode in ("pvp", "pvb"):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if game_mode == "pvb" and current_player == game_bot.color:
                        continue  

                    mouse_pos = pygame.mouse.get_pos()
                    row, col = mouse_to_board(mouse_pos)
                    
                    if not game_board.in_bounds(row, col):
                        continue
                    
                    piece = game_board.piece_at(row, col)

                    if selected_position is None:
                        if piece and piece.color == current_player:
                            selected_position = (row, col)
                            moves = get_legal_moves_for_piece(game_board, 
                                                             row, col, 
                                                             current_player)
                            target_positions = [move.to for move in moves]
                    else:
                        chosen_move = None
                        moves = get_legal_moves_for_piece(game_board, 
                                                         selected_position[0], 
                                                         selected_position[1], 
                                                         current_player)
                        for move in moves:
                            if move.to == (row, col):
                                chosen_move = move
                                break
                        
                        if chosen_move:
                            game_board.move_piece(chosen_move)
                            if game_board.is_terminal():
                                winner = game_board.winner()
                                print(f"Game Over! {winner} wins!")
                                pygame.time.wait(2000)
                                game_mode = "menu"
                            else:
                                current_player = opponent(current_player)
                        selected_position = None
                        target_positions = []

        if (game_mode == "pvb" and game_bot and 
            current_player == game_bot.color and not game_board.is_terminal()):
            current_time = pygame.time.get_ticks()
            if current_time - last_bot_time > BOT_DELAY_MS:
                bot_move = game_bot.choose_move(game_board)
                if bot_move:
                    game_board.move_piece(bot_move)
                if game_board.is_terminal():
                    winner = game_board.winner()
                    print(f"Game Over! {winner} wins!")
                    pygame.time.wait(2000)
                    game_mode = "menu"
                else:
                    current_player = WHITE
                last_bot_time = current_time

        if game_mode == "menu":
            draw_menu(screen, buttons, font)
        elif game_mode in ("pvp", "pvb"):
            draw_board(screen, game_board, selected_position, 
                      target_positions, images)

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
