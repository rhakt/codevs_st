from main import *

AI_NAME = "simpleAI"


def process_turn_simple():
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


def simple():
    random.seed(800000002)
    print(AI_NAME)
    sys.stdout.flush()
    input_initial()
    try:
        while True:
            print(*process_turn_simple())
            sys.stdout.flush()
    except KeyboardInterrupt as _:
        pass
    except Exception as e:
        print("error: {0}".format(e), file=sys.stderr)


if __name__ == '__main__':
    simple()
