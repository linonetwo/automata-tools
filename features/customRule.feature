Feature: Write Custom Rule
  In order to parse text with ease,
  As a NLP tool developer
  I want to build automata builder that can parse my simple custom rules
  So I can write my simple rules instead of heavy regex rules

  Scenario: Find text with certain words
    Given the rule "$ * aaa bbb $ *"
      Then it matches sentence "oh my aaa bbb is not a ccc"
      But it won't match sentence "oh my aaa is mine!"

  Scenario: Find text with repeated words
    Given the rule "$ * aaa { 2 , 4 } bbb $ *"
      Then it matches sentence "Ouch aaa aaa bbb cool!"
      Then it matches sentence "Ouch aaa aaa aaa bbb cool!"
      Then it matches sentence "Ouch aaa aaa aaa aaa bbb cool!"
      But it won't match sentence "Ouch aaa bbb cool!"
      And it won't match sentence "Ouch bbb cool!"
