from pyparsing import Literal, Word, alphas, Optional, OneOrMore, Forward, Group, ZeroOrMore, Literal, Empty, oneOf, nums, ParserElement
from pydash import flatten_deep

ParserElement.enablePackrat()

# $ means words, % means numbers, & means punctuations
WildCards = oneOf("$ % &")
LeafWord = WildCards | Word(alphas)
# aaa+ aaa* aaa? aaa{0,3} aaa{2}
RangedQuantifiers = Literal("{") + Word(nums) + Optional(
    Literal(",") + Word(nums)) + Literal("}")
Quantifiers = oneOf("* + ?") | RangedQuantifiers
QuantifiedLeafWord = LeafWord + Quantifiers
# a sequence
ConcatenatedSequence = OneOrMore(QuantifiedLeafWord | LeafWord)
# syntax root
Rule = Forward()
# ( xxx )
GroupStatement = Forward()
QuantifiedGroup = GroupStatement + Quantifiers
# xxx | yyy
orAbleStatement = QuantifiedGroup | GroupStatement | ConcatenatedSequence
OrStatement = Group(orAbleStatement +
                    OneOrMore(Literal("|") + Group(orAbleStatement)))

GroupStatement << Group(Literal("(") + Rule + Literal(")"))
Rule << OneOrMore(OrStatement | orAbleStatement)
ruleParser = lambda ruleString: flatten_deep(
    Rule.parseString(ruleString).asList())

if __name__ == "__main__":
    ruleString = "$ * (airfare | fares | fare | cost | costs | class ( ticket | tickets ) {0,3} | how much) $ *"
    parseResult = ruleParser(ruleString)
    print(parseResult)
