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

        if self.exists and self.refresh:
            self.fetch()
            self.save()

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

    def delete(self):
        return self.db.delete(self.key)

    @classmethod
    def game_state(cls, game):
        return {0: 'Idle',
                1: 'Waiting'}.get(len(cls.find(game)), "Full")

    @classmethod
    def find(cls, game, **kwargs):
        players_key = cls._set.format(game=game)
        exclude = kwargs.pop('exclude', {})
        def get_known_players():
            try: players = cls._redis.smembers(players_key)
            except TypeError: players = []
            players = [Player(game, player, refresh=False) for player in players]
            return players
        def player_matches_kwargs(player):
            player.fetch()
            return reduce(lambda acc, k_v: acc and (player.info.get(k_v[0]) == k_v[1]),
                          kwargs.items(),
                          True)
        def player_is_excluded(player):
            return exclude and reduce(lambda acc, k_v: acc and (player.info.get(k_v[0]) or getattr(player, k_v[0], None) == k_v[1]),
                                      exclude.items(),
                                      True)

        #Clean the game player set based on expiry
        transaction = cls._redis.pipeline()
        [transaction.srem(players_key, player.uid)
         for player in get_known_players()
         if not player.exists]
        transaction.execute()

        return [player for player in get_known_players() if player_matches_kwargs(player) and not player_is_excluded(player)]


    def __unicode__(self):
        return u'Player: {0}'.format(self.uid)
    __str__ = __unicode__

    def __repr__(self):
        return '<{0}>'.format(self.__unicode__())
