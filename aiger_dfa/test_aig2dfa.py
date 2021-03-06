from dfa import DFA, dict2dfa
from pyrsistent import pmap

from aiger_dfa import dfa2aig, aig2dfa


def test_dfa2aig():
    dfa1 = DFA(
        start=0,
        inputs={0, 1},
        label=lambda s: (s % 4) == 3,
        transition=lambda s, c: (s + c) % 4,
    )
    circ, relabels, _ = dfa2aig(dfa1)
    dfa2 = aig2dfa(circ, relabels)
    for i in range(1, 5):
        word = (0,)*i
        word2 = (pmap({'action': 0}),)*(i + 1)
        assert dfa1.label(word) == dfa2.label(word2)['output']

        word = (1,)*i
        word2 = (pmap({'action': 1}),)*(i + 1)
        assert dfa1.label(word) == dfa2.label(word2)['output']


def test_dfa2aig_smoke():
    dfa1 = dict2dfa({
        'foo': (False, {'a': 'foo', 'b': 'bar'}),
        'bar': (True, {'a': 'foo', 'b': 'foo'})
    }, 'foo')
    circ1, start, _ = dfa2aig(dfa1)
    dfa2 = aig2dfa(circ1, start)

    test = ('a', 'b', 'a', 'a', 'b')
    test2 = tuple(pmap({'action': x}) for x in test) + (pmap({'action': 'a'}),)
    assert dfa1.label(test) == dfa2.label(test2)['output']
