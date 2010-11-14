#!/usr/bin/env python
'''
Rules as interpreted from:
http://en.wikipedia.org/wiki/Rules_of_Go
'''
import unittest
import gogogo

def default_setUp(self):
    self.new_board = lambda *args, **kwargs: gogogo.BoardState(*args, **kwargs)
    self.board = self.new_board()
    def set_board_positions(**positions):
        for color, locs in positions.items():
            [self.board._set(x, y, color) for (x, y) in locs]
    self.set_board_positions = set_board_positions

class SimpleBoardStateTests(unittest.TestCase):
    setUp = default_setUp

    def tearDown(self):
        pass

    def test_distance_function(self):
        self.assertEqual(int(self.board._distance((0,0), (0, 1))), 1, "Two points are 1 unit appart")
        self.assertEqual(int(self.board._distance((0,0), (0, 2))), 2, "Two points are 2 unit appart")
        self.assertEqual(int(self.board._distance((0,0), (1, 1))), 1, "Two points are 1 unit appart by diagonal")
        self.assertEqual(int(self.board._distance((0,0), (0, 0))), 0, "Two points the same")

    def test_two_players(self):
        self.assertEqual(len(self.board.players), 2, "Game needs two players")

    def test_board_has_size(self):
        self.assertTrue(self.board.width > 0, "Board needs to have a width")
        self.assertTrue(self.board.height > 0, "Board needs to have a height")

    def test_intersection_has_value(self):
        self.board._set(0, 0, "Black")
        self.assertEqual(type(self.board._get(0, 0)), gogogo.Position, "Value of intersection is returnable.")

    def test_intersection_only_takes_valid_state(self):
        self.assertTrue(self.new_board()._set(0, 0, None), "A space should be able to be clear")
        self.assertTrue(self.new_board()._set(0, 0, "Black"), "A space should be able to be black")
        self.assertTrue(self.new_board()._set(0, 0, "White"), "A space should be able to be white")

    def test_intersection_can_only_have_one_value(self):
        self.board._set(0, 0, "Black")
        self.board._set(0, 0, "White")
        self.assertEqual(len(self.board.positions), 1, "A space can only have one position")

    def test_blank_positions_are_not_stored(self):
        self.board._set(0, 0, None)
        self.assertEqual(len(self.board.positions), 0, "We should not be keeping track of empty squares")
        self.board._set(1, 1, "Black")
        self.board._set(1, 1, None)
        self.assertEqual(len(self.board.positions), 0, "Clearing a square should remove the position.")

class BoardStateSimpleGroupTests(unittest.TestCase):
    setUp = default_setUp

    def tearDown(self):
        pass

    def test_two_interersections_are_connected(self):
        self.assertTrue(self.board.is_chain((1,1),(1,2)), "Intersections are connected if a path exists between them")
        self.assertTrue(self.board.is_chain((1,1),(3,6)), "Intersections are connected if a longer path exists between them")

    def test_two_intersections_not_connected(self):
        b, w = "Black", "White"
        self.board._set(0, 1, b)
        self.board._set(1, 0, b)
        self.assertFalse(self.board.is_chain((0,0),(1,1)), "Two intersections with no path without diagonals of equal state are not connected")

    def test_two_stones_connected(self):
        self.board._set(5, 5, 'Black')
        self.board._set(5, 6, 'Black')
        self.assertTrue(self.board.is_chain((5,5), (5,6)), "Two 90deg adjacent stones are connected")

    def test_two_diagonal_stones_not_connected(self):
        self.board._set(5, 5, 'Black')
        self.board._set(6, 6, 'Black')
        self.assertFalse(self.board.is_chain((5,5), (6,6)), "Two 90deg adjacent stones are connected")

