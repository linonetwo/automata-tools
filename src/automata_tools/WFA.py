from automata_tools.Automata import Automata
from typing import Dict, List, Union, Callable
import numpy as np


class WFA:
    dfa: Automata

    def __init__(self, dfa: Automata, word2index: Dict[str, int],
                 dfa_to_tensor: Callable) -> None:
        self.dfa = dfa
        self.dfaDict = self.dfa.to_dict()
        wfaTensor, wfaState2idx, wildcardMatrix, language = dfa_to_tensor(
            self.dfaDict, word2index)
        self.word2index = word2index
        self.wfaTensor = wfaTensor + wildcardMatrix  # word sparse transition matrix and wildcard all 1 transition matrix
        self.wfaState2idx = wfaState2idx
        self.language = language
        self.tokenizer = lambda inputText: self.dfa.tokenizer(inputText)

    def setTokenizer(self, tokenizerFunction: Callable[[str], List[str]]):
        self.tokenizer = tokenizerFunction

    def getStateLength(self) -> int:
        return len(self.dfaDict['states'])

    def getFinalStateIndex(self) -> List[int]:
        return [self.wfaState2idx[i] for i in self.dfaDict['finalstates']]

    def getStartStateIndex(self) -> int:
        return self.wfaState2idx[self.dfaDict['startstate']]

    def execute(self, inputWords: Union[str, np.array]) -> bool:
        if isinstance(inputWords, str):
            inputWordTensor = np.array(
                list(
                    map(lambda word: self.word2index[word],
                        self.tokenizer(inputWords))))
        else:
            inputWordTensor = inputWords
        stateTensor = np.zeros((self.getStateLength(), 1))
        stateTensor[self.getStartStateIndex(
        )] = 1  # set initial state's probability to 1
        # every word have a size SxS transition matrix, where S = self.getStateLength()
        for inputIndex in range(len(inputWordTensor)):
            inputWordIndex = inputWordTensor[inputIndex]
            transitionMatrixOfCurrentInputWord = self.wfaTensor[int(
                inputWordIndex)].transpose()
            stateTensor = np.dot(transitionMatrixOfCurrentInputWord,
                                 stateTensor)
        for index in self.getFinalStateIndex():
            if int(stateTensor[index]) >= 1:
                return True
        return False