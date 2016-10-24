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


AI_NAME = "efutea_local"
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
CHECK_AROUND_DIR = [(-1, 0), (-1, -1), (-1, 1)]
PACK_INCLUDE = None


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


def pack_includes(pack):
    lst = [False] * (SUMMATION - 1)
    for p in pack:
        for pp in p:
            if EMPTY < pp < OBSTACLE:
                lst[pp - 1] = True
    return lst


def input_initial():
    global WIDTH, HEIGHT, PACK_SIZE, SUMMATION, MAX_TURN, OBSTACLE, PACKS, PACKS_CACHE, PACK_INCLUDE
    WIDTH, HEIGHT, PACK_SIZE, SUMMATION, MAX_TURN = [int(x) for x in input().split()]
    HEIGHT += PACK_SIZE
    OBSTACLE = SUMMATION + 1
    PACKS = [input_packs() for _ in range(MAX_TURN)]
    PACKS_CACHE = [p for pack in PACKS for p in rotate_packs(pack)]
    PACK_INCLUDE = [pack_includes(pack) for pack in PACKS]


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


def __force_gravity(board, lst):
    for i in lst:
        b = board[i]
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


def force_gravity(board, lst):
    return [u for u in __force_gravity(board, set(lst))]


def fall_pack(board, pack, x):
    b = [row[:] for row in board]
    lst = []
    for j, p in enumerate(pack):
        for i, q in enumerate(p):
            if q == EMPTY:
                continue
            if b[x + i][j] != EMPTY:
                return None, []
            b[x + i][j] = q
            lst.append(x + i)
    u = force_gravity(b, lst)
    return b, u


def __anni_board(sb, tb, x, y, dx, dy, lst):
    start = last = 0
    summ = 0
    anni = 0
    i = 0
    sx = x
    sy = y
    while 0 <= x < WIDTH and 0 <= y < HEIGHT:
        e = sb[x][y]
        if e == EMPTY:
            break
        else:
            last += 1
            summ += e
            while summ > SUMMATION:
                summ -= sb[sx + dx * start][sy + dy * start]
                start += 1
            if summ == SUMMATION:
                anni += (last - start)
                for k in range(start, last):
                    xx = sx + dx * k
                    yy = sy + dy * k
                    tb[xx][yy] = EMPTY
                    lst.append(xx)
        i += 1
        x += dx
        y += dy
    return anni


def anni_board(board, update):
    anni = 0
    b = [row[:] for row in board]
    lst = []
    for x, y in update:
        sx = x - 1
        while sx >= 0:
            if b[sx][y] == EMPTY:
                break
            sx -= 1
        lst.append((sx + 1, y, 1, 0))
        lst.append((x, y, 0, 1))

        sx = x - 1
        sy = y - 1
        while sx >= 0 and sy >= 0:
            if b[sx][sy] == EMPTY:
                break
            sx -= 1
            sy -= 1
        lst.append((sx + 1, sy + 1, 1, 1))

        sx = x - 1
        sy = y + 1
        while sx >= 0 and sy < HEIGHT:
            if b[sx][sy] == EMPTY:
                break
            sx -= 1
            sy += 1
        lst.append((sx + 1, sy - 1, 1, -1))

    anni_lst = []
    for x, y, dx, dy in set(lst):
        anni += __anni_board(b, board, x, y, dx, dy, anni_lst)
    return anni, force_gravity(board, anni_lst)


def evaluate_board(board, update):
    score = 0
    chain = 0
    while True:
        anni, update = anni_board(board, update)
        if anni == 0:
            break
        chain += 1
        score += math.floor(1.3**chain) * math.floor(anni / 2.0)
    return score, chain


def check_next_pack(turn, num=2):
    lst = [False] * (SUMMATION - 1)
    for t in range(turn + 1, turn + num + 1):
        for i in range(SUMMATION - 1):
            lst[i] |= PACK_INCLUDE[t][i]
    return lst


def check_around(board, x, y):
    lst = [False] * (SUMMATION - 1)

    for car in CHECK_AROUND_DIR:
        bb = OBSTACLE
        bb2 = OBSTACLE

        xx = x + car[0]
        yy = y + car[1]
        if 0 <= xx < WIDTH and 0 <= yy < HEIGHT:
            bb = board[xx][yy]
            if EMPTY < bb < OBSTACLE:
                lst[SUMMATION - bb - 1] = True

        xx = x - car[0]
        yy = y - car[1]
        if 0 <= xx < WIDTH and 0 <= yy < HEIGHT:
            bb2 = board[xx][yy]
            if EMPTY < bb2 < OBSTACLE:
                lst[SUMMATION - bb2 - 1] = True

        if 0 < bb + bb2 < SUMMATION:
            lst[SUMMATION - bb - bb2 - 1] = True

    return lst


