#!/usr/bin/env python
import sys, math

class BoardError(Exception): pass
class HistoryInvalid(BoardError): pass
class DuplicatePosition(BoardError): pass

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


class Position(object):
    def __init__(self, board, x, y, owner, **options):
        self.board, self.x, self.y, self.owner = board, x, y, owner
        self.tag = None
        [setattr(self, key, val) for (key, val) in options]
        self.discover_tag()

    def discover_tag(self):
        return None

class BoardState(object):
    def __init__(self, *players, **options):
        '''
        Call with __init__(list, of players, width=n, height=m...)
        '''
        options = dict({'width': 19,
                        'height': 19,
                        'players': players or ['Black', 'White'],
                        'moves': [],
                        'positions': [],
                        },
                       **options)
        [setattr(self, k, v) for (k, v) in options.items()]
        if not self.validate(): raise HistoryInvalid()

    def validate(self):
        return True

    def dump_board(self, **options):
        marks = options.pop('marks', {})
        def mark_for(x, y):
            for (mark, coord) in marks.items():
                if coord == (x, y): return mark
            return None
        for y in range(self.height - 1, -1, -1):
            for x in range(self.width):
                p = self._get(x, y)
                p = getattr(p, 'owner', mark_for(x, y) or "+")[0]
                print p,
            print
        return True

    def _legal_position(self, x, y):
        return (x <= self.width and
                y <= self.height)

    def _clean_positions(self):
        self.positions = [p for p in set(self.positions) if p.owner != None]

    def _clear(self, x, y):
        def is_cleared_position(p):
            return (p.x, p.y) == (x, y)
        self.positions = [p for p in self.positions if not is_cleared_position(p)]

    def _set(self, x, y, val):
        if val not in [None] + list(self.players): return False
        self._clear(x, y)
        if val != None: self.positions.append(Position(self, x, y, val))
        self._clean_positions()
        return True

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
        return (x < self.width) and (y < self.height)

    def is_chain(self, start, finish):
        '''
        Determines if there is a path of same state from point a(x, y) to point b(x, y)
        '''
        import heapq
        #Queue stores the to-visit list as (x, y, distance)
        heap = []
        found = False

        def add_neighbors_of(node):
            '''Add weighted neighbors of node to the queue'''
            v = self._get(node.x, node.y)
            def neighbors_of_same_state(p):
                maybe = [(p.x - 1, p.y),
                         (p.x + 1, p.y),
                         (p.x, p.y - 1),
                         (p.x, p.y + 1)]
                v = getattr(self._get(p.x, p.y), 'owner', None)
                return [TargettedPoint(*loc + (finish,)) for loc in maybe if self.position_exists(*loc) and
                        getattr(self._get(*loc), 'owner', None) == v]

            for neighbor in neighbors_of_same_state(node):
                heapq.heappush(heap, neighbor)

        searching = True
        heapq.heappush(heap, TargettedPoint(start[0], start[1], finish))
        while searching:
            visit = heapq.heappop(heap)
            #print "Visiting:", visit
            #self.dump_board(marks={'S': start, 'F': finish, 'V': (visit.x, visit.y)})
            found = int(visit.distance) == 0
            if found: break
            add_neighbors_of(visit)
            if not len(heap): searching = False

        return found

    def _distance(self, a, b):
        if type(a) == tuple and type(b) == tuple: (x1, y1), (x2, y2) = a, b
        else: (x1, y1), (x2, y2) = (a.x, a.y), (b.x, b.y)
        dx2 = math.pow(x1-x2, 2)
        dy2 = math.pow(y1-y2, 2)
        return math.sqrt(dx2 + dy2)

    def __str__(self):
        return u"<Board: (%d, %d) :: (%s) Moves: %d>" % (self.width, self.height, " vs ".join(self.players), len(self.moves))
    __unicode__ = __str__
