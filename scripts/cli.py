import sys
import os
_project_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(_project_root)

import time

from examples.NFAfromCustomRule import NFAFromRegex, executor, tokenizer
from examples.customRuleDFAToTensor import dfa_to_tensor
from examples.customRuleTokenizer import ruleParser
from src.automata_tools import DFAtoMinimizedDFA, NFAtoDFA, NFAtoDFAGroupStable, WFA, get_word_to_index, drawGraph, isInstalled

def main():
    rule = "a+(bb|b)c d{0, 3} $*"
    textInput = "a bb c"
    nfa = NFAFromRegex().buildNFA(rule)
    # print(nfa.splitNFA([nfa.groups[0].startState, nfa.groups[0].finalState])[0])
    # drawGraph(NFAtoDFA(nfa.splitNFA([nfa.groups[0].startState, nfa.groups[0].finalState])[0]), "splitdfa")
    minDFA = NFAtoDFAGroupStable(nfa)
    minDFA.setExecuter(executor)
    minDFA.setTokenizer(tokenizer)
    if isInstalled("dot"):
        # drawGraph(dfa, "dfa")
        drawGraph(nfa, "nfa")
        drawGraph(minDFA, "mdfa")
    print(minDFA.execute(textInput))
    _, wordToIndex = get_word_to_index([ruleParser(rule), tokenizer(textInput)])
    wfa = WFA(minDFA, wordToIndex, dfa_to_tensor)
    print(wfa.execute(textInput))


if __name__ == '__main__':
    t = time.time()
    try:
        main()
    except BaseException as e:
        print("\nFailure:", e)
    print("\nExecution time: ", time.time() - t, "seconds")
