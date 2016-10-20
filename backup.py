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
import collections
import hashlib
import codecs
import struct
from heapq import heappush, heappop


AI_NAME = "efuteaI2"
WIDTH = 10
HEIGHT = 16
PACK_SIZE = 3
SUMMATION = 10
MAX_TURN = 500
OBSTACLE = SUMMATION + 1
EMPTY = 0
PACKS = []
INF = float('inf')
BOARD_CACHE = {}
struct_format = struct.Struct("160h")
RATE = [0, 0]


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
    for _ in range(rot):
        pack = rot1(pack)
    return pack


def anni_board_line(board, x, y, dx, dy, idx):
    for i in idx:
        board[x + dx * i][y + dy * i] = EMPTY


def is_fallable(pack, x):
    if 0 <= x <= WIDTH - PACK_SIZE:
        return True
    return all(ee == EMPTY for i, e in enumerate(zip(*pack)) if not 0 <= x + i < WIDTH for ee in e)


def fill_obstacle(pack, num):
    if num == 0:
        return pack, 0
    idx = itertools.islice((
        (i, j) for i in range(PACK_SIZE) for j in range(PACK_SIZE) if pack[i][j] == EMPTY
    ), num)
    p = [row[:] for row in pack]
    for i in idx:
        p[i[0]][i[1]] = OBSTACLE
        num -= 1
    return p, num


def fall_pack(board, pack, x):
    update = []
    b = [row[:] for row in board]
    p = [[c for c in col if c != EMPTY] for col in zip(*pack)]
    for i, pp in enumerate(p):
        if len(pp) < 1:
            continue
        j = len(pp) - 1
        if b[x + i][j] != EMPTY:
            return None, []
        while b[x + i][j] == EMPTY:
            j += 1
            if j > HEIGHT - 1:
                break
        j -= len(pp)
        update.extend((x + i, j + k) for k in range(len(pp)))
        for k, q in enumerate(pp):
            b[x + i][j + k] = q
    return b, update


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
            j -= 1


def force_gravity(board):
    return [u for u in __force_gravity(board)]


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
        anni += __anni_board(board, b, x, y, dx, dy)

    update = force_gravity(b)
    return anni, b, update


def board_hash(board):
    data = struct_format.pack(*[bb for b in board for bb in b])
    # return codecs.encode(data, 'base64')
    return hashlib.md5(data).hexdigest()


def evaluate_board(board, update):
    score = 0
    chain = 0
    anni_total = 1
    while True:
        #k = board_hash(board)
        #res = BOARD_CACHE.get(k, None)
        #if res is not None:
        #    anni, board, update = res
        #    RATE[0] += 1
        #    # TODO: 本当に一致する？
        #    # 他にキャッシュできるところは？
        #else:
        anni, board, update = anni_board(board, update)
        #BOARD_CACHE[k] = (anni, board, update)
        #RATE[1] += 1
        if anni == 0:
            break
        anni_total *= anni
        chain += 1
        score += math.floor(1.3**chain) * math.floor(anni / 2.0)
    return score, chain, anni_total, board


def evaluate(board, update):
    if board is None:
        return INF, None
    score, chain, anni, b = evaluate_board(board, update)
    temp = [len(col) - col.count(EMPTY) for col in board]
    h = max(temp) - math.floor(sum(temp) / len(temp))
    s = score * 5 if score >= 5 else 1
    if chain > 3:
        print("chain: {}".format(chain), file=sys.stderr)
    return h - s, b


def next_boards(board, turn, obstacle_num=0):
    pack = fill_obstacle(PACKS[turn], obstacle_num)[0]
    packs = [rotate_pack(pack, r) for r in range(4)]
    temp = ((packs[r], (p, r)) for p in range(-2, WIDTH) for r in range(4))
    #temp = ((packs[1], (5, 1)) for _ in range(1))
    return ((fall_pack(board, t[0], t[1][0]), t[1]) for t in temp if is_fallable(t[0], t[1][0]))


def solve(board, turn, obstacle_num, remain_time):
    # limit = time.time() + remain_time
    hpq = []
    beam = 100
    r = 1

    for c in next_boards(board, turn, obstacle_num):
        score, b = evaluate(c[0][0], c[0][1])
        heappush(hpq, (score, b, c[1]))

    for t in range(turn + 1, min(MAX_TURN, turn + r + 1)):
        next_hpq = []
        # print("NEXT: {}".format(min(beam, len(hpq))), file=sys.stderr)
        for _ in range(min(beam, len(hpq))):
            st = heappop(hpq)
            if st[1] is None:
                continue
            for c in next_boards(st[1], t, 0):
                score, b = evaluate(c[0][0], c[0][1])
                heappush(next_hpq, (st[0] + score, b, st[2]))
        if len(next_hpq) < 1:
            break
        # print("max: {}".format(next_hpq[0][0]), file=sys.stderr)
        hpq = next_hpq
        #beam = max(math.floor(math.sqrt(beam)), 1)

    if len(hpq) < 1:
        return INF, None, (0, 0)

    return hpq[0]


def process_turn():
    turn = int(input())
    #print("turn: {}".format(turn), file=sys.stderr)
    remain_time = int(input())

    obstacle_num = int(input())
    board = [list(bb) for bb in zip(*[[int(i) for i in input().split()] for _ in range(HEIGHT)])]
    _ = input()

    enemy_obstacle_num = int(input())
    enemy_board = [list(bb) for bb in zip(*[[int(i) for i in input().split()] for _ in range(HEIGHT)])]
    _ = input()

    ob = max(obstacle_num - enemy_obstacle_num, 0)
    res = solve(board, turn, ob, min(remain_time, 20000))
    #print(res[0], file=sys.stderr)
    #print(str(math.floor(RATE[0] * 100 / (RATE[0] + RATE[1]))) + "%", file=sys.stderr)
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
        print(traceback.format_exc(), file=sys.stderr)
        print("error: {0}".format(e), file=sys.stderr)


if __name__ == '__main__':
    main()
