from typing import Set, Dict, Optional, List, Callable, Union
from pydash import flatten, uniq

from automata_tools.constants import EPSILON

IAutomataTransitions = Dict[int, Dict[int, Set[str]]]
IAutomataExecutor = Callable[[List[str], int, List[int], IAutomataTransitions],
                             bool]


class GroupMetadata:
    stateNumbers: List[int]
    def __init__(self, stateNumbers: List[int], groupName: str = ''):
        self.stateNumbers = stateNumbers
        self.stateNumbers.sort()
        self.groupName = groupName

    @property
    def startState(self):
        return self.stateNumbers[0]

    @property
    def finalState(self):
        return self.stateNumbers[-1]

    def toString(self):
        return f"Group{self.groupName}{self.stateNumbers}"

    def __str__(self):
        return self.toString()

    def __repr__(self):
        return self.toString()

    def __eq__(self, other):
        return self.toString() == other.toString()


class Automata:
    """class to represent an Automata"""

    executer: IAutomataExecutor
    tokenizer: Callable[[str], List[str]]
    language: Set[str] # used in DFAtoMinimizedDFA
    groups: List[GroupMetadata] # used for "(xxx)" group match

    def __init__(self, language: Optional[Set[str]] = None, groups: Optional[List[GroupMetadata]] = None):
        self.groups: List[GroupMetadata] = groups if groups != None else []
        self.language = language if language != None else set()
        self.states: Set[int] = set()
        self.startstate: Optional[int] = None
        self.finalStates: List[int] = []
        self.transitions: IAutomataTransitions = dict()

        defaultExecuter: IAutomataExecutor = lambda tokens, startState, finalStates, transitions: True
        self.executer = defaultExecuter
        self.tokenizer = lambda input: input.split(' ')

    def toString(self):
        groupInfo = f',groups:{self.groups}' if self.groups else ''
        return f"Automata{{states:{self.states}{groupInfo},transitions:{self.transitions},language:{self.language}}}"

    def __str__(self):
        return self.toString()

    def __repr__(self):
        return self.toString()

    def setExecuter(self, executerFunction: IAutomataExecutor):
        self.executer = executerFunction

    def setTokenizer(self, tokenizerFunction: Callable[[str], List[str]]):
        self.tokenizer = tokenizerFunction

    def setLanguage(self, newLanguage: Set[str]):
        self.language = newLanguage

    def execute(self, input: str) -> bool:
        """
        test whether input string can let automata go from initial state to final state
        """
        if not isinstance(self.startstate, int):
            raise BaseException(
                "startstate is not a interger, please init this automata properly"
            )
        if not callable(self.executer):
            raise BaseException(
                "executer is not a Function, please use setExecuter to set a valid function"
            )
        tokens = self.tokenizer(input)
        return self.executer(tokens, self.startstate, self.finalStates,
                             self.transitions)

    def setAsGroup(self, groupName: str):
        """
        If we have build a big automata, and wants to annotate it as a "(xxxx)" group, use this
        """
        self.groups.append(GroupMetadata(list(self.states), groupName))

    def addGroups(self, groups: Union[GroupMetadata, List[GroupMetadata]]):
        """
        After we build a concanated automata, we can add group metadata of child automata into it.
        """
        self.groups = uniq(self.groups + flatten([groups]))

    def to_dict(self):
        return {
            'states': self.states,
            'startstate': self.startstate,
            'finalStates': self.finalStates,
            'transitions': self.transitions,
            'language': self.language
        }

    def setStartState(self, state: int):
        self.startstate = state
        self.states.add(state)

    def addfinalStates(self, state: Union[int, List[int]]):
        if isinstance(state, int):
            state = [state]
        for s in state:
            if s not in self.finalStates:
                self.finalStates.append(s)

    def addTransition(self, fromState: int, toState: int,
                      token: Union[str, Set[str]]):
        if isinstance(token, str):
            token = set([token])
        self.states.add(fromState)
        self.states.add(toState)
        if fromState in self.transitions:
            if toState in self.transitions[fromState]:
                self.transitions[fromState][toState] = self.transitions[
                    fromState][toState].union(token)
            else:
                self.transitions[fromState][toState] = token
        else:
            self.transitions[fromState] = {toState: token}

    def addTransitionsByDict(self, transitions: IAutomataTransitions):
        for fromState, toStates in transitions.items():
            for state in toStates:
                self.addTransition(fromState, state, toStates[state])

    def getReachableStates(self, states: Union[int, List[int]], token: str):
        """
        获取某个状态给定一个字符可以到达的所有状态，在 NFA 中会有多个，DFA 中应该只有一个，以 Set[int] 的形式返回
        """
        if isinstance(states, int):
            states = [states]
        transitionsOfCurrentState: Set[int] = set()
        for state in states:
            if state in self.transitions:
                for aTransitionOfCurrentState in self.transitions[state]:
                    if token in self.transitions[state][
                            aTransitionOfCurrentState]:
                        transitionsOfCurrentState.add(
                            aTransitionOfCurrentState)
        return transitionsOfCurrentState

    def getEClosure(self, findstate):
        """
        只通过ε可以到达的状态，即ε闭包
        """
        allstates = set()
        states = set([findstate])
        while len(states) != 0:
            state = states.pop()
            allstates.add(state)
            if state in self.transitions:
                for tns in self.transitions[state]:
                    if EPSILON in self.transitions[state][
                            tns] and tns not in allstates:
                        states.add(tns)
        return allstates

    def display(self):
        print("states:", self.states)
        print("start state: ", self.startstate)
        print("final states:", self.finalStates)
        print("transitions:")
        for fromState, toStates in self.transitions.items():
            for state in toStates:
                for char in toStates[state]:
                    print("  ", fromState, "->", state, "on '" + char + "'")

    def getPrintText(self):
        text = "language: {" + ", ".join(self.language) + "}\n"
        text += "states: {" + ", ".join(map(str, self.states)) + "}\n"
        text += "start state: " + str(self.startstate) + "\n"
        text += "final states: {" + ", ".join(map(str,
                                                  self.finalStates)) + "}\n"
        text += "transitions:\n"
        linecount = 5
        for fromState, toStates in self.transitions.items():
            for state in toStates:
                for char in toStates[state]:
                    text += "    " + str(fromState) + " -> " + str(
                        state) + " on '" + char + "'\n"
                    linecount += 1
        return [text, linecount]

    def withNewStateNumber(self, startStateNumber: int):
        """
        在把两个子自动机整合为一个大自动机时，重编结点编号

        ## 用例

        ```python
        state1 = 1 # 大自动机的第一个状态
        [a, m1] = a.newBuildFromNumber(2) # 子自动机一的状态编号从 2 开始，并会返回子自动机最大的状态号 m1
        [b, m2] = b.newBuildFromNumber(m1) # 子自动机二的状态编号从 m1 开始，并会返回子自动机最大的状态号 m2
        state2 = m2 # 大自动机的最后一个状态
        plus = Automata()
        plus.setStartState(state1)
        plus.addfinalStates(state2)
        ```

        也可以用来复制一个自动机 `withNewStateNumber(0)`
        """
        if not isinstance(self.startstate, int):
            raise Exception("You should set startState before rebuild states")
        translations: Dict[int, int] = {}
        for i in list(self.states):
            translations[i] = startStateNumber
            startStateNumber += 1
        newAutomata = Automata(self.language)
        newAutomata.setStartState(translations[self.startstate])
        newAutomata.addfinalStates(list(map(lambda state: translations[state], self.finalStates)))
        for fromState, toStates in self.transitions.items():
            for state in toStates:
                newAutomata.addTransition(translations[fromState],
                                          translations[state], toStates[state])
        newGroups = []
        for group in self.groups:
            mappedGroupStates = list(
                map(lambda stateID: translations[stateID], group.stateNumbers))
            newGroups.append(GroupMetadata(mappedGroupStates, group.groupName))
        newAutomata.addGroups(newGroups)
        return [newAutomata, startStateNumber]

    def splitNFA(self, splitPoints: List[int]) -> List['Automata']:
        """
        Split NFA into several NFA, useful when you want to NFAtoDFA for each part in parallel, or stript some part of NFA
        """
        splitAutomata = []
        splitPoints = [self.startstate] + splitPoints
        for index, toState in enumerate(splitPoints):
            # TODO： get language subset properly
            subAutomata = Automata()
            if index == len(splitPoints) - 1: # last one
                startState = toState
                finalState = len(self.states) + self.startstate - 1 # we assume self.states start at 1
            else: # first one and middle one
                startState = toState
                finalState = splitPoints[index + 1] + self.startstate - 1

            subAutomata.setStartState(startState)
            subAutomata.addfinalStates([finalState])
            language: Set[str] = set()
            for fromState, toStates in self.transitions.items():
                for toState in toStates:
                    if fromState in range(startState, finalState + 1) and toState in range(startState, finalState + 1):
                        transitionTokens = toStates[toState]
                        language = language.union(transitionTokens)
                        subAutomata.addTransition(fromState, toState, transitionTokens)
            language.remove(EPSILON)
            subAutomata.setLanguage(language)
            subAutomata, _ = subAutomata.withNewStateNumber(1)
            splitAutomata.append(subAutomata)
        return splitAutomata

    def newBuildFromEquivalentStates(self, equivalent, pos):
        """
        等价状态的合并
        """
        rebuild = Automata(self.language)
        for fromState, toStates in self.transitions.items():
            for state in toStates:
                rebuild.addTransition(pos[fromState], pos[state],
                                      toStates[state])
        rebuild.setStartState(pos[self.startstate])
        for s in self.finalStates:
            rebuild.addfinalStates(pos[s])
        return rebuild

    def getDotFile(self):
        dotFile = "digraph DFA {\nrankdir=LR\n"
        if len(self.states) != 0:
            dotFile += "root=s1\nstart [shape=point]\nstart->s%d\n" % self.startstate
            for state in self.states:
                if state in self.finalStates:
                    dotFile += "s%d [shape=doublecircle]\n" % state
                else:
                    dotFile += "s%d [shape=circle]\n" % state
            for fromState, toStates in self.transitions.items():
                for state in toStates:
                    for char in toStates[state]:
                        dotFile += 's%d->s%d [label="%s"]\n' % (fromState,
                                                                state, char)
        dotFile += "}"
        return dotFile
