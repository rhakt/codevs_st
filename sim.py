#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import traceback
import random
import itertools
import functools
import operator
import math
import time
from collections import deque
from heapq import heappush, heappop


AI_NAME = "sim"
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
NEXT_CACHE = None


def input_packs():
    pack = [[int(i) for i in input().split()] for _ in range(PACK_SIZE)]
    _ = input()
    return pack


def rot1(pack):
    return [[pack[PACK_SIZE - 1 - i][j] for i in range(PACK_SIZE)] for j in range(PACK_SIZE)]


def rotate_packs(pack):
    yield pack
    for _ in range(3):
        pack = rot1(pack)
        yield pack


def input_initial():
    global WIDTH, HEIGHT, PACK_SIZE, SUMMATION, MAX_TURN, OBSTACLE, PACKS, PACKS_CACHE
    WIDTH, HEIGHT, PACK_SIZE, SUMMATION, MAX_TURN = [int(x) for x in input().split()]
    HEIGHT += PACK_SIZE
    OBSTACLE = SUMMATION + 1
    PACKS = [input_packs() for _ in range(MAX_TURN)]
    PACKS_CACHE = [p for pack in PACKS for p in rotate_packs(pack)]


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
        num -= 1
    return p, num


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
    anni_total = 1
    while True:
        anni, update = anni_board(board, update)
        if anni == 0:
            break
        anni_total *= anni
        chain += 1
        score += math.floor(1.3**chain) * math.floor(anni / 2.0)
    return score, chain, anni_total


def __evaluate(board):
    s = 0
    for i, b in enumerate(board):
        for j, bb in enumerate(b):
            if j - 2 < 0:
                continue
            if i - 1 >= 0:
                if board[i - 1][j - 2] + bb == SUMMATION:
                    s += 2
            if i + 1 < WIDTH:
                if board[i + 1][j - 2] + bb == SUMMATION:
                    s += 2
            if board[i][j - 2] + bb == SUMMATION:
                s += 1
    return s


def evaluate(board, update):
    if board is None:
        return INF
    score, chain, anni = evaluate_board(board, update)
    if chain >= 10:
        print("chain: {}".format(chain), file=sys.stderr)
    if any(board[i][PACK_SIZE - 1] != EMPTY for i in range(WIDTH)):
        return INF
    s = __evaluate(board)
    if chain < 10:
        s += chain * chain
        s += score
        s -= anni * 100
    else:
        s += score
    return -s


def cand_range(board):
    start = -2
    end = WIDTH - 1
    while start < WIDTH / 2:
        b = board[start + PACK_SIZE]
        if sum(b) > 0:
            break
        start += 1
    while start < end - 1:
        b = board[end - 1]
        if sum(b) > 0:
            break
        end -= 1
    return start, end


def next_boards(board, turn, obstacle_num=0):
    start, end = cand_range(board)
    if obstacle_num > 0:
        pack, obstacle_num = fill_obstacle(PACKS[turn], obstacle_num)
        packs = (p for p in rotate_packs(pack))
    else:
        packs = (PACKS_CACHE[turn * 4 + r] for r in range(4))
    temp = ((p, (x, r)) for r, p in enumerate(packs) for x in range(start, end))
    return ((fall_pack(board, t[0], t[1][0]), t[1], obstacle_num) for t in temp if is_fallable(t[0], t[1][0]))


def solve(board, turn, obstacle_num, remain_time):
    # limit = time.time() + remain_time
    hpq = []
    beam = 48
    r = 10

    for c in next_boards(board, turn, obstacle_num):
        score = evaluate(c[0][0], c[0][1])
        if score != INF:
            heappush(hpq, (score, c[0][0], [(c[1][0], c[1][1], obstacle_num)], c[2]))

    for t in range(turn + 1, min(MAX_TURN, turn + r + 1)):
        next_hpq = []
        for _ in range(min(beam, len(hpq))):
            st = heappop(hpq)
            if st[1] is None:
                continue
            for c in next_boards(st[1], t, st[3]):
                score = evaluate(c[0][0], c[0][1])
                if score != INF:
                    pr = [t for t in st[2]]
                    pr.append((c[1][0], c[1][1], st[3]))
                    heappush(next_hpq, (st[0] + score, c[0][0], pr, c[2]))
        if len(next_hpq) < 1:
            break
        hpq = next_hpq

    if len(hpq) < 1:
        return INF, None, [(0, 0, obstacle_num)], 0

    return hpq[0]


def process_turn():
    global NEXT_CACHE
    turn = int(input())
    remain_time = int(input())

    obstacle_num = int(input())
    board = [list(bb) for bb in zip(*[[int(i) for i in input().split()] for _ in range(HEIGHT - PACK_SIZE)])]
    for i, b in enumerate(board):
        b.extend([0] * PACK_SIZE)
    _ = input()

    enemy_obstacle_num = int(input())
    _ = [list(bb) for bb in zip(*[[int(i) for i in input().split()] for _ in range(HEIGHT - PACK_SIZE)])]
    #for b in board:
    #    b.extend([0] * PACK_SIZE)
    _ = input()

    ob = max(obstacle_num - enemy_obstacle_num, 0)
    if NEXT_CACHE is not None:
        if len(NEXT_CACHE) != 0:
            pr = NEXT_CACHE.popleft()
            if ob == pr[2]:
                return pr[:2]
            NEXT_CACHE = None
            print("cache reset!", file=sys.stderr)
    res = solve(board, turn, ob, min(remain_time, 20000))
    NEXT_CACHE = deque(res[2])
    pr = NEXT_CACHE.popleft()
    #print(pr, file=sys.stderr)
    return pr[:2]


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
        print(traceback.format_exc(), file=sys.stderr)
        print("error: {0}".format(e), file=sys.stderr)


if __name__ == '__main__':
    main()
