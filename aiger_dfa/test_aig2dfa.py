from dfa import DFA, dict2dfa

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
        assert dfa1.label(word) == dfa2.label(word)

        # Moore encoding of Mealy. Need 1 step delay.
        word = (1,) * i
        assert dfa1.label(word) == dfa2.label(word + (0,))


def test_dfa2aig_default_encoding():
    dfa1 = dict2dfa({
        'foo': (False, {'a': 'foo', 'b': 'bar'}),
        'bar': (True, {'a': 'foo', 'b': 'foo'})
    }, 'foo')
    circ1, *_ = dfa2aig(dfa1)
    dfa2 = aig2dfa(circ1)
    assert len(dfa2.inputs) == 4
    assert len(dfa2.outputs) == 4 + 1  # Moore Encoding.


def test_dfa2aig_smoke():
    dfa1 = dict2dfa({
        'foo': (False, {'a': 'foo', 'b': 'bar'}),
        'bar': (True, {'a': 'foo', 'b': 'foo'})
    }, 'foo')
    circ1, relabels, _ = dfa2aig(dfa1)
    dfa2 = aig2dfa(circ1, relabels)

    assert dfa2.inputs == dfa1.inputs
    assert dfa2.outputs == dfa1.outputs | {None}

    word = ('a', 'b', 'a', 'a', 'b')
    assert dfa1.label(word) == dfa2.label(word)
