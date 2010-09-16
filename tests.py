'''
Rules as interpreted from:
http://en.wikipedia.org/wiki/Rules_of_Go
'''
import unittest

class BoardStateTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def test_two_players(self):
        self.assertTrue(False, "Game needs two players")
    
    def test_board_has_size(self):
        self.assertTrue(False, "Board needs to be n by m where n>=m>0")

    def test_intersection_only_takes_valid_state(self):
        self.assertTrue(False, "A space can only have nothing, black, or white")

    def test_two_interersections_are_connected(self):
        self.assertTrue(False, "Intersections are connected if a path exists between them")

    def test_two_intersections_not_connected(self):
        self.assertTrue(False, "Two intersections with no path without diagonals of equal state are not connected")

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

    def test_liberty_is_adjecent_empty_space_of_stone(self):
        self.assertTrue(False, "A Liberty is an adjecent empty space of stone")

    def test_single_stone_has_four_liberties(self):
        self.assertTrue(False, "A single stone has four liberties")

    def test_single_oposing_stone_removes_liberty(self):
        self.assertTrue(False, "An adjacent oposing stone, decrements a stone's liberties")

    def test_group_shares_liberties(self):
        self.assertTrue(False, "Adding a connected stone shares the liberties of both stones")

    def test_shape_can_count_liberties(self):
        self.assertTrue(False, "A shape should correctly count its liberties")

class BoardMoveTests(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def test_start_board_is_empty(self):
        self.assertTrue(False, "Initial board is empty")

    def test_know_who_plays_next(self):
        self.assertTrue(False, "Board should know who's move it is")

    def test_players_move_alternate(self):
        self.assertTrue(False, "Player move changes each turn")

    def test_player_can_pass(self):
        self.assertTrue(False, "Player can pass a turn")

    def test_play_steps(self):
        def step_1_move_to_empty_space():
            self.assertTrue(False, "Player can play empty intersection")

        def step_2_player_removes_opposing_liberty_free_stones():
            self.assertTrue(False, "Player removes oposing stones with no liberties")

        def step_3_conditional_suicide():
            if True: #TODO: Conditional
                self.assertTrue(False, "Self capture is not allowed")
            else:
                self.assertTrue(False, "Self capture is allowed")

        [step() for step in (step_1_move_to_empty_space,
                             step_2_player_removes_opposing_liberty_free_stones,
                             step_3_conditional_suicide)]

    def test_turn_must_not_recreate_prior_state(self):
        self.assertTrue(False, "A move can't create a boad state that existed in the past")

    def test_game_ends_after_two_consecutive_passes(self):
        self.assertTrue(False, "Back-to back passes should end a game")

class BoardScoreTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_determine_ownership_of_intersection(self):
        self.assertTrue(False, "Should know if an intersection belongs to a player, or is neutral")
        self.assertTrue(False, "Territory belongs to a player if there is no path to a point adjacent to oposing area")

    def test_determine_player_area(self):
        self.assertTrue(False, "Intersections belong to players area if the player ownes the intersection, or has a stone on it")

    def test_determine_winner(self):
        self.assertTrue(False, "Winner should be the player with the highest area")
        
    def test_understand_draw(self):
        self.assertTrue(False, "Equal scores draw the game")

    



if __name__ == '__main__':
    unittest.main()
