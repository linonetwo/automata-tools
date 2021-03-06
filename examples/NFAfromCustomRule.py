import sys
import os
_project_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.join(_project_root, 'src'))
sys.path.append(os.path.join(_project_root, 'examples'))

from typing import Optional, List, Tuple, Dict, Set, cast, Union
import re

from src.automata_tools import BuildAutomata, Automata
from customRuleTokenizer import ruleParser

punctuations = [
    ',', '，', ':', '：', '!', '！', '《', '》', '。', '；', '.', '(', ')', '（', '）',
    '|', '?', '"'
]


def padPunctuations(shortString: str):
    for punctuation in punctuations:
        shortString = re.sub(f'[{punctuation}]', f' {punctuation} ',
                             shortString)
    return shortString


def tokenizer(input: str):
    inputWithPunctuationsPaddedWithSpace = padPunctuations(input)
    tokens = inputWithPunctuationsPaddedWithSpace.split(' ')
    return [item for item in tokens if item]


IAvailableTransitions = Dict[int, Set[str]]

SymbolWord = 'SymbolWord'
SymbolNumeric = 'SymbolNumeric'
SymbolPunctuation = 'SymbolPunctuation'
SymbolWildcard = 'SymbolWildcard'


def matchTokenInSet(token: Optional[str], acceptTokens: Set[str]):
    if token == None:
        return None
    if token in acceptTokens:
        return SymbolWord
    elif '%' in acceptTokens and token.replace('.', '', 1).isdigit():
        return SymbolNumeric
    elif '&' in acceptTokens and token in punctuations:
        return SymbolPunctuation
    elif '$' in acceptTokens and not token.replace('.', '', 1).isdigit() and token not in punctuations:
        return SymbolWildcard
    return None


def tryConsumeNonWildCard(availableTransitions: IAvailableTransitions,
                          currentToken: Optional[str], currentTokens: List[str]
                          ) -> Optional[Tuple[int, Optional[str], List[str]]]:
    # search available transition in the first pass
    for nextState, pathSet in availableTransitions.items():
        if matchTokenInSet(currentToken, pathSet) == SymbolWord:
            nextToken = currentTokens.pop(0) if len(currentTokens) > 0 else None
            return (nextState, nextToken, currentTokens)
    return None


def tryConsumeWildCard(availableTransitions: IAvailableTransitions,
                       currentToken: Optional[str], currentTokens: List[str]
                       ) -> Optional[Tuple[int, Optional[str], List[str]]]:
    # non-greedy wild card, we only use it when there is no other choice
    for nextState, pathSet in availableTransitions.items():
        if matchTokenInSet(currentToken, pathSet) == SymbolNumeric:
            nextToken = currentTokens.pop(0) if len(currentTokens) > 0 else None
            return (nextState, nextToken, currentTokens)
        elif matchTokenInSet(currentToken, pathSet) == SymbolPunctuation:
            nextToken = currentTokens.pop(0) if len(currentTokens) > 0 else None
            return (nextState, nextToken, currentTokens)
        elif matchTokenInSet(currentToken, pathSet) == SymbolWildcard:
            nextToken = currentTokens.pop(0) if len(currentTokens) > 0 else None
            return (nextState, nextToken, currentTokens)
    return None


def executor(tokens, startState, finalStates,
             transitions: Dict[int, IAvailableTransitions]):
    currentState: int = startState
    currentToken: Optional[str] = tokens.pop(0)
    while currentState not in finalStates:
        availableTransitions = transitions[currentState]
        # count if we have ambiguous situation, since wildcard can make DFA sometimes actually a NFA
        availablePathCount = 0
        for _, pathSet in availableTransitions.items():
            if matchTokenInSet(currentToken, pathSet):
                availablePathCount += 1
        # try consume a non wildcard matcher in rule first
        matchingResult = tryConsumeNonWildCard(transitions[currentState],
                                               currentToken, tokens)
        if matchingResult and matchingResult[0] in finalStates:
            return True

        if availablePathCount > 1 and matchingResult != None:
            # it is ambiguous now
            # try go on, and see if consume a non wildcard matcher is a right choice
            # (currentState, currentToken, tokens) = matchingResult
            if matchingResult[1] == None:
                return False
            initialStateToTry = matchingResult[0]
            tokensToTry = [cast(str, matchingResult[1])] + matchingResult[2]
            if executor(tokensToTry, initialStateToTry, finalStates,
                        transitions):
                return True
            else:
                matchingResult = None
        if matchingResult == None:
            matchingResult = tryConsumeWildCard(transitions[currentState],
                                                currentToken, tokens)
            if matchingResult == None:
                return False  # sadly, no available transition for current token
        (currentState, currentToken, tokens) = matchingResult
    return True


