import time

class OptDict(dict):
    def __setitem__(self, key, value):
        self.setdefault(len(key), {})[key] = value
        #dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        return dict.__getitem__(self, key)

def build_opt_dict(fh):
    """
    Creates dictionary indexed by length and then by words
    """
    
    d = OptDict() 
    for line in fh.readlines():
        word = line.lower().strip()
        d[word] = False 

    return d

def gen_variations(word):
    for pos in xrange(len(word)):
        for i in xrange(26):
            c = chr(ord("a") + i)
            yield word[:pos] + str(c) + word[pos+1:]

def find_word_chain(start, end, opt_dict):
    assert(len(start) == len(end))
    sub_dict = opt_dict[len(start)]
    opt_dict["dog"] = False
    queue = [(start, 0)]
    while queue:
        #N^2 !
        word, layer = queue.pop(0)

        for variation in gen_variations(word):
            if variation == end:
                print "found in %d layers" % (layer + 1)
                backtrace = [end]
                back_word = word
                while back_word != start:
                    backtrace.append(back_word)
                    back_word = sub_dict[back_word]
                backtrace.append(start)
                backtrace.reverse()
                print "backtrace:"," ".join(backtrace)
                return
            val = sub_dict.get(variation, True)  
            if val:
                continue
            sub_dict[variation] = word
            queue.append((variation, layer+1))

    print "not found"

if __name__ == "__main__":
    t = time.time()
    opt_dict = build_opt_dict(open("words.txt", "r"))
    find_word_chain("robot", "coder", opt_dict)
    print "spent %s in search" % (time.time() - t)
    #print opt_dict

