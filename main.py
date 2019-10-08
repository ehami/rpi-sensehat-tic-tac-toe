"""
    -Eric Hamilton
    -Period 1
    -eng006
"""

from sense_hat import SenseHat
import time
import pygame  # See http://www.pygame.org/docs
from pygame.locals import *
import copy

sense = SenseHat()

WHITE = [255,255,255]
PLAYER_ONE = [255, 0, 0]
PLAYER_TWO = [0, 0, 255]
PLAYER_ONE_DIM = [0, 0, 0]
PLAYER_TWO_DIM = [0, 0, 0]
# 0, 0 = Top left
# 7, 7 = Bottom right


def set_pixels(pixels, color):
    for p in pixels:
        sense.set_pixel(p[0], p[1], color[0], color[1], color[2])


board = [x[:] for x in [["empty"] * 3] * 3]
game_mode = "undef"
turn = "one"
turn_number = 1
selected_square = [0, 0]  # x, y


def main():
    
    global board
    global game_mode
    global turn
    global turn_number
    global selected_square
    
    pygame.init()
    pygame.display.set_mode((64, 64))
    while True:
        board = [x[:] for x in [["empty"] * 3] * 3]
        game_mode = "undef"
        turn = "one"
        turn_number = 1
        selected_square = [0, 0]  # x, y
        
        request_gametype()
        
        while not is_game_over():
            print_board()
            request_play()
        
        print_board()
        if player_won("one", board):
            set_edge(PLAYER_ONE)
        elif player_won("two", board):
            set_edge(PLAYER_TWO)
        else:
            print("nobody won...")
            set_edge([0, 0, 0])
        time.sleep(5)


# user selects square to play in (and updates board to represent that), todo: computer AI for selection
def request_play():  # AI is always player one, playing first (life isn't fair. deal with it.)
    global game_mode
    global square_chosen
    if turn == "one":
        set_edge(PLAYER_ONE)
    else: 
        set_edge(PLAYER_TWO)
    if (game_mode == "slp") and (turn == "one"):
        request_ai_play()
    else:   # player's turn (either slp or coop)
        square_chosen = False
        is_invalid_input = True
        while is_invalid_input:  # loop until valid square is selected
            not_selected = True
            print_board()
            if turn == "one":
                set_edge(PLAYER_ONE)
                print_cursor(selected_square[0], selected_square[1], PLAYER_ONE_DIM)
            else: 
                set_edge(PLAYER_TWO)
                print_cursor(selected_square[0], selected_square[1], PLAYER_TWO_DIM)
            while not_selected:  # loop until center pressed (indicating selection)
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        if event.key == pygame.K_RETURN:    # center joystick pressed
                            not_selected = False
                        else:
                            handle_event(event)
                            print_board()
                            if turn == "one":
                                set_edge(PLAYER_ONE)
                                print_cursor(selected_square[0], selected_square[1], PLAYER_ONE_DIM)
                            else: 
                                set_edge(PLAYER_TWO)
                                print_cursor(selected_square[0], selected_square[1], PLAYER_TWO_DIM)
            if board[selected_square[0]][selected_square[1]] == "empty":    # valid square, so update board and end loop
                    is_invalid_input = False
                    board[selected_square[0]][selected_square[1]] = turn
    swap_turn()


