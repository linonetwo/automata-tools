Feature: Minify DFA state on given DFA
  In order to run automata efficiently,
  I want its state as less as possible
  So I use minify DFA algorithm to refactor its states

  Scenario: Find text with certain words
    Given the rule "($* ( ccc | what ) $* bbb $*)|($* ccc $*)"
      Then it matches sentence "a what a bbb"
      And it matches sentence "ccc what bbb"
      But it won't match sentence "what is the abbreviated expression for the national bureau of investigation ?"
