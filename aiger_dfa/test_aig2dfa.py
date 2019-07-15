from dfa import DFA

from aiger_dfa import dfa2aig, aig2dfa


def test_dfa2aig():
    dfa1 = DFA(
        start=0,
        inputs={0, 1},
        label=lambda s: (s % 4) == 3,
        transition=lambda s, c: (s + c) % 4,
    )
    circ, relabels = dfa2aig(dfa1)
    dfa2 = aig2dfa(circ, relabels)
    for i in range(5):
        word = (0,)*i
        assert dfa1.label(word) == dfa2.label(word)

        word = (1,)*i
        assert dfa1.label(word) == dfa2.label(word)
