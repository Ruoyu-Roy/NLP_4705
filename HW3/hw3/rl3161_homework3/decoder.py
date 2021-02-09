from conll_reader import DependencyStructure, DependencyEdge, conll_reader
from collections import defaultdict
import copy
import sys

import numpy as np
import keras

from extract_training_data import FeatureExtractor, State

class Parser(object): 

    def __init__(self, extractor, modelfile):
        self.model = keras.models.load_model(modelfile)
        self.extractor = extractor
        
        # The following dictionary from indices to output actions will be useful
        self.output_labels = dict([(index, action) for (action, index) in extractor.output_labels.items()])

    def parse_sentence(self, words, pos):
        state = State(range(1,len(words)))
        state.stack.append(0)    

        while state.buffer:
            # TODO: Write the body of this loop for part 4
            input_vec = self.extractor.get_input_representation(words, pos, state)
            output_vec = self.model.predict(input_vec.reshape((1, 6)))[0]

            sortedIdx_by_possibility = np.argsort(output_vec)[::-1]
            permitted_idx = 0
            permitted_action, rel = self.output_labels[sortedIdx_by_possibility[permitted_idx]]
            while (len(state.stack) == 0 and permitted_action in {'left_arc','right_arc'}) \
                    or (len(state.buffer) == 1 and permitted_action=='shift' and len(state.stack) > 0) \
                    or (len(state.stack) > 0 and state.stack[-1] == 0 and permitted_action == 'left_arc'):
                permitted_idx += 1
                permitted_action, rel = self.output_labels[sortedIdx_by_possibility[permitted_idx]]

            if permitted_action == 'shift':
                state.shift()
            elif permitted_action == 'left_arc':
                state.left_arc(rel)
            elif permitted_action == 'right_arc':
                state.right_arc(rel)

        result = DependencyStructure()
        for p,c,r in state.deps: 
            result.add_deprel(DependencyEdge(c,words[c],pos[c],p, r))
        return result 
        

if __name__ == "__main__":

    WORD_VOCAB_FILE = 'data/words.vocab'
    POS_VOCAB_FILE = 'data/pos.vocab'

    try:
        word_vocab_f = open(WORD_VOCAB_FILE,'r')
        pos_vocab_f = open(POS_VOCAB_FILE,'r') 
    except FileNotFoundError:
        print("Could not find vocabulary files {} and {}".format(WORD_VOCAB_FILE, POS_VOCAB_FILE))
        sys.exit(1) 

    extractor = FeatureExtractor(word_vocab_f, pos_vocab_f)
    parser = Parser(extractor, sys.argv[1])

    with open(sys.argv[2],'r') as in_file: 
        for dtree in conll_reader(in_file):
            words = dtree.words()
            pos = dtree.pos()
            deps = parser.parse_sentence(words, pos)
            print(deps.print_conll())
            print()
