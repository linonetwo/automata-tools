from behave import given, then

from examples.NFAfromCustomRule import NFAFromRegex, executor, tokenizer
from examples.customRuleDFAToTensor import dfa_to_tensor
from examples.customRuleTokenizer import ruleParser
from automata_tools import DFAtoMinimizedDFA, NFAtoDFA, WFA, get_word_to_index

@given('the rule "{rule}"')
def getRule(context, rule):
    nfa = NFAFromRegex().buildNFA(rule)
    minDFA = DFAtoMinimizedDFA(NFAtoDFA(nfa))
    minDFA.setExecuter(executor)
    minDFA.setTokenizer(tokenizer)
    context.minDFA = minDFA
    context.rule = rule

@then('it matches sentence "{text}"')
def matchSentence(context, text):
    assert context.minDFA.execute(text) is True
    # construct a fast WFA
    _, wordToIndex = get_word_to_index([ruleParser(context.rule), tokenizer(text)])
    context.wfa = WFA(context.minDFA, wordToIndex, dfa_to_tensor)
    assert context.wfa.execute(text) is True 

@then('it won\'t match sentence "{text}"')
def notMatchSentence(context, text):
    assert context.minDFA.execute(text) is not True
    # construct a fast WFA
    _, wordToIndex = get_word_to_index([ruleParser(context.rule), tokenizer(text)])
    context.wfa = WFA(context.minDFA, wordToIndex, dfa_to_tensor)
    assert context.wfa.execute(text) is not True 
