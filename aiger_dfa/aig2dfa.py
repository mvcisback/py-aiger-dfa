from dfa import DFA


def aig2dfa(circ, relabels=None,
            action_str='action',
            output_str='output',
            state_str='state'):
    assert len(circ.inputs) == len(circ.latches) == 1
    assert len(circ.outputs) == 2

    imap, omap = dict(circ.input_map), dict(circ.output_map)
    inputs = range(len(imap[action_str]))
    outputs = range(len(omap[output_str]))

    if relabels is not None:
        inputs = map(relabels['inputs'].get, inputs)
        outputs = map(relabels['outputs'].get, outputs)

    l2init = dict(circ.aig.latch2init)
    start = tuple(l2init[l] for l in dict(circ.latch_map)[state_str])

    def label(s):
        circ_out, _ = circ({action_str: 1}, latches={state_str: s})
        output = circ_out[output_str].index(True)
        return output if relabels is None else relabels['outputs'][output]

    def transition(s, c):
        if relabels is not None:
            c = relabels['inputs'].inv[c]

        # Note: input is 1-hot encoded.
        _, circ_state = circ({action_str: 1 << c}, latches={state_str: s})
        return circ_state[state_str]

    return DFA(
        start=start, inputs=inputs, outputs=outputs,
        label=label, transition=transition,
    )
