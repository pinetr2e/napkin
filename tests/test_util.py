from napkin import util


class TestNeighbour(object):
    def test_empty_item(self):
        it = util.neighbour([])
        assert [] == list(it)

    def test_one_item(self):
        it = util.neighbour([1])
        assert list(it) == [(None, 1, None)]

    def test_two_items(self):
        it = util.neighbour([1, 2])
        assert list(it) == [(None, 1, 2), (1, 2, None)]

    def test_three_items(self):
        it = util.neighbour([1, 2, 3])
        assert list(it) == [(None, 1, 2), (1, 2, 3), (2, 3, None)]
