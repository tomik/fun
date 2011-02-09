import sys 
import random

import psyco
psyco.full()

EDGE = 10
LIST = "wordlist.txt"
OFF = '!'
ANY = '*'

OFFSETS = [ 1, -1, EDGE, -EDGE, EDGE + 1, EDGE - 1, -EDGE + 1, -EDGE - 1]

def make_puzzle(edge, words):
    size = edge * edge
    puzzle = list(ANY * size)
    placed = [] 
    for i in xrange(1000000):
        to_place = random.choice(words)
        pos = random.randint(0, size)
        offset = random.choice(OFFSETS) 

        verified = True
        act_pos = pos
        for c in to_place:   
            if act_pos < 0 or act_pos >= size or abs((act_pos + offset) % edge - act_pos % edge) > 1  \
               or (puzzle[act_pos] != '*' and puzzle[act_pos] != c):
                verified = False
                break
            act_pos += offset

        if verified:
            placed.append(to_place)
            act_pos = pos
            for c in to_place:
                puzzle[act_pos] = c
                act_pos += offset
            words.remove(to_place)

    print 'words placed:', len(placed)
    print 'letters placed:', sum(map(len, placed))
    print 'empty positions:', puzzle.count('*')
    for word in placed: 
        print word
    return puzzle
    
def print_puzzle(puzzle):
    for i in xrange(EDGE):
        print ''.join(puzzle[i*EDGE: (i+1) * EDGE])

if __name__ == '__main__':
    fp = open(LIST, 'r')
    l = map(lambda x: x.strip(), list(fp.readlines()))
    puzzle = make_puzzle(EDGE, l) 
    print_puzzle(puzzle)
