import sys
import os
_project_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(_project_root)

import time

from examples.NFAfromCustomRule import NFAfromRegex
from src.DFAFromNFA import DFAFromNFA
from src.BuildAutomata import BuildAutomata
from src.utils import drawGraph, isInstalled


def main():
    input = "$ * what is { 0 , 2 } that $ *"
    if len(sys.argv) > 1:
        input = sys.argv[1]

    print("Regular Expression: ", input)
    nfa = NFAfromRegex().buildNFA(input)
    dfaObj = DFAFromNFA(nfa)
    dfa = dfaObj.getDFA()
    minDFA = dfaObj.getMinimisedDFA()
    print(minDFA.execute("a stands for b what is is that c"))
    # print("\nNFA: ")
    # nfaObj.displayNFA()
    # print("\nDFA: ")
    # dfaObj.displayDFA()
    # print("\nMinimised DFA: ")
    # dfaObj.displayMinimisedDFA()
    if isInstalled("dot"):
        drawGraph(dfa, "dfa")
        drawGraph(nfa, "nfa")
        drawGraph(minDFA, "mdfa")
        # pickle.dump(dfa.to_dict(), open('dfa.pkl', 'wb'))
        # pickle.dump(nfa.to_dict(), open('nfa.pkl', 'wb'))
        # pickle.dump(minDFA.to_dict(), open('mdfa.pkl', 'wb'))
        # print("\nGraphs have been created in the code directory")
        # print(minDFA.getDotFile())


if __name__ == '__main__':
    t = time.time()
    try:
        main()
    except BaseException as e:
        print("\nFailure:", e)
    print("\nExecution time: ", time.time() - t, "seconds")