# ai turn
def request_ai_play():
    print("ai's turn", turn, turn_number)
    # AI's turn (odd turn (turn counts from 1))
    for i in range(9):  # test all possible wins
        test_board = copy.deepcopy(board)
        test_board[i // 3][i % 3] = "one"
        if board[i // 3][i % 3] == "empty" and player_won("one", test_board):  # winning move, so play
            board[i // 3][i % 3] = "one"
            return
    for i in range(9):  # test all possible opponent wins
        test_board = copy.deepcopy(board)
        test_board[i // 3][i % 3] = "two"
        if board[i // 3][i % 3] == "empty" and player_won("two", test_board):  # block opp win move
            board[i // 3][i % 3] = "one"
            return
    if board[0][0] == board[2][2] == board[1][1] == "empty":  # take top left if diagonal from it is free
        board[0][0] = "one"
        return
    if turn_number == 3:
        if board[0][0] == "one" and board[1][1] == board[2][2] == "empty":
            # take bottom right corner if it and center are empty
            board[2][2] = "one"
            return
        else:
            board[2][0] = "one"  # take bottom left if player took our square or center
            return
    if turn_number == 5:
        if board[2][0] == "empty":  # check bottom left, if empty, take it
            board[2][0] = "one"
            return
        elif board[0][2] == "empty":  # take top right square if empty and bottom left is already used
            board[0][2] = "one"
            return
        else:
            # should never reach (if the opponent blocked both above squares, we'd play in the winning squares),
            # but play in a random square
            print("nuclear option! playing randomly! watch out!")
    for i in range(9):  # find an empty square
        if board[i // 3][i % 3] == "empty":
            board[i // 3][i % 3] = "one"
            return


# swaps value of global turn var
def swap_turn():
    global turn
    global turn_number
    turn_number += 1
    if turn == "one":
        turn = "two"
    else:
        turn = "one"


# returns True if there are no more open spaces or if a player has won
def is_game_over():
    if player_won("one", board) or player_won("two", board):
        return True
    for i in range(3):
        for j in range(3):
            if board[i][j] == "empty":
                return False
    return True


# Checks win conditions for one player on board
def player_won(player, brd):
    for i in range(3):  # Horizontal Rows
        if brd[i][0] == brd[i][1] == brd[i][2] == player:
            return True
    for i in range(3):  # Vertical Columns
        if brd[0][i] == brd[1][i] == brd[2][i] == player:
            return True
    if brd[0][0] == brd[1][1] == brd[2][2] == player:  # L->R Diagonal
        return True
    if brd[0][2] == brd[1][1] == brd[2][0] == player:  # R->L Diagonal
        return True
    return False


# prompts for game type, then sets game type global var
def request_gametype():
    global game_mode
    # SHOW OPTIONS
    sense.clear(0, 0, 0)
    print_square(0, 1, [255, 0, 0])
    print_square(2, 0, [0, 255, 0])
    print_square(2, 2, [0, 255, 0])
    # show current selection on border
    sel = 0
    not_selected = True
    while not_selected:
        if sel == 0:
            set_edge([255, 0, 0])
        else: 
            set_edge([0, 255, 0])
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    sel = (sel + 1) % 2
                elif event.key == pygame.K_RETURN:
                    not_selected = False
    if sel == 0:
        game_mode = "slp"
    else: 
        game_mode = "coop"
    print(game_mode)


def print_board():
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == "empty":
                print_square(i, j, WHITE)
            elif board[i][j] == "one":
                print_square(i, j, PLAYER_ONE)
            elif board[i][j] == "two":
                print_square(i, j, PLAYER_TWO)
            else:
                print("junk in square " + str(i) + str(j))
    if turn == "one":
        set_edge(PLAYER_ONE)
    else:
        set_edge(PLAYER_TWO)


# sets a specific tic tac toe square (0 to 2 X 0 to 2) to a given color
def print_square(x, y, color):
    x = (x * 2) + 1
    y = (y * 2) + 1
    set_pixels([[x, y], [x+1, y], [x+1, y+1], [x, y+1]], color)


def set_edge(color):
    for i in range(8):
        sense.set_pixel(i, 0, color[0], color[1], color[2])
        sense.set_pixel(i, 7, color[0], color[1], color[2])
        sense.set_pixel(0, i, color[0], color[1], color[2])
        sense.set_pixel(7, i, color[0], color[1], color[2])


# same as print_square, but creates a diagonal cursor to show selection
def print_cursor(x, y, color):
    x = (x * 2) + 1
    y = (y * 2) + 1
    set_pixels([[x, y], [x + 1, y + 1]], color)
    

def handle_event(event):
    if event.key == pygame.K_DOWN:
        selected_square[1] = (selected_square[1] + 1 + 3) % 3
    elif event.key == pygame.K_UP:
        selected_square[1] = (selected_square[1] - 1 + 3) % 3
    elif event.key == pygame.K_LEFT:
        selected_square[0] = (selected_square[0] - 1 + 3) % 3
    elif event.key == pygame.K_RIGHT:
        selected_square[0] = (selected_square[0] + 1 + 3) % 3


if __name__ == '__main__':
    main()
