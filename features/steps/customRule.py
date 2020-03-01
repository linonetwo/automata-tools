from behave import given, then

from examples.NFAfromCustomRule import NFAFromRegex
from src.DFAFromNFA import DFAFromNFA

@given('the rule "{rule}"')
def getRule(context, rule):
    nfa = NFAFromRegex().buildNFA(rule)
    dfaObj = DFAFromNFA(nfa)
    minDFA = dfaObj.getMinimisedDFA()
    context.minDFA = minDFA

@then('it matches sentence "{text}"')
def matchSentence(context, text):
    assert context.minDFA.execute(text) is True

@then('it won\'t match sentence "{text}"')
def notMatchSentence(context, text):
    assert context.minDFA.execute(text) is not True
