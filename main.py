#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import random
import itertools
import functools
import operator


AI_NAME = "efuteai"
WIDTH = 10
HEIGHT = 16
PACK_SIZE = 3
SUMMATION = 10
MAX_TURN = 500
OBSTACLE = SUMMATION + 1
EMPTY = 0
PACKS = []


def rot1(pack):
    return [[pack[PACK_SIZE - 1 - i][j] for i in range(PACK_SIZE)] for j in range(PACK_SIZE)]


def rotate_pack(pack, rot):
    return functools.reduce(lambda x, _: rot1(x), range(rot), pack)


def input_packs():
    pack = [[int(i) for i in input().split()] for _ in range(PACK_SIZE)]
    _ = input()
    return pack


def input_initial():
    global WIDTH, HEIGHT, PACK_SIZE, SUMMATION, MAX_TURN, OBSTACLE, PACKS
    WIDTH, HEIGHT, PACK_SIZE, SUMMATION, MAX_TURN = [int(x) for x in input().split()]
    OBSTACLE = SUMMATION + 1
    PACKS = [input_packs() for _ in range(MAX_TURN)]


def fill_obstacle(pack, num):
    idx = itertools.islice(
        ((i, j) for i in range(PACK_SIZE) for j in range(PACK_SIZE) if pack[i][j] == EMPTY),
        num
    )
    p = [row[:] for row in pack]
    for i in idx:
        p[i[0]][i[1]] = OBSTACLE
    return p


def is_fallable(pack, x):
    if 0 <= x <= WIDTH - PACK_SIZE: return True
    return all(ee == EMPTY for i, e in enumerate(zip(*pack)) if not 0 <= x + i < WIDTH for ee in e)


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

    rot = random.randrange(0, 4)
    pack = fill_obstacle(PACKS[turn], max(obstacle_num - enemy_obstacle_num, 0))
    pack = rotate_pack(pack, rot)

    left = -PACK_SIZE + 1
    right = WIDTH
    while not is_fallable(pack, left): left += 1
    while not is_fallable(pack, right - 1): right -= 1
    col = random.randrange(left, right)
    return col, rot


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
