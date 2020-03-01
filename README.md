# Automata Tools

Tools to build automata from your custom rule.

This package provides a set of handy tools to programmatically build automata, so you can build NFA、DFA、MinimizedDFA、WFA from any custom rules.

## Usage

### Install

```shell
conda install -c conda-forge automata-tools # not available yet
# or
pip install automata-tools
```

### Import

See example in [examples/NFAfromCustomRule.py](examples/NFAfromCustomRule.py)

```python
from typing import List
from automata_tools import BuildAutomata, Automata

automata: List[Automata] = []
```

### BuildAutomata

#### characterStruct

Build simple `(0)-[a]->(1)` automata

```python
automata.append(BuildAutomata.characterStruct(char))
```

### unionStruct

Build automata that is an "or" of two sub-automata `(1)<-[a]-(0)-[b]->(1)`

```python
# to match "a|b"
a = automata.pop()
b = automata.pop()
if operator == "|":
    automata.append(BuildAutomata.unionStruct(b, a))
```

### concatenationStruct

Build automata that is an "and" of two sub-automata `(0)-[a]->(1)-[b]->(2)`

```python
# to match "ab"
a = automata.pop()
b = automata.pop()
automata.append(BuildAutomata.concatenationStruct(b, a))
```

### starStruct

Build automata that looks like the "Kleene closure"

```python
# to match "a*"
if operator == "*":
    a = automata.pop()
    automata.append(BuildAutomata.starStruct(a))
```

### skipStruct

Build automata that looks like the "Kleene closure" but without the loop back `(1)<-[ε]-(2)`, so it only match the token once at most.

```python
# to match "a*"
if operator == "?":
    a = automata.pop()
    automata.append(BuildAutomata.skipStruct(a))
```

### repeatRangeStruct

Build automata that will match the same token for several times `(0)-[a]->(1)-[a]->(2)-[a]->(3)`

```python
# to match "a{3}"
repeatedAutomata = BuildAutomata.repeatStruct(automata, 3)
```

### repeatStruct

Build automata that will match the same token for n to m times

`(0)-[a]->(1)-[a]->(4), (0)-[a]->(2)-[a]->(3)-[a]->(4)`

```python
# to match "a{2,3}"
repeatedAutomata = BuildAutomata.repeatRangeStruct(automata, 2, 3)
```

### Automata

See example in [features/steps/customRule.py](features/steps/customRule.py)

```python
from automata_tools import DFAFromNFA, Automata

from your_implementation import NFAFromRegex, executor

nfa: Automata = NFAFromRegex().buildNFA(rule)
minDFA: Automata = DFAFromNFA(nfa).getMinimizedDFA()
minDFA.setExecuter(executor)

print(minDFA.execute(someText))
```

where `executor` is a function like the one in [examples/NFAfromCustomRule.py](examples/NFAfromCustomRule.py):

```python
def executor(tokens, startState, finalStates, transitions):
    return True
```

### setExecuter

Set an executor to the automata that can freely use state and transition of the automata, and return a boolean value.

```python
from automata_tools import IAutomataExecutor

defaultExecuter: IAutomataExecutor = lambda tokens, startState, finalStates, transitions: True
minDFA.setExecuter(defaultExecuter)
```

### setTokenizer

Set an tokenizer to the automata that can transform string to list of string token, which will be used by the executer.

```python
minDFA.setExecuter(lambda input: input.split(' ')[::-1])
```

## Development

### Environment

Create environment from the text file:

```shell
conda env create --file automataTools-env.txt
conda activate automataTools
```

Save env file: `conda list --explicit > automataTools-env.txt`

### Python Path

Create a `.env` file with content `PYTHONPATH=automataTools`

### Publish

To pypi

```shell
rm -rf ./dist && python3 setup.py sdist bdist_wheel && twine upload dist/*
```

To Conda

```shell
# I'm learning how to do...
```

## Resources

[Automata Theory Course Slides](http://www.cs.may.ie/staff/jpower/Courses/Previous/parsing/node5.html)

Probably the original reference [source](https://github.com/sdht0/automata-from-regex)
