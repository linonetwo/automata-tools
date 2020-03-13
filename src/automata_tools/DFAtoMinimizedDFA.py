from automata_tools.Automata import Automata

def DFAtoMinimizedDFA(dfa: Automata) -> Automata:
    states = list(dfa.states)
    n = len(states)
    unchecked = dict()
    count = 1
    distinguished = []
    equivalent = dict(zip(range(len(states)), [{s} for s in states]))
    pos = dict(zip(states, range(len(states))))
    for i in range(n - 1):
        for j in range(i + 1, n):
            if not ([states[i], states[j]] in distinguished
                    or [states[j], states[i]] in distinguished):
                eq = 1
                toappend = []
                for char in dfa.language:
                    s1 = dfa.gettransitions(states[i], char)
                    s2 = dfa.gettransitions(states[j], char)
                    if len(s1) != len(s2):
                        eq = 0
                        break
                    if len(s1) > 1:
                        raise BaseException(
                            "Multiple transitions detected in DFA")
                    elif len(s1) == 0:
                        continue
                    s1 = s1.pop()
                    s2 = s2.pop()
                    if s1 != s2:
                        if [s1, s2] in distinguished or [
                                s2, s1
                        ] in distinguished:
                            eq = 0
                            break
                        else:
                            toappend.append([s1, s2, char])
                            eq = -1
                if eq == 0:
                    distinguished.append([states[i], states[j]])
                elif eq == -1:
                    s = [states[i], states[j]]
                    s.extend(toappend)
                    unchecked[count] = s
                    count += 1
                else:
                    p1 = pos[states[i]]
                    p2 = pos[states[j]]
                    if p1 != p2:
                        st = equivalent.pop(p2)
                        for s in st:
                            pos[s] = p1
                        equivalent[p1] = equivalent[p1].union(st)
    newFound = True
    while newFound and len(unchecked) > 0:
        newFound = False
        toremove = set()
        for p, pair in unchecked.copy().items():
            for tr in pair[2:]:
                if [tr[0], tr[1]] in distinguished or [tr[1], tr[0]
                                                        ] in distinguished:
                    unchecked.pop(p)
                    distinguished.append([pair[0], pair[1]])
                    newFound = True
                    break
    for pair in unchecked.values():
        p1 = pos[pair[0]]
        p2 = pos[pair[1]]
        if p1 != p2:
            st = equivalent.pop(p2)
            for s in st:
                pos[s] = p1
            equivalent[p1] = equivalent[p1].union(st)
    if len(equivalent) == len(states):
        minDFA = dfa
    else:
        minDFA = dfa.newBuildFromEquivalentStates(
            equivalent, pos)
    return minDFA
