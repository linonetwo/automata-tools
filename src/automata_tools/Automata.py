from typing import Set, Dict, Optional, List, Callable, Union

from automata_tools.constants import EPSILON

IAutomataTransitions = Dict[int, Dict[int, Set[str]]]
IAutomataExecutor = Callable[[List[str], int, List[int], IAutomataTransitions], bool]

class Automata:
    """class to represent an Automata"""

    executer: IAutomataExecutor
    tokenizer: Callable[[str], List[str]]
    def __init__(self, language=set(['0', '1'])):
        self.states: Set[int] = set()
        self.startstate: Optional[int] = None
        self.finalstates: List[int] = []
        self.transitions: IAutomataTransitions = dict()
        self.language: Set[str] = language

        defaultExecuter: IAutomataExecutor = lambda tokens, startState, finalStates, transitions: True
        self.executer = defaultExecuter
        self.tokenizer = lambda input: input.split(' ')[::-1]

    def setExecuter(self, executerFunction: IAutomataExecutor):
        self.executer = executerFunction

    def setTokenizer(self, tokenizerFunction: Callable[[str], List[str]]):
        self.tokenizer = tokenizerFunction

    def execute(self, input: str) -> bool:
        """
        test whether input string can let automata go from initial state to final state
        """
        if not isinstance(self.startstate, int):
            raise BaseException("startstate is not a interger, please init this automata properly")
        if not callable(self.executer):
            raise BaseException("executer is not a Function, please use setExecuter to set a valid function")
        tokens = self.tokenizer(input)
        return self.executer(tokens, self.startstate, self.finalstates, self.transitions)

    def to_dict(self):
        return {
            'states': self.states,
            'startstate': self.startstate,
            'finalstates': self.finalstates,
            'transitions': self.transitions,
            'language': self.language
        }

    def setstartstate(self, state: int):
        self.startstate = state
        self.states.add(state)

    def addfinalstates(self, state: Union[int, List[int]]):
        if isinstance(state, int):
            state = [state]
        for s in state:
            if s not in self.finalstates:
                self.finalstates.append(s)

    def addtransition(self, fromstate: int, tostate: int,
                      inp: Union[str, Set[str]]):
        if isinstance(inp, str):
            inp = set([inp])
        self.states.add(fromstate)
        self.states.add(tostate)
        if fromstate in self.transitions:
            if tostate in self.transitions[fromstate]:
                self.transitions[fromstate][tostate] = self.transitions[
                    fromstate][tostate].union(inp)
            else:
                self.transitions[fromstate][tostate] = inp
        else:
            self.transitions[fromstate] = {tostate: inp}

    def addtransition_dict(self, transitions: IAutomataTransitions):
        for fromstate, tostates in transitions.items():
            for state in tostates:
                self.addtransition(fromstate, state, tostates[state])

    def gettransitions(self, states: Union[int, List[int]], token: str):
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
        print("final states:", self.finalstates)
        print("transitions:")
        for fromstate, tostates in self.transitions.items():
            for state in tostates:
                for char in tostates[state]:
                    print("  ", fromstate, "->", state, "on '" + char + "'")

    def getPrintText(self):
        text = "language: {" + ", ".join(self.language) + "}\n"
        text += "states: {" + ", ".join(map(str, self.states)) + "}\n"
        text += "start state: " + str(self.startstate) + "\n"
        text += "final states: {" + ", ".join(map(str,
                                                  self.finalstates)) + "}\n"
        text += "transitions:\n"
        linecount = 5
        for fromstate, tostates in self.transitions.items():
            for state in tostates:
                for char in tostates[state]:
                    text += "    " + str(fromstate) + " -> " + str(
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
        plus.setstartstate(state1)
        plus.addfinalstates(state2)
        ```

        也可以用来复制一个自动机 `withNewStateNumber(0)`
        """
        if not isinstance(self.startstate, int):
            raise Exception("You should set startState before rebuild states")
        translations: Dict[int, int] = {}
        for i in list(self.states):
            translations[i] = startStateNumber
            startStateNumber += 1
        combinedAutomata = Automata(self.language)
        combinedAutomata.setstartstate(translations[self.startstate])
        combinedAutomata.addfinalstates(translations[self.finalstates[0]])
        for fromstate, tostates in self.transitions.items():
            for state in tostates:
                combinedAutomata.addtransition(translations[fromstate],
                                               translations[state],
                                               tostates[state])
        return [combinedAutomata, startStateNumber]

    def newBuildFromEquivalentStates(self, equivalent, pos):
        """
        等价状态的合并
        """
        rebuild = Automata(self.language)
        for fromstate, tostates in self.transitions.items():
            for state in tostates:
                rebuild.addtransition(pos[fromstate], pos[state],
                                      tostates[state])
        rebuild.setstartstate(pos[self.startstate])
        for s in self.finalstates:
            rebuild.addfinalstates(pos[s])
        return rebuild

    def getDotFile(self):
        dotFile = "digraph DFA {\nrankdir=LR\n"
        if len(self.states) != 0:
            dotFile += "root=s1\nstart [shape=point]\nstart->s%d\n" % self.startstate
            for state in self.states:
                if state in self.finalstates:
                    dotFile += "s%d [shape=doublecircle]\n" % state
                else:
                    dotFile += "s%d [shape=circle]\n" % state
            for fromstate, tostates in self.transitions.items():
                for state in tostates:
                    for char in tostates[state]:
                        dotFile += 's%d->s%d [label="%s"]\n' % (fromstate,
                                                                state, char)
        dotFile += "}"
        return dotFile