def evaluate(board, update, ob, turn):
    if board is None:
        return INF, 0, 0, ob

    score, chain = evaluate_board(board, update)
    ob = max(0, ob - math.floor(score / 5))

    if any(board[i][PACK_SIZE - 1] != EMPTY for i in range(WIDTH)):
        return INF, 0, 0, ob

    sf = math.floor(score / 5)
    if chain > 11:
        print("emitable: {} ({})".format(chain, sf), file=sys.stderr)
    s = sf * 5 * 2

    hei = [len(b) - b.count(0) for b in board]
    hpena = 0
    for i in range(WIDTH - 1):
        dh = abs(hei[i] - hei[i + 1])
        if dh > 3:
            hpena += (dh - 3) * (dh - 3)

    next_sc = s
    next_ch = 0
    next_ch_total = 0
    pack_lst = check_next_pack(turn)
    for x in range(WIDTH):
        hs = hei[x + 1] if x + 1 < WIDTH else 0
        hs += hei[x - 1] if x - 1 > 0 else 0
        if hs == 0:
            continue
        y = HEIGHT - 1 - hei[x]
        ar = check_around(board, x, y)
        for i in range(1, SUMMATION):
            if not pack_lst[i - 1]:
                continue
            if not ar[i - 1]:
                continue
            b = [bb[:] for bb in board]
            b[x][y] = i
            sc, ch = evaluate_board(b, [(x, y)])
            sf = math.floor(sc / 5)
            s = ch * 30
            s += sf * 5
            #next_ch_total += max(ch - 10, 0) * sf
            next_ch_total += sf if ch > 10 else 0
            next_ch = max(ch, next_ch)
            next_sc = max(s, next_sc)

    if next_ch > 11:
        print("next chain: {} ({}, {})".format(next_ch, next_sc, next_ch_total), file=sys.stderr)

    next_sc += next_ch_total

    #if ob > 7:
    #    next_sc -= ob * 5
    next_sc -= hpena

    return -next_sc, chain, score, ob


def cand_range(board):
    start = -2
    end = WIDTH
    stan = WIDTH / 2
    while start < stan:
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
    beam = 32
    r = 2

    for c in next_boards(board, turn, obstacle_num):
        score, chain, sc, ob = evaluate(c[0][0], c[0][1], c[2], turn)
        if score != INF:
            heappush(hpq, (score, c[0][0], [(c[1][0], c[1][1], obstacle_num, chain)], ob, sc))

    for t in range(turn + 1, min(MAX_TURN, turn + r + 1)):
        next_hpq = []
        max_chain = 0
        for _ in range(min(beam, len(hpq))):
            st = heappop(hpq)
            if st[1] is None:
                continue
            for c in next_boards(st[1], t, st[3]):
                score, chain, sc, ob = evaluate(c[0][0], c[0][1], c[2], turn)
                ob = max(0, c[2] - math.floor(sc / 5))
                max_chain = max(max_chain, chain)
                if score != INF:
                    pr = [t for t in st[2]]
                    pr.append((c[1][0], c[1][1], st[3], chain))
                    heappush(next_hpq, (score - st[4], c[0][0], pr, ob, sc + st[4]))
                    #heappush(next_hpq, (score, c[0][0], pr, ob))
                #if chain > 12:
                #    print("chain: {}".format(chain), file=sys.stderr)
        if len(next_hpq) < 1:
            break
        hpq = next_hpq

    if len(hpq) < 1:
        return INF, None, [(0, 0, obstacle_num, 0)], 0

    return hpq[0]


def process_turn():
    global NEXT_CACHE
    turn = int(input())
    print("turn: {}".format(turn), file=sys.stderr)
    remain_time = int(input())

    obstacle_num = int(input())
    board = [[0] * PACK_SIZE for _ in range(WIDTH)]
    tmp = [list(bb) for bb in zip(*[[int(i) for i in input().split()] for _ in range(HEIGHT - PACK_SIZE)])]
    for i, b in enumerate(board):
        b.extend(tmp[i])
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
                if pr[3] > 1:
                    print("emit {} chain".format(pr[3]), file=sys.stderr)
                return pr[:2]
            NEXT_CACHE = None
            print("cache reset!", file=sys.stderr)
    res = solve(board, turn, ob, min(remain_time, 20000))
    NEXT_CACHE = deque(res[2])
    pr = NEXT_CACHE.popleft()
    if pr[3] > 1:
        print("emit {} chain ({})".format(pr[3], res[0]), file=sys.stderr)
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
