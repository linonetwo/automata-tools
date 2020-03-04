Feature: Write Custom Rule
  In order to parse text with ease,
  As a NLP tool developer
  I want to build automata builder that can parse my simple custom rules
  So I can write my simple rules instead of heavy regex rules

  Scenario: Find text with certain words
    Given the rule "$ * aaa bbb $ *"
      Then it matches sentence "oh my aaa bbb is not a ccc"
      And it matches sentence "aaa bbb"
      But it won't match sentence "oh my aaa is mine!"

  Scenario: Custom tokenizer can split word and punctuations, so we can make & to stand for punctuations in our rules
    Given the rule "$ * & I think $ ( are | is ) $ & $ *"
      Then it matches sentence "well, I think punctuations are cool!"
      And it matches sentence "Wow, I think your are using, punctuations!"

  Scenario: Find text with repeated words
    Given the rule "$ * aaa { 2 , 4 } bbb $ *"
      Then it matches sentence "Ouch aaa aaa bbb cool!"
      Then it matches sentence "Ouch aaa aaa aaa bbb cool!"
      Then it matches sentence "Ouch aaa aaa aaa aaa bbb cool!"
      But it won't match sentence "Ouch aaa bbb cool!"
      And it won't match sentence "Ouch bbb cool!"
    Given the rule "$ * aaa + bbb $ *"
      Then it matches sentence "Ouch aaa bbb cool!"
      Then it matches sentence "Ouch aaa aaa bbb cool!"
      Then it matches sentence "Ouch aaa aaa aaa bbb cool!"
      Then it matches sentence "Ouch aaa aaa aaa aaa bbb cool!"
      And it won't match sentence "Ouch bbb cool!"

  Scenario: Find text with none greedy behavior
    Given the rule "( $ | & ) * and you are BBB $ *"
      Then it matches sentence "Wow, and you are AAA and you are BBB"
      And it matches sentence "Wow, and you are BBB"

  Scenario: Use wildcard and word in a group
    Given the rule "I may have ( $ + | you ) with me"
      Then it matches sentence "I may have you with me"
      And it matches sentence "I may have her with me"
      And it matches sentence "I may have my little three with me"