class BoardStateTests(unittest.TestCase):
    setUp = default_setUp

    def tearDown(self):
        pass

    def test_complex_shape_is_connected(self):
        b = 'Black'
        all = [self.board._set(0, 0, b),
               self.board._set(0, 1, b),
               self.board._set(1, 1, b),
               self.board._set(1, 2, b)]
        all_connected = reduce(lambda acc, p: acc and
                                              (len([t for t in all
                                                      if self.board.is_chain((p.x, p.y), (t.x, t.y))]) == len(all)),
                               all, True)
        self.assertTrue(all_connected, "A shape of three pairs at 90deg angles, all peices are connected")

    def test_shape_knows_all_members(self):
        members = [self.board._set(x, y, "Black") for (x, y) in
                   [(0,0),
                    (0,1),
                    (1, 0)]]
        shape = self.board.shape_at(0, 0)
        all_present = len(members) == len([m for m in shape.members if m in members]) == shape.size
        self.assertTrue(all_present, "A shape should be able to tell me its members")

    def test_two_complex_shapes_are_distinct(self):
        self.set_board_positions(Black=((10, 10),
                                        (9, 10),
                                        (8, 10),
                                        (7, 9),
                                        (6, 9),
                                        (5, 9)))
        shape1 = self.board.shape_at(10,10)
        self.assertTrue(shape1, "There is a shape that touches (10, 10)")
        shape2 = self.board.shape_at(6, 9)
        self.assertTrue(shape2, "There is a shape that touches (6, 9)")
        self.assertNotEqual(shape1, shape2, "Two shapes are present because of a diagonal")

    def test_board_can_find_all_shapes_for_player(self):
        [self.board._set(x, y, "Black") for (x, y)
         in [(10, 10),
             (9, 10),
             (8, 10),
             (7, 9),
             (6, 9),
             (5, 9)]]
        self.board._set(18, 18, "White")
        black_shapes = self.board.all_objects_of("Black")
        white_shapes = self.board.all_objects_of("White")
        self.assertEqual(len(black_shapes), 2, "There are two shapes that black owns")
        self.assertEqual(len(white_shapes), 1, "There is one shape that white owns")
        self.assertEqual(black_shapes[0].owner, "Black", "Black should own black shapes")

    def test_liberty_is_adjecent_empty_space_of_stone(self):
        p = self.board._set(1, 1, "Black")
        self.board._set(0, 1, "Black")
        self.assertTrue(p.is_liberty(1, 0), "A Liberty is an adjecent empty space of stone")
        self.assertFalse(p.is_liberty(0, 1), "A Liberty is an adjecent _empty_ space of stone")

    def test_single_stone_has_four_liberties(self):
        p = self.board._set(1, 1, "Black")
        self.assertEqual(len(p.liberties), 4, "A single stone has four liberties")

    def test_single_oposing_stone_removes_liberty(self):
        p = self.board._set(1, 1, "Black")
        before = p.liberties
        self.board._set(0, 1, "White")
        after = p.liberties
        self.assertEqual(len(after), len(before) - 1, "An adjacent oposing stone, decrements a stone's liberties")

    def test_group_shares_liberties(self):
        self.board._set(10, 10, "Black")
        self.board._set(10, 11, "Black")
        self.board._set(9, 10, "Black")
        shape = self.board.shape_at(10, 10)
        self.assertEqual(len(shape.liberties), 7, "Adding a connected stone shares the liberties of both stones")

    def test_shape_can_count_liberties(self):
        self.board._set(10, 10, "Black")
        self.board._set(10, 11, "Black")
        self.board._set(9, 10, "Black")
        self.board._set(8, 10, "Black")
        self.board._set(8, 11, "Black")
        self.board._set(8, 12, "Black")
        self.board._set(8, 13, "Black")
        self.board._set(7, 12, "Black")

        self.board._set(7, 10, "White")
        self.board._set(9, 11, "White")

        shape = self.board.shape_at(10, 10)

        self.assertEqual(len(shape.liberties), 12, "A shape should correctly count its liberties")

class BoardMoveTests(unittest.TestCase):
    setUp = default_setUp

    def tearDown(self):
        pass

    def test_start_board_is_empty(self):
        self.assertEqual(len(self.board.positions), 0, "Initial board is empty")

    def test_know_who_plays_next(self):
        self.assertEqual(self.board.player_turn(), self.board.players[0], "Board should know who's move it is")

    def test_players_move_alternate(self):
        self.assertEqual(self.board.player_turn(), self.board.players[0], "Black moves first")
        self.board.move(None) #Pass
        self.assertEqual(self.board.player_turn(), self.board.players[1], "Players turn should alternate")


    def test_player_can_pass(self):
        self.board.move(None)
        self.assertEqual(self.board.player_turn(), self.board.players[1], "Player can pass a turn")

    def test_play_steps(self):
        def step_1_move_to_empty_space():
            self.assertEqual(self.board.player_turn(), self.board.players[0], "It should be the first player's turn")
            m = self.board.move(6, 3)
            self.assertTrue(m, "Player can play empty intersection")

        def step_2_player_removes_opposing_liberty_free_stones():
            self.assertFalse(self.board._get(6, 4), "Player removes oposing stones with no liberties")

        def step_3_conditional_suicide():
            self.board.move(2, 0)

            if not self.board.self_capture_allowed:
                m = self.board.move(1, 0)
                self.assertFalse(m, "Self capture is not allowed")
                self.assertEqual(self.board.player_turn(), self.board.players[0], "Should still be black's turn")
            else:
                self.assertTrue(self.board.move(1, 0), "Self capture is allowed")
                self.assertEqual(self.board.player_turn(), self.board.players[1], "Should now be white's turn")

        [self.board._set(x, y, color) for (x, y, color) in [(bx, by, "Black") for (bx, by) in [(0, 0),
                                                                                               (5, 5), (6, 5), (7, 5),
                                                                                               (5, 4),         (7, 4),
                                                                                               (5, 3),
                                                                                               ]] +
                                                           [(wx, wy, "White") for (wx, wy) in [(18, 18),
                                                                                                       (6, 4),

                                                                                               (0, 1), (1, 1), (2, 1),
                                                                                               ]]]

        [step() for step in (step_1_move_to_empty_space,
                             step_2_player_removes_opposing_liberty_free_stones,
                             step_3_conditional_suicide)]

    def test_turn_must_not_recreate_prior_state(self):
        [self.board._set(x, y, color) for (x, y, color) in [(bx, by, "Black") for (bx, by) in [(0, 0),
                                                                                                       (6, 6),
                                                                                               (5, 5),
                                                                                                       (6, 4),
                                                                                               ]] +
                                                           [(wx, wy, "White") for (wx, wy) in [(18, 18),
                                                                                                       (7, 6),
                                                                                               (6, 5),         (8, 5),
                                                                                                       (7, 4),
                                                                                               ]]]

        #Black captures
        self.board.move(7, 5)

        #White tries to capture, but it's illegal as it would be the same as before last move
        m = self.board.move(6, 5)
        self.assertFalse(m, "A move can't create a boad state that existed in the past")



    def test_game_ends_after_two_consecutive_passes(self):
        m = self.board.move(None)
        self.assertTrue(m, "Black can pass")
        m = self.board.move(None)
        self.assertTrue(m, "White can pass")
        self.assertTrue(self.board.game_over, "Back-to back passes should end a game")

