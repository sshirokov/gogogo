#!/usr/bin/env python
import sys, math

class BoardError(Exception): pass
class HistoryInvalid(BoardError): pass
class InvalidPosition(BoardError): pass
class DuplicatePosition(BoardError): pass
class NotValidShape(BoardError): pass

class Move(object):
    def __init__(self, player, *pass_or_x_y):
        self.player = player
        self.passing = len(pass_or_x_y) == 1
        if not self.passing:
            self.x, self.y = pass_or_x_y

    def __repr__(self):
        return "<Move: %s %s>" % (self.player, self.passing and "Pass" or (self.x, self.y))


class TargettedPoint(object):
    def __init__(self, x, y, target):
        self.x, self.y = x, y
        self.target = target

    @property
    def pair(self):
        return (self.x, self.y)

    def distance_between(self, a, b):
        (x1, y1), (x2, y2) = a, b
        dx2 = math.pow(x1-x2, 2)
        dy2 = math.pow(y1-y2, 2)
        return math.sqrt(dx2 + dy2)

    @property
    def distance(self):
        if getattr(self, "distance_cache", None) == None:
            self.distance_cache = self.distance_between(self.pair, self.target)
        return self.distance_cache
    
    def __cmp__(self, other):
        return cmp(self.distance, other.distance)

    def __repr__(self):
        return "<Point: (%s, %s) |%s|>" % (self.x, self.y, self.distance)

class Shape(object):
    def __init__(self, board, x, y):
        self.board = board
        self.initial = board._get(x, y) or (self.board.position_exists(x, y) and (x, y))
        self.members = []
        if not self.initial: raise NotValidShape()
        self.discover_members()

    @property
    def owner(self):
        owned = True
        return self.type or "TODO: Fuck"

    @property
    def type(self):
        return getattr(self.members[0], 'owner', None)

    @property
    def size(self):
        return len(self.members)

    @property
    def liberties(self):
        liberties = set()
        [liberties.update(p.liberties) for p in self.members]
        return list(liberties)

    def discover_members(self):
        self.members = []

        def neighbors_of_same_owner(p):
            def point_considered_for_p(pp):
                if not pp: return False
                if type(pp) != type(p): return False
                if type(p) == tuple: return True
                if p.owner == pp.owner: return True
                return False

            return self.board.neighbors_of(p, transform=lambda *loc: self.board._get(*loc) or loc,
                                              test=point_considered_for_p)

        def walk_network(point):
            if point in self.members: return
            self.members.append(point)
            [walk_network(p) for p in neighbors_of_same_owner(point)]
        walk_network(self.initial)

    def __eq__(self, other):
        return (self.size == other.size and
                sorted(self.members) == sorted(other.members))


    def __repr__(self):
        return "<Shape: size=%s owner=%s type=%s>" % (self.size, self.owner, self.type)



class Position(object):
    def __init__(self, board, x, y, owner, **options):
        self.board, self.x, self.y, self.owner = board, x, y, owner
        self.tag = None
        [setattr(self, key, val) for (key, val) in options]

    @property
    def edges(self):
        return self.board.neighbors_of(self)

    @property
    def liberties(self):
        return [loc for loc in self.edges if self.is_liberty(*loc)]

    def is_liberty(self, x, y):
        return (x, y) in self.edges and not self.board._get(x, y)

    def __eq__(self, other):
        return (self.x == other.x and
                self.y == other.y and
                self.owner == other.owner and
                self.board == other.board)

    def __cmp__(self, other):
        p = "(%s, %s)"
        return cmp(p % (self.x, self.y),
                   p % (other.x, other.y))

    def __repr__(self):
        return "Position: (%s, %s) => %s" % (self.x, self.y, self.owner)

