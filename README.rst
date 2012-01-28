.. -*-rst-*-

===========
 verobject
===========

:name:        verobject
:description: Version controlled object database on Redis
:copyright:   © 2012 Justine Alexandra Roberts Tunney
:license:     MIT


What Is This?
=============

It's a key value store that keeps copies of past revisions.

Why you should use this
-----------------------

- You've already deployed Redis
- You don't ever want to lose data
- You like pythonic APIs
- You want the KVS to automatically pickle (or jsonify) your data
- You want something simple (140 source lines of code)
- You want something that works (70 lines of test code)

Why you shouldn't use this
--------------------------

- It's space inefficient.  It doesn't compress revision deltas like git does.
- It doesn't support transactions or fancy save methods like zope


Installation
============

From folder::

    sudo python setup.py install

From cheeseshop::

    sudo pip install verobject

From git::

    sudo pip install git+git://github.com/jart/verobject.git


Basic Usage
===========

::

    import datetime, verobject, redis
    redis = redis.Redis()
    table1 = verobject.Store('table1', redis=redis)

    table1['hk'] = {'hello': ['kitty', 'kitty', 'kitty']}
    table1['ts'] = datetime.date(1984, 10, 31)
    print table1['ts'], table1['hk']
    del table1['ts']

    table1['vc'] = 'version1'
    table1['vc'] = 'version2'
    table1['vc'] = 'version3'
    assert list(table1.versions('vc')) == ['version3', 'version2', 'version1']
    assert table1.versions('vc')[0] == 'version3'
    assert table1.versions('vc')[-1] == 'version1'
