import unittests

class BoardStateTests(unittest.TestCase):
    def test_two_players(self):
        self.assertTrue(False, "Game needs two players")
    
    def test_board_has_size(self):
        self.assertTrue(False, "Board needs to be n by m where n>=m>0")

    def test_intersection_only_takes_valid_state(self):
        self.assertTrue(False, "A space can only have nothing, black, or white")

    def test_two_stones_connected(self):
        self.assertTrue(False, "Two 90deg adjacent stones are connected")

    def test_two_empty_spaces_are_connected(self):
        self.assertTrue(False, "Two 90deg adjacent empties are connected")

    def test_two_diagonal_stones_not_connected(self):
        self.assertFalse(True, "Two stones diagnoally do not connect")

    def test_complex_shape_is_connected(self):
        self.assertTrue(False, "A shape of three pairs at 90deg angles, are connected")

    def test_two_complex_shapes_are_distinct(self):
        self.assertTrue(False, "Two shapes are present because of a diagonal")

    
