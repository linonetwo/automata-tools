from automata_tools.Automata import Automata
from typing import Dict
import numpy as np

def is_number(token):
    return token.replace('.', '', 1).isdigit()

punctuations = {
    ',', '，', ':', '：', '!', '！', '《', '》', '。', '；', '.', '(', ')', '（', '）',
    '|', '?', '"'
}

def is_punctuations(token):
    return token in punctuations

def dfa_to_tensor(automata, word2idx: Dict[str, int]):
    """
    Parameters
    ----------
    automata: Automata.to_dict()
    word2idx

    Returns
    -------
    tensor: tensor for language
    state2idx: state to idx
    wildcard_mat: matrix for wildcard
    language: set for language
    """

    all_states = list(automata['states'])
    state2idx = {
        state: idx for idx, state in enumerate(all_states)
    }

    number_indexes = {word: idx for word, idx in word2idx.items() if is_number(word)}
    punctuations_indexes = {word: idx for word, idx in word2idx.items() if is_punctuations(word)}

    max_states = len(automata['states'])
    tensor = np.zeros((len(word2idx), max_states, max_states))

    language = set([])
    language.update(number_indexes.keys())
    language.update(punctuations_indexes.keys())

    wildcard_matrix = np.zeros((max_states, max_states))

    for from_state, to in automata['transitions'].items():
        for to_state, to_edges in to.items():
            for edge in to_edges:
                if edge == '&': # punctuations
                    tensor[list(punctuations_indexes.values()), state2idx[from_state], state2idx[to_state]] = 1
                elif edge == '%': # digits
                    tensor[list(number_indexes.values()), state2idx[from_state], state2idx[to_state]] = 1
                elif edge == "$":
                    wildcard_matrix[state2idx[from_state], state2idx[to_state]] = 1
                else:
                    if edge in word2idx:
                        tensor[word2idx[edge], state2idx[from_state], state2idx[to_state]] = 1
                        language.add(edge)
                    else:
                        print(f'OutOfVocabulary word: {edge} in rule')

    return tensor, state2idx, wildcard_matrix, list(language)
