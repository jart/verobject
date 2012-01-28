# -*- coding: utf-8 -*-
#
# verobject - version controlled object database on redis
# Copyright (c) 2012 Justine Alexandra Roberts Tunney
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use, copy,
# modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
ur"""

    verobject
    ~~~~~~~~~

    Version controlled object database on Redis.

    I am simple but not space efficient.

    Here's how the happy python api works::

        >>> lolcat = Store('lolcat')
        >>> lolcat.flush()
        >>> lolcat['hk'] = {'hello': 'kitty'}
        >>> lolcat['hk']
        {'hello': 'kitty'}
        >>> lolcat['hk'] = {'hello': 'kitty again'}
        >>> lolcat['hk']
        {'hello': 'kitty again'}
        >>> del lolcat['hk']

    Here's how you access past versions of your object::

        >>> lolcat['hk'] = {'hello': 'kitty'}
        >>> len(lolcat.versions('hk'))
        1
        >>> lolcat['hk'] = {'hello': 'kitty again'}
        >>> len(lolcat.versions('hk'))
        2
        >>> lolcat.versions('hk')[0]
        {'hello': 'kitty again'}
        >>> lolcat.versions('hk')[1]
        {'hello': 'kitty'}
        >>> lolcat.versions('hk')[-1]
        {'hello': 'kitty'}
        >>> list(lolcat.versions('hk'))
        [{'hello': 'kitty again'}, {'hello': 'kitty'}]

    Pickle is used by default to serialize objects::

        >>> import datetime
        >>> lolcat['ts'] = datetime.date(1984, 10, 31)
        >>> lolcat['ts']
        datetime.date(1984, 10, 31)

    You can't access keys that don't exist but you can store None::

        >>> lolcat['blah']
        Traceback (most recent call last):
          ...
        KeyError: 'blah'
        >>> lolcat.get('blah', 'not found')
        'not found'
        >>> lolcat['blah'] = None
        >>> lolcat['blah'] is None
        True
        >>> lolcat.versions('blah')[10]
        Traceback (most recent call last):
          ...
        IndexError: 10

    This is a bad idea::

        >>> lolcat['__keys__'] = 'lolol'
        Traceback (most recent call last):
          ...
        ValueError

    Unicode works::

        >>> lolcat['blah'] = u'✰hello✰'
        >>> print lolcat['blah']
        ✰hello✰

    Time to clean up::

        >>> sorted(list(lolcat))
        ['blah', 'hk', 'ts']
        >>> len(lolcat)
        3
        >>> lolcat.flush()
        >>> len(lolcat)
        0

"""

__version__ = '0.1.4'


class Store(object):
    """Dict-like version controlled immutable serialized object store"""

    def __init__(self, table, redis=None, serializer=None):
        self.table = table
        self.redis = redis
        self.serializer = serializer
        self.keylistkey = table + ".__keys__"
        if not self.redis:
            import redis
            self.redis = redis.StrictRedis()
        if not self.serializer:
            import cPickle
            self.serializer = cPickle

    def __getitem__(self, sid):
        key = "%s.%s" % (self.table, sid)
        res = self.redis.lindex(key, 0)
        if res is None:
            raise KeyError(sid)
        return self.serializer.loads(res)

    def __setitem__(self, sid, obj):
        key = "%s.%s" % (self.table, sid)
        if key == self.keylistkey:
            raise ValueError()
        self.redis.lpush(key, self.serializer.dumps(obj))
        self.redis.sadd(self.keylistkey, sid)

    def __delitem__(self, sid):
        key = "%s.%s" % (self.table, sid)
        if key == self.keylistkey:
            raise ValueError()
        self.redis.delete(key)
        self.redis.srem(self.keylistkey, sid)

    def __len__(self):
        return self.redis.scard(self.keylistkey)

    def __iter__(self):
        return iter(self.redis.smembers(self.keylistkey))

    def get(self, sid, default=None):
        try:
            return self[sid]
        except KeyError:
            return default

    def flush(self):
        for key in self:
            del self[key]
        self.redis.delete(self.keylistkey)

    def versions(self, sid):
        return Versions(self, sid)


class Versions(object):
    """List-like access to past versions of a particular object"""

    def __init__(self, store, sid):
        self.redis = store.redis
        self.serializer = store.serializer
        self.key = "%s.%s" % (store.table, sid)

    def __len__(self):
        return self.redis.llen(self.key)

    def __getitem__(self, n):
        res = self.redis.lindex(self.key, int(n))
        if res is None:
            raise IndexError(n)
        return self.serializer.loads(res)

    def __iter__(self):
        """Iterate versions mindful of new revisions being added"""
        n = 0
        sz = len(self)
        while n < sz:
            sz2 = len(self)
            if sz2 > sz:
                n += sz2 - sz
                sz = sz2
                continue
            assert sz == sz2
            yield self[n]
            n += 1


if __name__ == '__main__':
    import doctest
    doctest.testmod()