class BoardSerializationTests(unittest.TestCase):
    setUp = default_setUp

    def tearDown(self):
        pass

    def test_board_can_become_json(self):
        self.assertTrue(len(self.board.as_json()) >= 2, "Serialization must reply with a string of length")
        self.assertTrue(self.board.as_json().startswith('{') and self.board.as_json().endswith('}'), "JSON encodings must begin with { and end with }")

        import json
        try: json.loads(self.board.as_json())
        except: self.fail("JSON returned must be valid")

    def test_board_with_positions_can_json(self):
        blank_json = self.board.as_json()
        self.board._set(5, 5, "Black")
        self.board._set(1, 2, "White")
        after_json = self.board.as_json()
        self.assertNotEqual(blank_json, after_json, "JSON serialization should changes with board")
        self.assertTrue(len(blank_json) < len(after_json), "Size of after json should increased since we added data")
        self.board.dump_board()

    def test_can_deserialize_board_with_same_positions(self):
        self.board.move(0, 0)
        self.board.move(1, 1)
        self.board.move(5, 5)
        self.board.move(10, 10)
        new_board = gogogo.BoardState.from_json(self.board.as_json())
        self.assertTrue(False, "New board should have the same positions as old board")



class BoardScoreTests(unittest.TestCase):
    setUp = default_setUp

    def tearDown(self):
        pass

    def test_determine_ownership_of_intersection(self):
        owner = self.board.get_owner_of(10, 10)
        self.assertEqual(owner, None, "(10, 10) on an empty board is neutral")
        self.board.move(10, 10)
        self.assertEqual(self.board.get_owner_of(10, 10), self.board.players[0], "An owned square belongs to the peice owner")
        self.board = self.new_board()
        [self.board._set(x, y, color) for (x, y, color) in [(bx, by, "Black") for (bx, by) in [(0, 5), (1, 5), (2, 5),
                                                                                                               (2, 4),
                                                                                                               (2, 3),
                                                                                                               (2, 2),
                                                                                                               (2, 1),
                                                                                                               (2, 0),
                                                                                               ]] +
                                                           [(wx, wy, "White") for (wx, wy) in [(18, 18),
                                                                                               (3, 2), (4, 2), (5, 2), (6, 2),
                                                                                                                       (6, 1),
                                                                                                                       (6, 0),
                                                                                               ]]]
        self.assertEqual(self.board.get_owner_of(0, 0), "Black", "Empty space surrounded by a single color is owned by that color")
        self.assertEqual(self.board.get_owner_of(4, 0), None, "Empty space that connects to more than one color is neutral")

    def test_determine_player_area(self):
        self.set_board_positions(Black=[(0, 5), (1, 5), (2, 5),
                                                        (2, 4),
                                                        (2, 3),
                                                        (2, 2),
                                                        (2, 1),
                                                        (2, 0),
                                        ],
                                 White=[(18, 18),
                                        (3, 2), (4, 2), (5, 2), (6, 2),
                                                                (6, 1),
                                                                (6, 0),
                                        ])
        shape = self.board.shape_at(0, 0)
        self.assertTrue(shape, "Shapes of empty squares can be considered for area calculation")
        self.assertEqual(shape.owner, "Black", "Intersections belong to players area if the player ownes the intersection, or has a stone on it")
        shape = self.board.shape_at(3, 0)
        self.assertEqual(shape.owner, None, "Areas that are contested have no owner")

    def test_determine_winner(self):
        self.set_board_positions(Black=[(0, 5), (1, 5), (2, 5),
                                                        (2, 4),
                                                        (2, 3),
                                                        (2, 2),
                                                        (2, 1),
                                                        (2, 0),
                                        ],
                                 White=[(18, 18),
                                        (0, 6), (1, 6), (2, 6), (3, 6),
                                                                (3, 5),
                                                                (3, 4),
                                                                (3, 3),
                                                                (3, 2),
                                                                (3, 1),
                                                                (3, 0),
                                        ])
        self.assertEqual(self.board.winner, "White", "Winner should be the player with the highest area")

    def test_understand_draw(self):
        self.assertEqual(self.board.winner, None, "Equal scores draw the game")

if __name__ == '__main__':
    unittest.main()
