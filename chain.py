#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import traceback
import random
import itertools
import math


AI_NAME = "game info >"
WIDTH = 10
HEIGHT = 19
PACK_SIZE = 3
SUMMATION = 10
MAX_TURN = 500
OBSTACLE = SUMMATION + 1
EMPTY = 0
INF = float('inf')
PACKS = []
PACKS_CACHE = []


def input_packs():
    pack = [[int(i) for i in input().split()] for _ in range(PACK_SIZE)]
    _ = input()
    return pack


def rot1(pack):
    return [[pack[PACK_SIZE - 1 - i][j] for i in range(PACK_SIZE)] for j in range(PACK_SIZE)]


def rotate_pack(pack, rot):
    for _ in range(rot):
        pack = rot1(pack)
    return pack


def input_initial():
    global WIDTH, HEIGHT, PACK_SIZE, SUMMATION, MAX_TURN, OBSTACLE, PACKS, PACKS_CACHE
    WIDTH, HEIGHT, PACK_SIZE, SUMMATION, MAX_TURN = [int(x) for x in input().split()]
    HEIGHT += PACK_SIZE
    OBSTACLE = SUMMATION + 1
    PACKS = [input_packs() for _ in range(MAX_TURN)]
    PACKS_CACHE = [rotate_pack(pack, rot) for pack in PACKS for rot in range(4)]


def anni_board_line(board, x, y, dx, dy, idx):
    for i in idx:
        board[x + dx * i][y + dy * i] = EMPTY


def is_fallable(pack, x):
    if 0 <= x <= WIDTH - PACK_SIZE:
        return True
    return all(ee == EMPTY for i, e in enumerate(zip(*pack)) if not 0 <= x + i < WIDTH for ee in e)


def fill_obstacle(pack, num):
    idx = itertools.islice((
        (i, j) for i in range(PACK_SIZE) for j in range(PACK_SIZE) if pack[i][j] == EMPTY
    ), num)
    p = [row[:] for row in pack]
    for i in idx:
        p[i[0]][i[1]] = OBSTACLE
    return p


def __force_gravity(board):
    for i, b in enumerate(board):
        j = HEIGHT - 1
        e = None
        while j >= 0:
            if e is None and b[j] == EMPTY:
                e = j
            if e is not None and b[j] != EMPTY:
                b[j], b[e] = b[e], b[j]
                yield (i, e)
                j = e
                e = None
            elif j < PACK_SIZE and b[j] != EMPTY:
                yield (i, j)
            j -= 1


def force_gravity(board):
    return [u for u in __force_gravity(board)]


def fall_pack(board, pack, x):
    b = [row[:] for row in board]
    for j, p in enumerate(pack):
        for i, q in enumerate(p):
            if q == EMPTY:
                continue
            if b[x + i][j] != EMPTY:
                return None, []
            b[x + i][j] = q
    u = force_gravity(b)
    return b, u


def __anni_board(sb, tb, x, y, dx, dy):
    start = last = 0
    summ = 0
    anni = 0
    i = 0
    sx = x
    sy = y
    while 0 <= x < WIDTH and 0 <= y < HEIGHT:
        e = sb[x][y]
        if e == EMPTY:
            summ = 0
            start = i + 1
            last = start
        else:
            last += 1
            summ += e
            while summ > SUMMATION:
                summ -= sb[sx + dx * start][sy + dy * start]
                start += 1
            if summ == SUMMATION:
                anni += (last - start)
                for k in range(start, last):
                    tb[sx + dx * k][sy + dy * k] = EMPTY
        i += 1
        x += dx
        y += dy
    return anni


def anni_board(board, update):
    anni = 0
    b = [row[:] for row in board]
    lst = []
    for x, y in update:
        yy = HEIGHT - 1 - y
        lst.extend([
            (x, 0, 0, 1),
            (0, y, 1, 0),
            (x - y if y < x else 0, 0 if y < x else y - x, 1, 1),
            (x - yy if yy < x else 0, HEIGHT - 1 if yy < x else y + x, 1, -1)
        ])
    for x, y, dx, dy in set(lst):
        anni += __anni_board(b, board, x, y, dx, dy)

    update = force_gravity(board)
    return anni, update


def evaluate_board(board, update):
    score = 0
    chain = 0
    anni_total = []
    while True:
        anni, update = anni_board(board, update)
        if anni == 0:
            break
        anni_total.append(anni)
        chain += 1
        score += math.floor(1.3**chain) * math.floor(anni / 2.0)
    return score, chain, anni_total


def solve(board, turn, obstacle_num, x, r):
    if obstacle_num > 0:
        pack = rotate_pack(fill_obstacle(PACKS[turn], obstacle_num), r)
    else:
        pack = PACKS_CACHE[turn * 4 + r]
    if not is_fallable(pack, x):
        return "invalid (pos, rot)"
    b, u = fall_pack(board, pack, x)
    score, chain, anni = evaluate_board(b, u)
    return "score: {}, chain: {}, anni: {}".format(score, chain, anni)


def process_turn():
    s = ""
    while len(s.strip()) is 0:
        s = input()
    turn = int(s)
    print("turn: {}".format(turn), file=sys.stderr)
    _ = int(input())

    obstacle_num = int(input())
    board = [list(bb) for bb in zip(*[[int(i) for i in input().split()] for _ in range(HEIGHT - PACK_SIZE)])]
    for b in board:
        b.extend([0] * PACK_SIZE)
    _ = input()

    enemy_obstacle_num = int(input())
    _ = [list(bb) for bb in zip(*[[int(i) for i in input().split()] for _ in range(HEIGHT - PACK_SIZE)])]
    _ = input()

    ob = max(obstacle_num - enemy_obstacle_num, 0)

    if turn is 0:
        return ""

    print("(pos, rot) > ", file=sys.stderr)

    s = ""
    while len(s.strip()) is 0:
        s = input()
    pos, rot = [int(x) for x in s.split()]
    return solve(board, turn, ob, pos, rot)


def main():
    random.seed(800000002)
    print(AI_NAME)
    sys.stdout.flush()
    input_initial()
    try:
        while True:
            print(process_turn())
            print("turn info >")
            sys.stdout.flush()
    except KeyboardInterrupt as _:
        pass
    except Exception as e:
        print(traceback.format_exc(), file=sys.stderr)
        print("error: {0}".format(e), file=sys.stderr)


if __name__ == '__main__':
    main()
