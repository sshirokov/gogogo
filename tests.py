#!/usr/bin/env python
'''
Rules as interpreted from:
http://en.wikipedia.org/wiki/Rules_of_Go
'''
import unittest
import gogogo

class SimpleBoardStateTests(unittest.TestCase):
    def setUp(self):
        def get_default_board():
            return gogogo.BoardState()
        self.get_default_board = get_default_board

    def tearDown(self):
        pass

    def test_distance_function(self):
        board = self.get_default_board()
        self.assertEqual(int(board._distance((0,0), (0, 1))), 1, "Two points are 1 unit appart")
        self.assertEqual(int(board._distance((0,0), (0, 2))), 2, "Two points are 2 unit appart")
        self.assertEqual(int(board._distance((0,0), (1, 1))), 1, "Two points are 1 unit appart by diagonal")
        self.assertEqual(int(board._distance((0,0), (0, 0))), 0, "Two points the same")
        
    def test_two_players(self):
        board = self.get_default_board()
        self.assertEqual(len(board.players), 2, "Game needs two players")

    def test_board_has_size(self):
        board = self.get_default_board()
        self.assertTrue(board.width > 0, "Board needs to have a width")
        self.assertTrue(board.height > 0, "Board needs to have a height")

    def test_intersection_only_takes_valid_state(self):
        new_board = lambda: self.get_default_board()
        self.assertTrue(new_board()._set(0, 0, None), "A space should be able to be clear")
        self.assertTrue(new_board()._set(0, 0, "Black"), "A space should be able to be black")
        self.assertTrue(new_board()._set(0, 0, "White"), "A space should be able to be white")

    def test_intersection_can_only_have_one_value(self):
        board = self.get_default_board()
        board._set(0, 0, "Black")
        board._set(0, 0, "White")
        self.assertEqual(len(board.positions), 1, "A space can only have one position")

    def test_blank_positions_are_not_stored(self):
        board = self.get_default_board()
        board._set(0, 0, None)
        self.assertEqual(len(board.positions), 0, "We should not be keeping track of empty squares")
        board._set(1, 1, "Black")
        board._set(1, 1, None)
        self.assertEqual(len(board.positions), 0, "Clearing a square should remove the position.")

class BoardStateSimpleGroupTests(unittest.TestCase):
    def setUp(self):
        def get_default_board():
            return gogogo.BoardState()
        self.get_default_board = get_default_board

    def tearDown(self):
        pass

    def test_two_interersections_are_connected(self):
    	board = self.get_default_board()
        self.assertTrue(board.is_chain((1,1),(1,2)), "Intersections are connected if a path exists between them")
        self.assertTrue(board.is_chain((1,1),(3,6)), "Intersections are connected if a longer path exists between them")

    def test_two_intersections_not_connected(self):
        self.assertTrue(False, "Two intersections with no path without diagonals of equal state are not connected")

    def test_two_stones_connected(self):
        self.assertTrue(False, "Two 90deg adjacent stones are connected")

    def test_two_empty_spaces_are_connected(self):
        self.assertTrue(False, "Two 90deg adjacent empties are connected")

    def test_two_diagonal_stones_not_connected(self):
        self.assertFalse(True, "Two stones diagnoally do not connect")

class BoardStateTests(unittest.TestCase):
    def setUp(self):
        def get_default_board():
            return gogogo.BoardState()
        self.get_default_board = get_default_board

    def tearDown(self):
        pass
    
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
