from automata_tools.Automata import Automata


def NFAtoDFA(nfa: Automata) -> Automata:
    allstates = dict()
    eclose = dict()
    count = 1
    state1 = nfa.getEClosure(nfa.startstate)
    eclose[nfa.startstate] = state1
    dfa = Automata(nfa.language)
    dfa.setstartstate(count)
    states = [[state1, count]]
    allstates[count] = state1
    count += 1
    while len(states) != 0:
        [state, fromindex] = states.pop()
        for char in sorted(dfa.language):
            trstates = nfa.getReachableStates(state, char)
            for s in list(trstates)[:]:
                if s not in eclose:
                    eclose[s] = nfa.getEClosure(s)
                trstates = trstates.union(eclose[s])
            if len(trstates) != 0:
                if trstates not in allstates.values():
                    states.append([trstates, count])
                    allstates[count] = trstates
                    toindex = count
                    count += 1
                else:
                    toindex = [
                        k for k, v in sorted(allstates.items()) if v == trstates
                    ][0]
                dfa.addtransition(fromindex, toindex, char)
    for value, state in sorted(allstates.items()):
        if nfa.finalstates[0] in state:
            dfa.addfinalstates(value)
    return dfa
