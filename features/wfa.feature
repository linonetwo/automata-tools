Feature: Minify DFA state on given DFA
  In order to run large sized automata dramatically fast,
  We use matrix multiplication to execute DFA
  So It can effieiently operate on scenario that brute force algorithm can not handle properly 

  Scenario: Find text with certain words
    Given the rule "(($ * name & * $ ? a $*)|($ * ( which | what ) $* ( team | group | groups | teams ) $*)|($ * what & * $ ? kind $*)|($ * ( composed | made ) & * $ ? ( from | through | using | by | of ) $*)|($ * what $* called $*)|($ * novel $*)|($ * ( thing | instance | object ) $*)|($ * fear & * $ ? of $*)|($ * ( which | what ) & * $ ? ( play | game | movie | book ) $*)|($ * ( which | what ) $* ( organization | trust | company ) $*))"
      Then it matches sentence "what judith rossner novel was made into a film starring diane keaton ?"
      But it won't match sentence "what is grenada 's main commodity export ?"
      And it won't match sentence "what is it that walks on four legs , then on two legs , then on three ?"
