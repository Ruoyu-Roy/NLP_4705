"""
COMS W4705 - Natural Language Processing - Fall B 2020
Homework 2 - Parsing with Context Free Grammars 
Yassine Benajiba
"""

import sys
from collections import defaultdict
from math import fsum

class Pcfg(object): 
    """
    Represent a probabilistic context free grammar. 
    """

    def __init__(self, grammar_file): 
        self.rhs_to_rules = defaultdict(list)
        self.lhs_to_rules = defaultdict(list)
        self.startsymbol = None 
        self.read_rules(grammar_file)      
 
    def read_rules(self,grammar_file):
        
        for line in grammar_file: 
            line = line.strip()
            if line and not line.startswith("#"):
                if "->" in line: 
                    rule = self.parse_rule(line.strip())
                    lhs, rhs, prob = rule
                    self.rhs_to_rules[rhs].append(rule)
                    self.lhs_to_rules[lhs].append(rule)
                else: 
                    startsymbol, prob = line.rsplit(";")
                    self.startsymbol = startsymbol.strip()
                    
     
    def parse_rule(self,rule_s):
        lhs, other = rule_s.split("->")
        lhs = lhs.strip()
        rhs_s, prob_s = other.rsplit(";",1) 
        prob = float(prob_s)
        rhs = tuple(rhs_s.strip().split())
        return (lhs, rhs, prob)

    def verify_grammar(self):
        """
        Return True if the grammar is a valid PCFG in CNF.
        Otherwise return False. 
        """
        # TODO, Part 1
        for lhs_key in self.lhs_to_rules.keys():
            rules = self.lhs_to_rules[lhs_key]
            lhs_probs = []
            for rule in rules:
                lhs, rhs, prob = rule
                lhs_probs.append(prob)
                if len(rhs) not in (1, 2):
                    print('Error Message: ', rhs, 'is not in a format of "A -> BC" or "A -> b"')
                    return False
                elif len(rhs) == 1:
                    for c in rhs[0]:
                        if c.isupper():
                            print('Error Message: ', rhs, 'should all be lower case.')
                            return False
                elif len(rhs) == 2:
                    for c in rhs[0]:
                        if c.islower():
                            print('Error Message: ', rhs, 'should all be UPPER CASE.')
                            return False
                    for c in rhs[1]:
                        if c.islower():
                            print('Error Message: ', rhs, 'should all be UPPER CASE.')
                            return False
            if fsum(lhs_probs) < 0.999 or fsum(lhs_probs) > 1.001:
                print('Error Message: ', lhs, '\'s probability does not sum to 1.0')
                return False

        print("This is a valid PCFG in CNF.")
        return True


if __name__ == "__main__":
    with open(sys.argv[1],'r') as grammar_file:
        grammar = Pcfg(grammar_file)
    print(grammar.verify_grammar())
