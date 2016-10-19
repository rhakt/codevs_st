#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import random
import itertools
import functools
import operator
import heapq
import math
import time
import collections
from copy import deepcopy


AI_NAME = "efuteaI"
WIDTH = 10
HEIGHT = 16
PACK_SIZE = 3
SUMMATION = 10
MAX_TURN = 500
OBSTACLE = SUMMATION + 1
EMPTY = 0
PACKS = []

# @lru_cache(maxsize=32)


def input_packs():
    pack = [[int(i) for i in input().split()] for _ in range(PACK_SIZE)]
    _ = input()
    return pack


def input_initial():
    global WIDTH, HEIGHT, PACK_SIZE, SUMMATION, MAX_TURN, OBSTACLE, PACKS
    WIDTH, HEIGHT, PACK_SIZE, SUMMATION, MAX_TURN = [int(x) for x in input().split()]
    OBSTACLE = SUMMATION + 1
    PACKS = [input_packs() for _ in range(MAX_TURN)]


def rot1(pack):
    return [[pack[PACK_SIZE - 1 - i][j] for i in range(PACK_SIZE)] for j in range(PACK_SIZE)]


def rotate_pack(pack, rot):
    return functools.reduce(lambda x, _: rot1(x), range(rot), pack)


def get_board_line(board, x, y, dx, dy):
    while 0 <= x < WIDTH and 0 <= y < HEIGHT:
        yield board[y][x]
        x += dx
        y += dy


def anni_board_line(board, x, y, dx, dy, idx):
    for i in idx:
        board[y + dy * i][x + dx * i] = EMPTY


def is_fallable(pack, x):
    if 0 <= x <= WIDTH - PACK_SIZE:
        return True
    return all(ee == EMPTY for i, e in enumerate(zip(*pack)) if not 0 <= x + i < WIDTH for ee in e)


def fill_obstacle(pack, num):
    idx = itertools.islice((
        (i, j) for i in range(PACK_SIZE) for j in range(PACK_SIZE) if pack[i][j] == EMPTY
    ), num)
    p = deepcopy(pack)
    for i in idx:
        p[i[0]][i[1]] = OBSTACLE
        num -= 1
    return p, num


def fall_pack(board, pack, x):
    b = deepcopy(board)
    p = [[c for c in col if c != EMPTY] for col in zip(*pack)]
    for i, pp in enumerate(p):
        if len(pp) < 1:
            continue
        j = len(pp) - 1
        if b[j][x + i] != EMPTY:
            return None
        while b[j][x + i] == EMPTY:
            j += 1
            if j > HEIGHT - 1:
                break
        j -= len(pp)
        for k, q in enumerate(pp):
            b[j + k][x + i] = q
    return b


def force_gravity(board):
    bb = [[EMPTY for _ in range(WIDTH)] for _ in range(HEIGHT)]
    for i, b in enumerate(zip(*board)):
        col = [e for e in b if e != EMPTY]
        start = HEIGHT - len(col)
        for j, c in enumerate(col):
            bb[start + j][i] = c
    return bb


def count_anni(line):
    dq = collections.deque()
    summ = 0
    idx = []
    for i, l in enumerate(line):
        if l == EMPTY:
            summ = 0
            dq.clear()
            continue
        dq.append((l, i))
        summ += l
        while summ > SUMMATION:
            summ -= dq.popleft()[0]
        if summ == SUMMATION:
            idx.extend(d[1] for d in dq)
    return len(idx), set(idx)


def __anni_board(sb, tb, x, y, dx, dy):
    c, l = count_anni(l for l in get_board_line(sb, x, y, dx, dy))
    anni_board_line(tb, x, y, dx, dy, l)
    return c


def anni_board(board):
    anni = 0
    b = deepcopy(board)
    for h in range(HEIGHT):
        anni += __anni_board(board, b, 0, h, 1, 0)
        anni += __anni_board(board, b, 0, h, 1, 1)
        anni += __anni_board(board, b, 0, h, 1, -1)
    for w in range(WIDTH):
        anni += __anni_board(board, b, w, 0, 0, 1)
        anni += __anni_board(board, b, w, 0, 1, 1)
        anni += __anni_board(board, b, WIDTH - 1, HEIGHT - WIDTH + w, -1, 1)
    return anni, force_gravity(b)


def evaluate_board(board):
    score = 0
    chain = 0
    while True:
        anni, board = anni_board(board)
        if anni == 0:
            break
        chain += 1
        score += math.floor(1.3**chain) * math.floor(anni / 2.0)
    return score, chain


def evaluate(board):
    if board is None:
        return -float('inf')
    score, chain = evaluate_board(board)
    temp = [len(col) - col.count(EMPTY) for col in zip(*board)]
    h = max(temp) / len(temp)
    s = score if score >= 5 else -10
    return s - h


def solve(board, turn, obstacle_num, remain_time):
    # limit = time.time() + remain_time
    temp = ((rotate_pack(fill_obstacle(PACKS[turn], obstacle_num)[0], r), (p, r))
            for p in range(-2, WIDTH) for r in range(4))
    cand = ((fall_pack(board, t[0], t[1][0]), t[1])
            for t in temp if is_fallable(t[0], t[1][0]))
    return ((evaluate(c[0]), c[0], c[1]) for c in cand)


def process_turn():
    turn = int(input())
    print("turn: {}".format(turn), file=sys.stderr)
    remain_time = int(input())

    obstacle_num = int(input())
    board = [[int(i) for i in input().split()] for _ in range(HEIGHT)]
    _ = input()

    enemy_obstacle_num = int(input())
    enemy_board = [[int(i) for i in input().split()] for _ in range(HEIGHT)]
    _ = input()

    ob = max(obstacle_num - enemy_obstacle_num, 0)
    res = max(solve(board, turn, ob, min(remain_time, 20000)))
    return res[2]


def main():
    random.seed(800000002)
    print(AI_NAME)
    sys.stdout.flush()
    input_initial()
    try:
        while True:
            print(*process_turn())
            sys.stdout.flush()
    except KeyboardInterrupt as _:
        pass
    except Exception as e:
        print("error: {0}".format(e), file=sys.stderr)



if __name__ == '__main__':
    main()
