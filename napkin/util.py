import itertools


def neighbour(seq):
    """
    Generate sequence of adjacent items.
    For example, [1, 2] -> (None, 1, 2), (1, 2, None)
    """
    it = iter(seq)
    it_next = itertools.islice(itertools.chain(iter(seq), [None]), 1, None)

    prev = None
    for curr, next in zip(it, it_next):
        yield(prev, curr, next)
        prev = curr