class NFAFromDSL:
    """
    class for building e-nfa from regular expressions
    """

    #: 存放 + * 等特殊符号的栈
    operatorStack: List[Union[str, Dict[str, str]]] = [] # ['(', { type: '<', payload: 'label' }]
    #: 存放子自动机的栈
    automataStack: List[Automata] = []

    starOperator = '*'
    plusOperator = '+'
    questionOperator = '?'
    concatOperator = 'Symbol("concat")'
    orOperator = '|'
    initOperator = '::e::'
    openingBracket = '('
    closingBracket = ')'
    openingBrace = '{'
    closingBrace = '}'
    openingAngleBracket = '<'
    closingAngleBracket = '>'

    binaryOperators = [orOperator, concatOperator]
    unaryOperators = [starOperator, plusOperator, questionOperator]
    openingBrackets = [openingBracket, openingBrace]
    closingBrackets = [closingBracket, closingBrace]
    angleBrackets = [openingAngleBracket, closingAngleBracket]
    allOperators = [
        initOperator
    ] + binaryOperators + unaryOperators + openingBrackets + closingBrackets + angleBrackets

    def __init__(self):
        pass

    @staticmethod
    def displayNFA(nfa: Automata):
        nfa.display()

    def buildNFA(self, rule: str) -> Automata:
        language = set()
        self.operatorStack = []
        self.automataStack = []
        previous = self.initOperator
        ruleTokens = ruleParser(rule)
        index = 0
        while index < len(ruleTokens):
            token = ruleTokens[index]
            if token not in self.allOperators:
                language.add(token)
                # if previous automata is standalong (char or a group or so), we concat current automata with previous one
                if ((previous not in self.allOperators)
                        or previous in [self.closingBracket] +
                        self.unaryOperators): # previous is regular token or is not in (self.allOperators - ([self.closingBracket] + self.unaryOperators))
                    self.addOperatorToStack(self.concatOperator)
                self.automataStack.append(BuildAutomata.characterStruct(token))
            elif token == self.closingAngleBracket: # (?<label> xxx )
                # to handle ( ? < label > , we get "label"
                captureGroupLabel = ruleTokens[index - 1]
                # add { type: '<', payload: [label] } to the stack, and process it when we reach ")"
                self.addOperatorToStack({ 'type': self.openingAngleBracket, 'payload': captureGroupLabel })
                index += 1
                continue
            elif token == self.openingBracket: # "("
                # concat current automata with previous one, same as above
                if ((previous not in self.allOperators)
                        or previous in [self.closingBracket] +
                        self.unaryOperators):
                    self.addOperatorToStack(self.concatOperator)
                self.operatorStack.append(token)
                if ruleTokens[index + 1] == self.questionOperator and ruleTokens[index + 2] == self.openingAngleBracket and ruleTokens[index + 4] == self.closingAngleBracket: # (?<label> xxx )
                    # to handle ( ? < label > , we jump to ">"
                    index += 4
                    previous = token
                    continue
            elif token == self.closingBracket: # ")"
                if previous in self.binaryOperators:
                    raise BaseException(
                        f"Error processing {token} after {previous}")
                while (1): # grouping all child-automata in the stack into a big child-automata, which represents the group
                    if len(self.operatorStack) == 0:
                        raise BaseException(
                            f"Error processing {token}. Empty stack")
                    operatorWithinGroup = self.operatorStack.pop()
                    # basically, operatorWithinGroup will only be binaryOperators or "("
                    if operatorWithinGroup in self.binaryOperators:
                        self.processOperator(operatorWithinGroup)
                    elif type(operatorWithinGroup) == dict:
                        operatorWithinGroup = cast(Dict[str, str], operatorWithinGroup)
                        if operatorWithinGroup['type'] == self.openingAngleBracket:
                            self.automataStack[-1].setAsGroup(operatorWithinGroup['payload'])
                    elif operatorWithinGroup == self.openingBracket:
                        break # this means we have process all the operators inside this group, maybe not outer group 1 in "(1(2))", but that will be deal with when we come to next ")"
            elif token == self.openingBrace:
                # to handle { 0 , 2 } , we jump to "}"
                index += 4
                continue
            elif token == self.closingBrace:
                # to handle { 0 , 2 } , we get "0" and "2"
                repeatRangeStart = ruleTokens[index - 3]
                repeatRangeEnd = ruleTokens[index - 1]
                payload = (repeatRangeStart, repeatRangeEnd)
                self.processOperator(self.closingBrace, payload)
                index += 1
                continue
            elif token in self.unaryOperators:
                if previous in self.binaryOperators + self.openingBrackets + self.unaryOperators:
                    raise BaseException(
                        f"Error processing {token} after {previous}")
                self.processOperator(token)
            elif token in self.binaryOperators:
                if previous in self.binaryOperators or previous == self.openingBracket:
                    raise BaseException(
                        f"Error processing {token} after {previous}")
                self.addOperatorToStack(token)
            else:
                raise BaseException(f"Symbol {token} is not allowed")
            previous = token
            index += 1
        while len(self.operatorStack) != 0:
            op = self.operatorStack.pop()
            self.processOperator(op)
        if len(self.automataStack) > 1:
            print(self.automataStack)
            raise BaseException("Regex could not be parsed successfully")
        nfa = self.automataStack.pop()
        nfa.language = language
        return nfa

    def addOperatorToStack(self, char: Union[str, Dict[str, str]]):
        while (1):
            if len(self.operatorStack) == 0:
                break
            top = self.operatorStack[len(self.operatorStack) - 1]
            if top == self.openingBracket:
                break
            if top == char or top == self.concatOperator:
                op = self.operatorStack.pop()
                self.processOperator(op)
            else:
                break
        self.operatorStack.append(char)

    def processOperator(self,
                        operator,
                        payload: Optional[Tuple[str, str]] = None):
        if len(self.automataStack) == 0:
            raise BaseException(
                f"Error processing operator {operator}. Stack is empty")
        if operator == self.starOperator:
            a = self.automataStack.pop()
            self.automataStack.append(BuildAutomata.starStruct(a))
        elif operator == self.questionOperator:
            a = self.automataStack.pop()
            self.automataStack.append(BuildAutomata.skipStruct(a))
        elif operator == self.plusOperator:
            a = self.automataStack.pop()
            moreA = BuildAutomata.starStruct(a)
            self.automataStack.append(BuildAutomata.concatenationStruct(a, moreA))
        elif operator == self.closingBrace: # '}'
            if payload == None:
                raise BaseException(
                    f"Error processing operator {operator}. payload is None")
            repeatRangeStart, repeatRangeEnd = payload
            automataToRepeat = self.automataStack.pop()
            repeatedAutomata = BuildAutomata.repeatRangeStruct(
                automataToRepeat, int(repeatRangeStart), int(repeatRangeEnd))
            self.automataStack.append(repeatedAutomata)
        elif operator in self.binaryOperators:
            if len(self.automataStack) < 2:
                raise BaseException(
                    f"Error processing operator {operator}. Inadequate operands"
                )
            a = self.automataStack.pop()
            b = self.automataStack.pop()
            if operator == self.orOperator:
                self.automataStack.append(BuildAutomata.unionStruct(b, a))
            elif operator == self.concatOperator:
                self.automataStack.append(BuildAutomata.concatenationStruct(b, a))
