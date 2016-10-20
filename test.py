import unittest
from copy import deepcopy
import main


class Test(unittest.TestCase):

    def test_single_rot(self):
        pack_before = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        pack_after  = [[6, 3, 0], [7, 4, 1], [8, 5, 2]]
        self.assertEqual(main.rot1(pack_before), pack_after)

    def test_multi_rot(self):
        pack  = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        pack1 = [[6, 3, 0], [7, 4, 1], [8, 5, 2]]
        pack2 = [[8, 7, 6], [5, 4, 3], [2, 1, 0]]
        pack3 = [[2, 5, 8], [1, 4, 7], [0, 3, 6]]
        self.assertEqual(main.rotate_pack(pack, 0), pack)
        self.assertEqual(main.rotate_pack(pack, 1), pack1)
        self.assertEqual(main.rotate_pack(pack, 2), pack2)
        self.assertEqual(main.rotate_pack(pack, 3), pack3)
        self.assertEqual(main.rotate_pack(pack, 4), pack)

    def test_fill_obstacle(self):
        pack = [[0, 1, 0], [0, 4, 5], [0, 7, 8]]
        self.assertEqual(main.fill_obstacle(pack, 0), ([[0,  1,  0], [0,  4, 5], [0,  7, 8]], 0))
        self.assertEqual(main.fill_obstacle(pack, 1), ([[11, 1,  0], [0,  4, 5], [0,  7, 8]], 0))
        self.assertEqual(main.fill_obstacle(pack, 2), ([[11, 1, 11], [0,  4, 5], [0,  7, 8]], 0))
        self.assertEqual(main.fill_obstacle(pack, 3), ([[11, 1, 11], [11, 4, 5], [0,  7, 8]], 0))
        self.assertEqual(main.fill_obstacle(pack, 4), ([[11, 1, 11], [11, 4, 5], [11, 7, 8]], 0))
        self.assertEqual(main.fill_obstacle(pack, 5), ([[11, 1, 11], [11, 4, 5], [11, 7, 8]], 1))

    def test_fallable(self):
        pack1 = [[0, 0, 1], [0, 0, 1], [0, 0, 1]]
        pack2 = [[1, 1, 0], [1, 1, 0], [1, 1, 0]]
        pack3 = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        pack4 = [[1, 0, 1], [1, 0, 1], [1, 0, 1]]
        self.assertEqual(main.is_fallable(pack1, -2), True)
        self.assertEqual(main.is_fallable(pack1, -1), True)
        self.assertEqual(main.is_fallable(pack1,  0), True)
        self.assertEqual(main.is_fallable(pack1,  7), True)
        self.assertEqual(main.is_fallable(pack1,  8), False)
        self.assertEqual(main.is_fallable(pack1,  9), False)
        self.assertEqual(main.is_fallable(pack2, -2), False)
        self.assertEqual(main.is_fallable(pack2, -1), False)
        self.assertEqual(main.is_fallable(pack2,  0), True)
        self.assertEqual(main.is_fallable(pack2,  7), True)
        self.assertEqual(main.is_fallable(pack2,  8), True)
        self.assertEqual(main.is_fallable(pack2,  9), False)
        self.assertEqual(main.is_fallable(pack3, -2), True)
        self.assertEqual(main.is_fallable(pack3, -1), True)
        self.assertEqual(main.is_fallable(pack3,  0), True)
        self.assertEqual(main.is_fallable(pack3,  7), True)
        self.assertEqual(main.is_fallable(pack3,  8), True)
        self.assertEqual(main.is_fallable(pack3,  9), True)
        self.assertEqual(main.is_fallable(pack4, -2), False)
        self.assertEqual(main.is_fallable(pack4, -1), False)
        self.assertEqual(main.is_fallable(pack4,  0), True)
        self.assertEqual(main.is_fallable(pack4,  7), True)
        self.assertEqual(main.is_fallable(pack4,  8), False)
        self.assertEqual(main.is_fallable(pack4,  9), False)

    def test_fall_pack(self):
        board = [[main.EMPTY] * main.HEIGHT for _ in range(main.WIDTH)]
        board[2][main.HEIGHT-1] = main.OBSTACLE
        pack = [[1, 0, 3], [4, 0, 0], [0, 8, 9]]
        bb = deepcopy(board)
        bb[1][main.HEIGHT - 1] = pack[1][0]
        bb[1][main.HEIGHT - 2] = pack[0][0]
        bb[2][main.HEIGHT - 2] = pack[2][1]
        bb[3][main.HEIGHT - 1] = pack[2][2]
        bb[3][main.HEIGHT - 2] = pack[0][2]
        self.assertEqual(main.fall_pack(board, pack, 1), bb)
        for j in range(main.HEIGHT):
            board[2][j] = main.OBSTACLE
        self.assertEqual(main.fall_pack(board, pack, 1), None)

    def test_gravity(self):
        b = [[main.EMPTY] * main.HEIGHT for _ in range(main.WIDTH)]
        c = deepcopy(b)
        b[2][main.HEIGHT - 4] = main.OBSTACLE
        c[2][main.HEIGHT - 1] = main.OBSTACLE
        b[5][main.HEIGHT - 9] = 3
        c[5][main.HEIGHT - 1] = 3
        b[5][main.HEIGHT - 10] = 2
        c[5][main.HEIGHT - 2] = 2
        main.force_gravity(b)
        self.assertEqual(b, c)

    def test_anni_board(self):
        b = [[main.EMPTY] * main.HEIGHT for _ in range(main.WIDTH)]
        c = deepcopy(b)
        d = deepcopy(b)
        b[5][main.HEIGHT - 1] = 5
        b[6][main.HEIGHT - 1] = 5
        b[5][main.HEIGHT - 2] = 5
        b[6][main.HEIGHT - 2] = 2
        b[7][main.HEIGHT - 1] = 3
        b[8][main.HEIGHT - 1] = 5
        c[6][main.HEIGHT - 1] = 2
        c[7][main.HEIGHT - 1] = 3
        c[8][main.HEIGHT - 1] = 5
        anni, b = main.anni_board(b)
        self.assertEqual(anni, 6)
        self.assertEqual(b, c)
        anni, b = main.anni_board(b)
        self.assertEqual(anni, 3)
        self.assertEqual(b, d)
        anni, b = main.anni_board(b)
        self.assertEqual(anni, 0)
        self.assertEqual(b, d)

    def test_evaluate_board(self):
        b = [[main.EMPTY] * main.HEIGHT for _ in range(main.WIDTH)]
        b[5][main.HEIGHT - 1] = 5
        b[6][main.HEIGHT - 1] = 5
        b[5][main.HEIGHT - 2] = 5
        b[6][main.HEIGHT - 2] = 2
        b[7][main.HEIGHT - 1] = 3
        b[8][main.HEIGHT - 1] = 5
        score, chain = main.evaluate_board(b)
        self.assertEqual(chain, 2)
        self.assertEqual(score, 4)


if __name__ == '__main__':
    unittest.main()
