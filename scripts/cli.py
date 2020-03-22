import sys
import os
_project_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(_project_root)

import time

from examples.NFAfromCustomRule import NFAFromRegex, executor, tokenizer
from examples.customRuleDFAToTensor import dfa_to_tensor
from examples.customRuleTokenizer import ruleParser
from src.automata_tools import DFAtoMinimizedDFA, NFAtoDFA, WFA, get_word_to_index, drawGraph, isInstalled

def main():
    rule = "(a(bb|b)c)d"
    nfa = NFAFromRegex().buildNFA(rule)
    print(nfa)
    dfa = NFAtoDFA(nfa)
    minDFA = DFAtoMinimizedDFA(dfa)
    minDFA.setExecuter(executor)
    minDFA.setTokenizer(tokenizer)
    # print(minDFA.execute("aaa bbb"))
    textInput = "a bb c"
    print(minDFA.execute(textInput))
    _, wordToIndex = get_word_to_index([ruleParser(rule), tokenizer(textInput)])
    wfa = WFA(minDFA, wordToIndex, dfa_to_tensor)
    print(wfa.execute(textInput))
    # print("\nNFA: ")
    # nfaObj.displayNFA()
    # print("\nDFA: ")
    # dfaObj.displayDFA()
    # print("\nMinimized DFA: ")
    # dfaObj.displayMinimizedDFA()
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
