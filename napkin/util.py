import itertools


def neighbour(seq):
    it = iter(seq)
    it_next = itertools.chain(seq, [None])
    it_next.next()

    prev = None
    for curr, next in itertools.izip(it, it_next):
        yield(prev, curr, next)
        prev = curr