class BoardState(object):
    def __init__(self, *players, **options):
        '''
        Call with __init__(list, of players, width=n, height=m...)
        '''
        options = dict({'width': 19,
                        'height': 19,
                        'players': players or ['Black', 'White'],
                        'moves': [],
                        'last_move_message': '',
                        'positions': [],
                        'signatures': [],
                        'self_capture_allowed': False,
                        },
                       **options)
        [setattr(self, k, v) for (k, v) in options.items()]
        if not self.validate(): raise HistoryInvalid()

    def neighbors_of(self, *pos_or_loc, **kwargs):
        transform = kwargs.pop('transform', lambda *i: i)
        test = kwargs.pop('test', lambda p: True)
        if len(pos_or_loc) == 1: pos_or_loc = pos_or_loc[0]

        def coord(pp, axis):
            v = getattr(pp, axis, None)
            if v is None: v = pp[{'x': 0, 'y': 1}[axis]]
            return v

        X = lambda pp: coord(pp, 'x')
        Y = lambda pp: coord(pp, 'y')
        return [p for p in [transform(*pair) for pair in ((X(pos_or_loc) - 1, Y(pos_or_loc)),
                                                         (X(pos_or_loc) + 1, Y(pos_or_loc)),
                                                         (X(pos_or_loc), Y(pos_or_loc) - 1),
                                                         (X(pos_or_loc), Y(pos_or_loc) + 1))
                            if self.position_exists(*pair)]
                if test(p)]

    def move(self, *args, **kwargs):
        '''
        Perform move or skip turn

        move(None) => Passes the turn for the given player
        move(x, y) => Places a player's maker at (x, y) if possible

        move(..., player="Name") => Overrides the player performing the move
        '''
        passing = len(args) == 1 and args[0] == None
        x, y = (None, None)
        if not passing: x, y = args
        player = kwargs.pop('player', self.player_turn())
        snapshot = self.take_snapshot()

        if not passing:
            if self._get(x, y):
                self.last_move_message = "Not empty"
                return False
            self._set(x, y, player, sign=False)

            [[self._clear(p.x, p.y) for p in shape.members]
             for shape in self.get_captured_shapes_by(player)]

            losses = self.get_captured_shapes_of(player)
            if self.self_capture_allowed:
                self.dump_board()
                [[self._clear(p.x, p.y) for p in shape.members]
                 for shape in losses]
            elif losses:
                self.restore_snapshot(snapshot)
                self.last_move_message = "Self capture is not allowed"
                return False

        #Make a move or pass
        passing_or_xy = passing and (passing,)  or (x, y)
        self.moves.append(Move(player, *passing_or_xy))

        if not passing and not self.sign():
            self.restore_snapshot(snapshot)
            self.last_move_message = "Repeated state"
            return False

        self.last_move_message = "OK"
        return True

    @property
    def game_over(self):
        if len(self.moves) >= 2:
            return reduce(lambda acc, i: acc and i.passing, self.moves[:-2], True)
        return False

    def sign(self):
        try:
            self.signatures.index(self.signature)
            return False
        except ValueError:
            self.signatures.append(self.signature)

        return True

    @property
    def signature(self):
        '''A hash of the current game state, to be certain we won't be repeating it'''
        import hashlib
        sig = hashlib.sha512()
        [sig.update(str(pos)) for pos in sorted(self.positions)]
        return sig.hexdigest()
    
    def take_snapshot(self):
        from copy import copy
        return {'width': self.width,
                'height': self.height,
                'players': copy(self.players),
                'moves': copy(self.moves),
                'positions': copy(self.positions),
                'signatures': copy(self.signatures),}


    def restore_snapshot(self, snap):
        [setattr(self, name, value) for (name, value) in snap.items()]

    def get_opponents_of(self, player):
        return [p for p in self.players if p != player]

    def get_captured_shapes_by(self, player):
        captured = []
        [captured.extend(shapes) for shapes in
         [self.get_captured_shapes_of(oponnent)
          for oponnent in self.get_opponents_of(player)]]
        return captured

    def get_captured_shapes_of(self, player):
        return [shape for shape in
                self.all_objects_of(player)
                if len(shape.liberties) == 0]

    def all_objects_of(self, player):
        positions = [p for p in self.positions if p.owner == player]
        shapes = []
        while len(positions):
            position = positions.pop()
            shapes.append(self.shape_at(position.x, position.y))
            for p in shapes[-1].members:
                try: positions.remove(p)
                except ValueError: pass

        return list(set(shapes))

    def player_turn(self):
        return self.players[len(self.moves) % len(self.players)]

    def validate(self):
        return True

    def get_owner_of(self, x, y):
        p = self._get(x, y)
        o = None
        if p: o = p.owner
        else:
            visited = []
            touches = set()
            def visit(x, y):
                if (x, y) in visited: return
                if len(touches) > 1: return
                visited.append((x, y))
                [touches.add(p.owner) for p in [self._get(*loc) for loc in self.neighbors_of(x, y)]
                 if p]
                [visit(*loc) for loc in self.neighbors_of(*loc) if not self._get(*loc)]
            visit(x, y)
            if len(touches) == 1: o = touches.pop()
        return o

    def dump_board(self, **options):
        marks = options.pop('marks', {})
        def mark_for(x, y):
            for (mark, coord) in marks.items():
                if coord == (x, y): return mark
                if (x, y) in coord: return mark
            return None
        for y in range(self.height - 1, -1, -1):
            for x in range(self.width):
                p = self._get(x, y)
                p = getattr(p, 'owner', mark_for(x, y) or "+")[0]
                print p,
            print
        return True

    def _clean_positions(self):
        self.positions = [p for p in set(self.positions) if p.owner != None]

    def _clear(self, x, y):
        def is_cleared_position(p):
            return (p.x, p.y) == (x, y)
        self.positions = [p for p in self.positions if not is_cleared_position(p)]
        return self

    def _set(self, x, y, val, **options):
        sign = options.pop('sign', True)
        if val not in [None] + list(self.players): return False
        if not self.position_exists(x, y): raise InvalidPosition()
        self._clear(x, y)
        p = None
        if val != None:
            p = Position(self, x, y, val)
            self.positions.append(p)
        self._clean_positions()
        if sign: self.sign()
        return p or True

    def _get(self, x, y):
        '''
        Returns the value of that position. _get(x,y)
        '''
        pos = None
        pos = [p for p in self.positions if p.x == x and p.y == y]
        if len(pos) > 1: raise DuplicatePosition()
        if len(pos): pos = pos[0]
        return pos or None
    
    def position_exists(self, x, y):
        return (x >= 0) and (y >= 0) and (x < self.width) and (y < self.height)

    def is_chain(self, start, finish, **options):
        '''
        Determines if there is a path of same state from point a(x, y) to point b(x, y)
        '''
        import heapq
        loudly = options.pop('loudly', False)
        heap = []
        found = False

        def add_neighbors_of(node):
            '''Add weighted neighbors of node to the queue'''
            v = self._get(node.x, node.y)
            def neighbors_of_same_state(p):
                maybe = self.neighbors_of(p)
                #TODO: This can probably be done with a more thought out test/tranform combo
                v = getattr(self._get(p.x, p.y), 'owner', None)
                return [TargettedPoint(*loc + (finish,)) for loc in maybe if self.position_exists(*loc) and
                        getattr(self._get(*loc), 'owner', None) == v]

            for neighbor in neighbors_of_same_state(node):
                heapq.heappush(heap, neighbor)

        searching = True
        heapq.heappush(heap, TargettedPoint(start[0], start[1], finish))
        while searching:
            visit = heapq.heappop(heap)
            if loudly:
                print "Visiting:", visit
                self.dump_board(marks={'S': start, 'F': finish, 'V': (visit.x, visit.y)})
            found = int(visit.distance) == 0
            if found: break
            add_neighbors_of(visit)
            if not len(heap): searching = False

        return found

    def shape_at(self, x, y):
        try: return Shape(self, x, y)
        except NotValidShape: return None

    def _distance(self, a, b):
        if type(a) == tuple and type(b) == tuple: (x1, y1), (x2, y2) = a, b
        else: (x1, y1), (x2, y2) = (a.x, a.y), (b.x, b.y)
        dx2 = math.pow(x1-x2, 2)
        dy2 = math.pow(y1-y2, 2)
        return math.sqrt(dx2 + dy2)

    def __str__(self):
        return u"<Board: (%d, %d) :: (%s) Moves: %d>" % (self.width, self.height, " vs ".join(self.players), len(self.moves))
    __unicode__ = __str__
