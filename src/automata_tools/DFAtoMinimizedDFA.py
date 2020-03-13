from automata_tools.Automata import Automata

TWO_STATE_GIVEN_THIS_TOKEN_CAN_REACH_SAME_STATE = 1


def DFAtoMinimizedDFA(dfa: Automata) -> Automata:
    dfaStates = list(dfa.states)
    dfaStateLength = len(dfaStates)
    uncheckedState = dict()
    count = 1
    distinguished = []
    # {0: {1}, 1: {2}, 2: {3}, 3: {4}, 4: {5}, 5: {6}, 6: {7}, 7: {8}} at the outset
    # {0: {1, 2}, 2: {8, 3, 4, 6}, 4: {5, 7}} at the end
    equivalentStates = dict(
        zip(range(dfaStateLength), [{s} for s in dfaStates]))
    # partitionOfStates is
    # {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7} at the outset
    # {1: 0, 2: 1, 3: 1, 4: 0, 5: 1, 6: 5, 7: 5, 8: 1} at the end
    partitionOfStates = dict(zip(dfaStates, range(dfaStateLength)))
    for i in range(dfaStateLength - 1):
        for j in range(i + 1, dfaStateLength):
            if not ([dfaStates[i], dfaStates[j]] in distinguished
                    or [dfaStates[j], dfaStates[i]] in distinguished):
                iIsFinalButJisNot = (dfaStates[i] in dfa.finalstates
                                     and dfaStates[j] not in dfa.finalstates)
                jIsFinalButIisNot = (dfaStates[i] not in dfa.finalstates
                                     and dfaStates[j] in dfa.finalstates)
                if iIsFinalButJisNot or jIsFinalButIisNot:
                    distinguished.append([dfaStates[i], dfaStates[j]])
                    continue
                eq = TWO_STATE_GIVEN_THIS_TOKEN_CAN_REACH_SAME_STATE
                toAppend = []
                for token in dfa.language:
                    reachableStatesI = dfa.getReachableStates(
                        dfaStates[i], token)
                    reachableStatesJ = dfa.getReachableStates(
                        dfaStates[j], token)
                    if len(reachableStatesI) != len(reachableStatesJ):
                        eq = 0
                        break
                    if len(reachableStatesI) > 1:
                        raise BaseException(
                            f"Multiple transitions on same token {token} detected in DFA"
                        )
                    elif len(reachableStatesI) == 0:
                        continue
                    reachStateI = reachableStatesI.pop()
                    reachStateJ = reachableStatesJ.pop()
                    if reachStateI != reachStateJ:
                        if [reachStateI, reachStateJ] in distinguished or [
                                reachStateJ, reachStateI
                        ] in distinguished:
                            eq = 0
                            break
                        else:
                            toAppend.append([reachStateI, reachStateJ, token])
                            eq = -1
                if eq == 0:
                    distinguished.append([dfaStates[i], dfaStates[j]])
                elif eq == -1:
                    s = [dfaStates[i], dfaStates[j]]
                    s.extend(toAppend)
                    uncheckedState[count] = s
                    count += 1
                elif eq == TWO_STATE_GIVEN_THIS_TOKEN_CAN_REACH_SAME_STATE:
                    partitionI = partitionOfStates[dfaStates[i]]
                    partitionJ = partitionOfStates[dfaStates[j]]
                    if partitionI != partitionJ:
                        st = equivalentStates.pop(partitionJ)
                        for s in st:
                            partitionOfStates[s] = partitionI
                        equivalentStates[partitionI] = equivalentStates[
                            partitionI].union(st)
    newFound = True
    # uncheckedState is
    # {1: [2, 3, [8, 6, '$']], 2: [2, 6, [8, 6, '$']], 3: [3, 8, [6, 8, '$']], 4: [6, 8, [6, 8, '$']]}
    while newFound and len(uncheckedState) > 0:
        newFound = False
        for p, pair in uncheckedState.copy().items():
            for transition in pair[2:]:
                if [transition[0], transition[1]] in distinguished or [
                        transition[1], transition[0]
                ] in distinguished:
                    uncheckedState.pop(p)
                    distinguished.append([pair[0], pair[1]])
                    newFound = True
                    break
    for pair in uncheckedState.values():
        partitionI = partitionOfStates[pair[0]]
        partitionJ = partitionOfStates[pair[1]]
        if partitionI != partitionJ:
            st = equivalentStates.pop(partitionJ)
            for s in st:
                partitionOfStates[s] = partitionI
            equivalentStates[partitionI] = equivalentStates[partitionI].union(
                st)
    if len(equivalentStates) == dfaStateLength:
        minDFA = dfa
    else:
        minDFA = dfa.newBuildFromEquivalentStates(equivalentStates,
                                                  partitionOfStates)
    return minDFA
