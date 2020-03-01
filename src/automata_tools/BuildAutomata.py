from typing import cast, Optional

from automata_tools.Automata import Automata
from automata_tools.constants import EPSILON


class BuildAutomata:
    """class for building e-nfa basic structures"""
    @staticmethod
    def characterStruct(transitionToken: str):
        """
        If the regular expression is just a character, eg. a, then the corresponding NFA is : (0)-[a]->(1)
        """
        state1 = 1
        state2 = 2
        basic = Automata()
        basic.setstartstate(state1)
        basic.addfinalstates(state2)
        basic.addtransition(1, 2, transitionToken)
        return basic

    @staticmethod
    def unionStruct(a: Automata, b: Automata):
        """
        The union operator is represented by a choice of transitions from a node; thus a|b can be represented as: CREATE (1)<-[a]-(0)-[b]->(1)
        """
        state1 = 1
        [a, m1] = a.withNewStateNumber(2)
        [b, m2] = b.withNewStateNumber(m1)
        state2 = m2
        plus = Automata()
        plus.setstartstate(state1)
        plus.addfinalstates(state2)
        plus.addtransition(cast(int, plus.startstate), cast(int, a.startstate),
                           EPSILON)
        plus.addtransition(cast(int, plus.startstate), cast(int, b.startstate),
                           EPSILON)
        plus.addtransition(a.finalstates[0], plus.finalstates[0], EPSILON)
        plus.addtransition(b.finalstates[0], plus.finalstates[0], EPSILON)
        plus.addtransition_dict(a.transitions)
        plus.addtransition_dict(b.transitions)
        return plus

    @staticmethod
    def concatenationStruct(leftAutomata: Automata, rightAutomata: Automata):
        """
        Concatenation simply involves connecting one NFA to the other; eg. ab is:
        WITH leftAutomata = (0)-[a]->(1), rightAutomata = (0)-[b]->(1)
        CREATE (0)-[a]->(1)-[b]->(2)
        """
        state1 = 1
        [leftAutomata, middleState1] = leftAutomata.withNewStateNumber(1)
        [rightAutomata,
         middleState2] = rightAutomata.withNewStateNumber(middleState1)
        state2 = middleState2 - 1
        dot = Automata()
        dot.setstartstate(state1)
        dot.addfinalstates(state2)
        dot.addtransition(leftAutomata.finalstates[0],
                          cast(int, rightAutomata.startstate), EPSILON)
        dot.addtransition_dict(leftAutomata.transitions)
        dot.addtransition_dict(rightAutomata.transitions)
        return dot

    @staticmethod
    def starStruct(inputAutomata: Automata):
        """
        The Kleene closure must allow for taking zero or more instances of the letter from the input; thus a* looks like: 
        WITH inputAutomata = (1)-[a]->(2)
        CREATE (0)-[ε]->(1)-[a]->(2)-[ε]->(3)
        CREATE (1)<-[ε]-(2)
        CREATE (0)-[ε]->(3)
        """
        [inputAutomata, m1] = inputAutomata.withNewStateNumber(2)
        state1 = 1
        state2 = m1
        star = Automata()
        star.setstartstate(state1)
        star.addfinalstates(state2)
        star.addtransition(cast(int, star.startstate),
                           cast(int, inputAutomata.startstate), EPSILON)
        star.addtransition(cast(int, star.startstate), star.finalstates[0],
                           EPSILON)
        star.addtransition(inputAutomata.finalstates[0], star.finalstates[0],
                           EPSILON)
        # (1)<-[ε]-(2)
        star.addtransition(inputAutomata.finalstates[0],
                           cast(int, inputAutomata.startstate), EPSILON)
        star.addtransition_dict(inputAutomata.transitions)
        return star

    @staticmethod
    def skipStruct(inputAutomata: Automata):
        """
        The skip struct allow for taking zero or one instances of the letter from the input; thus a? looks like: 
        WITH inputAutomata = (1)-[a]->(2)
        CREATE (0)-[ε]->(1)-[a]->(2)-[ε]->(3)
        CREATE (0)-[ε]->(3)
        """
        state1 = 1
        [inputAutomata, m1] = inputAutomata.withNewStateNumber(2)
        state2 = m1
        questionMark = Automata()
        questionMark.setstartstate(state1)
        questionMark.addfinalstates(state2)
        questionMark.addtransition(cast(int, questionMark.startstate),
                                   cast(int, inputAutomata.startstate),
                                   EPSILON)
        questionMark.addtransition(cast(int, questionMark.startstate),
                                   questionMark.finalstates[0], EPSILON)
        questionMark.addtransition(inputAutomata.finalstates[0],
                                   questionMark.finalstates[0], EPSILON)
        questionMark.addtransition_dict(inputAutomata.transitions)
        return questionMark

    @staticmethod
    def repeatStruct(automataToRepeat: Automata, repeatTimes: int) -> Automata:
        """
        Repeat given token for several times, given a{3}, the automata will be: 
        WITH automataToRepeat = (0)-[a]->(1)
        CREATE (0)-[a]->(1)-[a]->(2)-[a]->(3)

        if repeat 0 or 1 times, it actually returns a?
        """
        if repeatTimes <= 1:
            return BuildAutomata.skipStruct(automataToRepeat)
        [repeatedAutomata, _] = automataToRepeat.withNewStateNumber(0)
        for times in range(repeatTimes):
            if times >= 1:
                repeatedAutomata = BuildAutomata.concatenationStruct(
                    repeatedAutomata, automataToRepeat)

        return repeatedAutomata

    @staticmethod
    def repeatRangeStruct(automataToRepeat: Automata,
                          repeatTimesRangeStart: int,
                          repeatTimesRangeEnd: int) -> Automata:
        """
        Repeat given token for several different times, given a{2,3}, the automata will be: 
        WITH automataToRepeat = (0)-[a]->(1)
        CREATE (0)-[a]->(1)-[a]->(4)
        CREATE (0)-[a]->(2)-[a]->(3)-[a]->(4)
        """
        rangeRepeatedAutomata: Optional[Automata] = None

        for repeatTimes in range(repeatTimesRangeStart,
                                 repeatTimesRangeEnd + 1):
            repeatedAutomata = BuildAutomata.repeatStruct(
                automataToRepeat, repeatTimes)
            if rangeRepeatedAutomata is None:
                rangeRepeatedAutomata = repeatedAutomata
            else:
                rangeRepeatedAutomata = BuildAutomata.unionStruct(
                    cast(Automata, rangeRepeatedAutomata), repeatedAutomata)

        if rangeRepeatedAutomata is None:
            [rangeRepeatedAutomata, _] = automataToRepeat.withNewStateNumber(0)
        return cast(Automata, rangeRepeatedAutomata)
