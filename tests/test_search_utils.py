"""
Testing module for search.utils. Even utils need some testing!
"""
from search import utils
import pytest


class TestUtils:
    def test_normalize(self):
        v = utils.normalize([5, 4, 3, 2.5, 1, 7])
        assert pytest.approx(sum(v)) == 1

    def test_scale_to_one(self):
        values = [6, 4, 3, 2, 8, 9, 4]
        v = utils.scale_to_one(values)
        assert max(v) == 1.0
        assert min(v) > 0
        assert sum(v) == pytest.approx(4)

    def test_weighted_average(self):
        s1, w1 = (1, 2, 3), (3, 2, 1)
        r1 = utils.weighted_average(s1, w1)
        assert r1 == pytest.approx(1.7, abs=1e-1)

        s2, w2 = (1, 2, 3), (1, 2, 3)
        r2 = utils.weighted_average(s2, w2)
        assert r2 == pytest.approx(2.3, abs=1e-1)

    def test_tokenize(self):
        v = utils.tokenize('This is a string, and should be tokenized! 123')
        assert v == ['this', 'string', 'should', 'tokenized']

    def test_max_distance(self):
        l1 = ['a', 'b', 'c', 'd']
        l2 = ['a', 'b', 'c', 'd', 'e']

        assert 2 == utils.max_distance(l1, 1)  # l1.b
        assert 2 == utils.max_distance(l1, 2)  # l1.c
        assert 3 == utils.max_distance(l2, 1)  # l2.b
        assert 4 == utils.max_distance(l2, 4)  # l2.e

    def test_position_similarity(self):
        # FIXME: The function is broken, but for continuity the test remains
        # with all `falsy` results checked.
        q, s = 'pinco'.split(' '), 'guerra pinco pallo'.split(' ')

        assert 1 == utils.position_similarity('pinco', 'guerra', q, s)  # 0,0
        assert 1 == utils.position_similarity('pinco', 'pinco', q, s)   # 0,1

        q = 'pallo pinco'.split(' ')
        assert 1 == utils.position_similarity('pallo', 'guerra', q, s)  # 0,1
        assert 1 == utils.position_similarity('pinco', 'guerra', q, s)  # 1,0
        assert 1 == utils.position_similarity('pinco', 'pinco', q, s)   # 1,1
        assert 1 == utils.position_similarity('pallo', 'guerra', q, s)  # 0,0

        q = 'hello world is it a sunny out there'
        s = 'hello there it is a sunny world'
        q, s = q.split(' '), s.split(' ')

        assert 1 == utils.position_similarity('world', 'there', q, s)  # 1,1
        assert 1 == utils.position_similarity('hello', 'world', q, s)  # 0,6
        assert 1 == utils.position_similarity('there', 'world', q, s)  # 8,1
        assert 1 == utils.position_similarity('it', 'it', q, s)        # 4,3
        assert 1 == utils.position_similarity('hello', 'is', q, s)     # 0,3
