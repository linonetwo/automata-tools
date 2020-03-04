import sys
import os
_project_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.join(_project_root, 'src'))

from typing import Optional, List, Tuple
import re

from automata_tools import BuildAutomata, Automata


punctuations = [',','，',':','：','!','！','《','》','。','；','.','(',')','（','）','|']
def padPunctuations(shortString: str):
    for punctuation in punctuations:
        shortString = re.sub(f'[{punctuation}]', f' {punctuation} ', shortString)
    return shortString
def tokenizer(input: str):
    inputWithPunctuationsPaddedWithSpace = padPunctuations(input)
    tokens = inputWithPunctuationsPaddedWithSpace.split(' ')[::-1]
    return [item for item in tokens if item]
def executor(tokens, startState, finalStates, transitions):
    currentState: int = startState
    currentToken: Optional[str] = tokens.pop()
    while currentState not in finalStates:
        availableTransitions = transitions[currentState]
        # search available transition in the first pass
        for nextState, pathSet in availableTransitions.items():
            if currentToken in pathSet:
                currentState = nextState
                currentToken = tokens.pop() if len(tokens) > 0 else None
                break
        else:
            # non-greedy wild card, we only use it when there is no other choice
            availableTransitions = transitions[currentState]
            for nextState, pathSet in availableTransitions.items():
                if '%' in pathSet and currentToken.isnumeric():
                    currentState = nextState
                    currentToken = tokens.pop() if len(tokens) > 0 else None
                    break
                elif '&' in pathSet and currentToken in punctuations:
                    currentState = nextState
                    currentToken = tokens.pop() if len(tokens) > 0 else None
                    break
                elif '$' in pathSet and not currentToken.isnumeric() and currentToken not in punctuations and currentToken != None:
                    currentState = nextState
                    currentToken = tokens.pop() if len(tokens) > 0 else None
                    break
            else:
                return False  # sadly, no available transition for current token
    return True


class NFAFromRegex:
    """
    class for building e-nfa from regular expressions
    """

    #: 存放 + * 等特殊符号的栈
    stack: List[str] = []
    #: 存放子自动机的栈
    automata: List[Automata] = []

    starOperator = '*'
    plusOperator = '+'
    concatOperator = '.'
    orOperator = '|'
    initOperator = '::e::'
    openingBracket = '('
    closingBracket = ')'
    openingBrace = '{'
    closingBrace = '}'

    binaryOperators = [orOperator, concatOperator]
    unaryOperators = [starOperator, plusOperator]
    openingBrackets = [
        openingBracket, openingBrace
    ]
    closingBrackets = [
        closingBracket, closingBrace
    ]
    allOperators = [initOperator
                    ] + binaryOperators + unaryOperators + openingBrackets + closingBrackets

    def __init__(self):
        pass

    @staticmethod
    def displayNFA(nfa: Automata):
        nfa.display()

    def buildNFA(self, regex: str):
        language = set()
        self.stack = []
        self.automata = []
        previous = self.initOperator
        tokens = regex.split()
        index = 0
        while index < len(tokens):
            token = tokens[index]
            if token not in self.allOperators:
                language.add(token)
                # if previous automata is standalong (char or a group or so), we concat current automata with previous one
                if ((previous not in self.allOperators) or
                        previous in [self.closingBracket] + self.unaryOperators):
                    self.addOperatorToStack(self.concatOperator)
                self.automata.append(BuildAutomata.characterStruct(token))
            elif token == self.openingBracket:
                # concat current automata with previous one, same as above
                if ((previous not in self.allOperators) or
                        previous in [self.closingBracket] + self.unaryOperators):
                    self.addOperatorToStack(self.concatOperator)
                self.stack.append(token)
            elif token == self.closingBracket:
                if previous in self.binaryOperators:
                    raise BaseException(
                        f"Error processing {token} after {previous}")
                while (1):
                    if len(self.stack) == 0:
                        raise BaseException(
                            f"Error processing {token}. Empty stack")
                    o = self.stack.pop()
                    if o == self.openingBracket:
                        break
                    elif o in self.binaryOperators:
                        self.processOperator(o)
            elif token == self.openingBrace:
                # to handle { 0 , 2 } , we jump to "}"
                index += 4
                continue
            elif token == self.closingBrace:
                # to handle { 0 , 2 } , we get "0" and "2"
                repeatRangeStart = tokens[index - 3]
                repeatRangeEnd = tokens[index - 1]
                payload = (repeatRangeStart, repeatRangeEnd)
                self.processOperator(self.closingBrace, payload)
                index += 1
                continue
            elif token == self.starOperator:
                if previous in self.binaryOperators + self.openingBrackets + self.unaryOperators:
                    raise BaseException(
                        f"Error processing {token} after {previous}")
                self.processOperator(token)
            elif token == self.plusOperator:
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
        while len(self.stack) != 0:
            op = self.stack.pop()
            self.processOperator(op)
        if len(self.automata) > 1:
            print(self.automata)
            raise BaseException("Regex could not be parsed successfully")
        nfa = self.automata.pop()
        nfa.language = language
        return nfa

    def addOperatorToStack(self, char: str):
        while (1):
            if len(self.stack) == 0:
                break
            top = self.stack[len(self.stack) - 1]
            if top == self.openingBracket:
                break
            if top == char or top == self.concatOperator:
                op = self.stack.pop()
                self.processOperator(op)
            else:
                break
        self.stack.append(char)

    def processOperator(self,
                        operator,
                        payload: Optional[Tuple[str, str]] = None):
        if len(self.automata) == 0:
            raise BaseException(
                f"Error processing operator {operator}. Stack is empty")
        if operator == self.starOperator:
            a = self.automata.pop()
            self.automata.append(BuildAutomata.starStruct(a))
        elif operator == self.plusOperator:
            a = self.automata.pop()
            moreA = BuildAutomata.starStruct(a)
            self.automata.append(BuildAutomata.concatenationStruct(a, moreA))
        elif operator == self.closingBrace:
            if payload == None:
                raise BaseException(
                    f"Error processing operator {operator}. payload is None")
            repeatRangeStart, repeatRangeEnd = payload
            automataToRepeat = self.automata.pop()
            repeatedAutomata = BuildAutomata.repeatRangeStruct(
                automataToRepeat, int(repeatRangeStart), int(repeatRangeEnd))
            self.automata.append(repeatedAutomata)
        elif operator in self.binaryOperators:
            if len(self.automata) < 2:
                raise BaseException(
                    f"Error processing operator {operator}. Inadequate operands"
                )
            a = self.automata.pop()
            b = self.automata.pop()
            if operator == self.orOperator:
                self.automata.append(BuildAutomata.unionStruct(b, a))
            elif operator == self.concatOperator:
                self.automata.append(BuildAutomata.concatenationStruct(b, a))
