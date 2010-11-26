import uuid
import redis

REDIS_OPTS = dict(host='localhost', port=6379, db=0)
class Player(object):
    _redis = redis.Redis(**REDIS_OPTS)
    _key = 'gogogo:player:{id}'
    _set = 'gogogo:game:{game}:players'
    _ttl = 60

    def __init__(self, game, uid=None, **options):
        self.db = self.__class__._redis
        self.uid = uid or uuid.uuid4().hex
        self.key = self._key.format(id=self.uid)
        self.ttl = self._ttl
        self.info = {}
        self.game = game
        self.refresh = True
        self.set_key = self._set.format(game=game)

        #Options override
        [setattr(self, key, value) for key, value in options.items()]

        print "Looking up:", self.key
        if self.exists and self.refresh:
            self.fetch()
            self.save()
        print "Info:", self.info

    def fetch(self):
        self.info = self.db.hgetall(self.key)
        return self

    def update(self, **data):
        self.info = dict(self.info, **data)
        return self.save()

    @property
    def exists(self):
        return self.db.exists(self.key)

    def save(self):
        transaction = self.db.pipeline()
        transaction.hmset(self.key, self.info)
        transaction.expire(self.key, self.ttl)
        transaction.sadd(self.set_key, self.uid)
        res = transaction.execute()
        if len([i for i in res if isinstance(i, redis.ResponseError)]):
            return None
        return self

    @classmethod
    def find(cls, game, **kwargs):
        players_key = cls._set.format(game=game)
        def get_known_players():
            players = cls._redis.smembers(players_key)
            players = [Player(game, player, refresh=False) for player in players]
            return players
        def player_matches_kwargs(player):
            player.fetch()
            print "Testing:", player.info, "vs", kwargs
            return reduce(lambda acc, k_v: acc and (player.info.get(k_v[0]) == k_v[1]),
                          kwargs.items(),
                          True)

        #Clean the game player set based on expiry
        transaction = cls._redis.pipeline()
        [transaction.srem(players_key, player.uid)
         for player in get_known_players()
         if not player.exists]
        transaction.execute()

        return [player for player in get_known_players() if player_matches_kwargs(player)]


    def __unicode__(self):
        return u'Player: {0}'.format(self.uid)
    __str__ = __unicode__

    def __repr__(self):
        return '<{0}>'.format(self.__unicode__())
