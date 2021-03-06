from typing import Dict, Set, List, Tuple
from math import floor

from automata_tools.Automata import Automata, GroupMetadata
from automata_tools.BuildAutomata import BuildAutomata
from automata_tools.DFAtoMinimizedDFA import DFAtoMinimizedDFA
from automata_tools.utils import drawGraph


def NFAtoDFA(nfa: Automata, minify: bool = True) -> Automata:
    stateTranslator: Dict[Set[int]] = dict() # from new state to old states, 1 to many { 1: {1}, 2: {2, 3, 4, 6}, 3: {8, 9, 7}, 4: {8, 9, 5}, 5: {10, 11}, 6: {12} }
    eClosure = dict()
    newStateCounter = 1
    state1 = nfa.getEClosure(nfa.startstate)
    eClosure[nfa.startstate] = state1
    dfa = Automata(nfa.language)
    dfa.setStartState(newStateCounter)
    states = [[state1, newStateCounter]]
    stateTranslator[newStateCounter] = state1
    newStateCounter += 1
    while len(states) != 0:
        [state, fromindex] = states.pop()
        for char in sorted(dfa.language):
            reachableStates = nfa.getReachableStates(state, char)
            for reachableState in list(reachableStates)[:]:
                if reachableState not in eClosure:
                    eClosure[reachableState] = nfa.getEClosure(reachableState)
                reachableStates = reachableStates.union(eClosure[reachableState])
            if len(reachableStates) != 0:
                if reachableStates not in stateTranslator.values():
                    states.append([reachableStates, newStateCounter])
                    stateTranslator[newStateCounter] = reachableStates
                    toIndex = newStateCounter
                    newStateCounter += 1
                else:
                    toIndex = [
                        k for k, v in sorted(stateTranslator.items()) if v == reachableStates
                    ][0]
                dfa.addTransition(fromindex, toIndex, char)
    for dfaState, correspondingNfaStates in sorted(stateTranslator.items()):
        for finalState in nfa.finalStates:
            if finalState in correspondingNfaStates:
                dfa.addfinalStates(dfaState)
    return DFAtoMinimizedDFA(dfa) if minify else dfa

def NFAtoDFAGroupStable(nfa: Automata) -> Automata:
    """
    While transform NFA to DFA, it will try to keep group stable, won't mix the state within them with the states outside the group. So you can know when this DFA automata is catching a group.

    They basically have same state count, just need a bit more time to construct.
    """
    if len(nfa.groups) == 0:
        return NFAtoDFA(nfa)
    splitNFAAutomata: List[Automata] = nfa.splitNFA([nfa.groups[0].startState, nfa.groups[0].finalState])
    concatenatedDFA = NFAtoDFA(splitNFAAutomata[0])
    for index, automataToConcat in enumerate(splitNFAAutomata):
        if index >= 1:
            currentGroup = nfa.groups[floor((index - 1) / 2)]
            startEndDescriptor = 'End' if (index + 1) % 2 else 'Start'
            edgeName = f'Capture{startEndDescriptor}-{currentGroup.groupName}'
            subDFA = NFAtoDFA(automataToConcat)
            concatenatedDFA = BuildAutomata.concatenationStruct(concatenatedDFA, subDFA, edgeName)
    # restore group metadata
    newGroups: List[GroupMetadata] = []
    for groupIndex, group in enumerate(nfa.groups):
        # when doing last NFAtoDFA(), we remove 1 ε before each group, and 1 ε after each group
        offsetOfGroupStart = groupIndex * 2
        offsetOfGroupEnd = offsetOfGroupStart + 1

    return concatenatedDFA