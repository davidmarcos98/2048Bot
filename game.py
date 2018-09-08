import random
from PIL import Image
from twitter import *
import os
os.system("killall chrome")

os.system("export PATH=$PATH:/home/david/2048Bot/")
login()
from twitter import browser

last_poll = ""
board = None



time.sleep(3)

def new_game():
    global board, last_poll
    board = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    for i in range(0, 4):
        for j in range(0, 4):
            print(board[i][j])
        print("\n")
    if browser.current_url is not 'https://twitter.com':
        print(browser.current_url)
        actions = ActionChains(browser)
        actions.send_keys('652897070')
        actions.send_keys(Keys.ENTER)
        actions.perform()
    time.sleep(3)
    last_poll=send_tweet("New game! We will use this thread to play! ID: " + str(random.randint(0, 99999)), "")
    time.sleep(3)
    next_round(0)

def move(direction):
    print(direction)
    global board
    if direction is "RIGHT" or direction is "DOWN":
        init = 0
        end = 3
        change = 1
    else:
        init = 3
        end = 0
        change = -1
    rows = [False, False, False, False]
    columns = [False, False, False, False]
    if direction is "RIGHT" or direction is "LEFT":
        for i in range(0, 4):
            while check_row(i, direction, rows, columns) is not True:
                for j, k in zip(range(init, end, change), range(end, init, -change)):
                    if (k - change >= 0 and board[i][k] != 0 and board[i][k - change] == board[i][k] and rows[i] is not True):
                        board[i][k - change] += board[i][k]
                        rows[i] = True
                        board[i][k] = 0
                    elif (j+change<4 and board[i][j] != 0 and board[i][j + change] == 0):
                        board[i][j + change] = board[i][j]
                        board[i][j] = 0
    else:
        for i in range(0, 4):
            while check_row(i, direction, rows, columns) is not True:
                for j, k in zip(range(init, end, change), range(end, init, -change)):
                    if (k - change < 4 and board[k][i] != 0 and board[k - change][i] == board[k][i] and columns[i] is not True):
                        board[k - change][i] += board[k][i]
                        columns[i] = True
                        board[k][i] = 0

                    elif (j+change<4 and board[j][i] != 0 and board[j+change][i] == 0):
                        board[j+change][i] = board[j][i]
                        board[j][i] = 0
    return board

def check_row(i, direction, rows, columns):
    result = True
    zeroes = False
    if direction is "RIGHT" or direction is "DOWN":
        init = 3
        end = -1
        change = -1
    else:
        init = 0
        end = 4
        change = 1
    if(direction is "RIGHT" or direction is "LEFT"):
        for j in range(init, end, change):
            if (board[i][j] == 0):
                zeroes = True
            elif zeroes is True:
                result = False
            elif j+1 < 4 and board[i][j+1] == board[i][j] and rows[i] is not True:
                result = False
    else:
        for j in range(init, end, change):
            if (board[j][i] == 0):
                zeroes = True
            elif zeroes is True:
                result = False
            elif j+1 < 4 and board[j+1][i] == board[j][i] and columns[i] is not True:
                result = False
    return result

def zeros():
    result = False
    for i in range(0, 4):
        for j in range(0, 4):
            if board[i][j] == 0:
                result = True
    return result

def next_round(round):
    print(round)
    choices = [4, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    global board, last_poll
    for i in range(0, 4):
        print(str(board[i][0]) + " "+ str(board[i][1]) + " " + str(board[i][2]) + " " + str(board[i][3]))
    print('-------------------------')
    generate_image(round)
    last_poll = post_image(last_poll, round)
    if not check_moves():
        game_over()
    else:
        last_poll = post_poll(last_poll, round)
        minutes = 6
        #time to wait until poll ends and we can retrieve the results. Added 1 more minute, just as backup
        time.sleep((60*minutes))
        #check poll results and move
        board = move(check_poll_results(last_poll))
        if round is 0:
            i = 0
            while i < 2:
                row = random.randint(0,3)
                column = random.randint(0,3)
                if (board[row][column] is 0):
                    board[row][column] = 2
                    i += 1
        elif zeros():
            i = 0
            while i < 1:
                row = random.randint(0, 3)
                column = random.randint(0, 3)
                if (board[row][column] is 0):
                    board[row][column] = choices[random.randint(0, 1)]
                    i += 1
        round += 1
        next_round(round)

def generate_image(round):
    background = Image.open('drawable/background.png', 'r')

    for i in range(0, 4):
        for j in range(0, 4):
            img = Image.open('drawable/' + str(board[i][j]) + '.png', 'r')
            img.thumbnail((600, 600))
            offset = (120 * (j + 1) + 600 * j, 120 * (i + 1) + 600 * i)
            background.paste(img, offset, mask=img)

    background.thumbnail((3000,3000))
    background.convert('RGBA')
    background.save(str(round) + '.png')

def check_moves():
    result = False
    for i in range(0, 4):
        for j in range(0, 3):
            if board[i][j] == board[i][j+1] or board[i][j] == 0 or board[i][j+1] == 0 or board[j+1][i] == board[j][i]:
                result = True
    return result

def game_over():
    reply("Game over! No more movements are possible! You guys finished with a max score of: " + str(max_tile()),
          last_poll)
    new_game()

def max_tile():
    max = 0
    for i in range(0, 4):
        for j in range(0,4):
            if board[i][j] > max: max = board[i][j]
    return max
