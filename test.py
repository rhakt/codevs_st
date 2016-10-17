import unittest
import main


class Test(unittest.TestCase):

    def test_single_rot(self):
        pack_before = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        pack_after = [[6, 3, 0], [7, 4, 1], [8, 5, 2]]
        self.assertEqual(main.rot1(pack_before), pack_after)

    def test_multi_rot(self):
        pack = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
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
        self.assertEqual(main.fill_obstacle(pack, 0), [[0, 1, 0], [0, 4, 5], [0, 7, 8]])
        self.assertEqual(main.fill_obstacle(pack, 1), [[11, 1, 0], [0, 4, 5], [0, 7, 8]])
        self.assertEqual(main.fill_obstacle(pack, 2), [[11, 1, 11], [0, 4, 5], [0, 7, 8]])
        self.assertEqual(main.fill_obstacle(pack, 3), [[11, 1, 11], [11, 4, 5], [0, 7, 8]])
        self.assertEqual(main.fill_obstacle(pack, 4), [[11, 1, 11], [11, 4, 5], [11, 7, 8]])

    def test_fallable(self):
        pack1 = [[0, 0, 1], [0, 0, 1], [0, 0, 1]]
        pack2 = [[1, 1, 0], [1, 1, 0], [1, 1, 0]]
        pack3 = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        pack4 = [[1, 0, 1], [1, 0, 1], [1, 0, 1]]
        self.assertEqual(main.is_fallable(pack1, -2), True)
        self.assertEqual(main.is_fallable(pack1, -1), True)
        self.assertEqual(main.is_fallable(pack1, 0), True)
        self.assertEqual(main.is_fallable(pack1, 7), True)
        self.assertEqual(main.is_fallable(pack1, 8), False)
        self.assertEqual(main.is_fallable(pack1, 9), False)
        self.assertEqual(main.is_fallable(pack2, -2), False)
        self.assertEqual(main.is_fallable(pack2, -1), False)
        self.assertEqual(main.is_fallable(pack2, 0), True)
        self.assertEqual(main.is_fallable(pack2, 7), True)
        self.assertEqual(main.is_fallable(pack2, 8), True)
        self.assertEqual(main.is_fallable(pack2, 9), False)
        self.assertEqual(main.is_fallable(pack3, -2), True)
        self.assertEqual(main.is_fallable(pack3, -1), True)
        self.assertEqual(main.is_fallable(pack3, 0), True)
        self.assertEqual(main.is_fallable(pack3, 7), True)
        self.assertEqual(main.is_fallable(pack3, 8), True)
        self.assertEqual(main.is_fallable(pack3, 9), True)
        self.assertEqual(main.is_fallable(pack4, -2), False)
        self.assertEqual(main.is_fallable(pack4, -1), False)
        self.assertEqual(main.is_fallable(pack4, 0), True)
        self.assertEqual(main.is_fallable(pack4, 7), True)
        self.assertEqual(main.is_fallable(pack4, 8), False)
        self.assertEqual(main.is_fallable(pack4, 9), False)


if __name__ == '__main__':
    unittest.main()
