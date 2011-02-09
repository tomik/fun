"""
Simulation of "hawks and doves" territorial behaviour.

Population of individuals.
Each round 2 of them fight for given payoff. 
Fitness of individual is his average payoff per fight.
Once in a time the weakest individual is replaced by an individual of randomly selected species.

Strategies are aggresive, peaceful (see the payoff matrix)
Species are Hawks(always aggresive), Doves(always peaceful), 
            Mutants(sometimes aggresive, sometimes peaceful in a fixed ratio), 
            Adaptable(peaceful to adaptable, aggresive to everyone else)
                - these guys obviously abuse information and are the strongest species

RESULTS:
    * hawks against doves reaches a fixed ratio (in given circumstances its around 3.5 hawks : 6.5 doves) 
    * best are (as expected) adaptables - 
        * against hawks they have slow start, but as they take off (around 50% of the pop) they go over 95%
    * under current conditions (evo replace in fixed probability with equal chance for every species) 
        the initial percentage of species doesn't matter - the equilibrium will be reached from evey starting position
    * mutants get quite good results in 1 on 1 against both doves and hawks (both over 80%)
    * results are quite sensitive to the mechanism behind 
        * especially tricky is how to calculate fitness for very young individuals (protect them, but not too much)

PROGRAMMING STUFF:
    * carefully with [mutable_object] * n - list of references to the same object is created
"""

import random

POP_SIZE = 1000
ROUNDS = 100000 
STATS_FREQ = 1000
EVO_REPLACE_PROB = 0.1

POF_WIN = 15 
POF_LOSE = 0
POF_FIGHT_COST = -30 
POF_LOST_TIME = -2.5 

ST_AGGRESIVE = "aggresive"
ST_PEACEFUL = "peaceful"
RES_UNKNOWN = "unknown" 

PAYOFF_MATRIX = {
    ST_AGGRESIVE: {
                ST_AGGRESIVE: POF_WIN/2.0 + POF_FIGHT_COST,
                ST_PEACEFUL: POF_WIN,
                },
    ST_PEACEFUL: {
                ST_AGGRESIVE: 0,
                ST_PEACEFUL: POF_WIN/2.0 + POF_LOST_TIME,
              }
}

class Indi(object):
    """
    Generic individual
    """
    def __init__(self):
        self.payoff = 0
        self.age = 0
        self.fights = 0
        
    @classmethod
    def get_strategy(cls, opponent_species=None):
        return cls.IMPLICIT_STRATEGY

    @property
    def fitness(self):
        """
        Fitness is average payoff per fight. Younglings are protected a "free win"
        """
        if self.fights == 0:
            return POF_WIN
        else:
            return float(self.payoff) / self.fights

    def replicate(self):
        return self.__class__()

    @classmethod
    def get_name(cls):
        return cls.__name__.lower()

    def get_species(self):
        return self.__class__

    def __str__(self):
        return self.__class__.get_name()

class Dove(Indi):
    IMPLICIT_STRATEGY = ST_PEACEFUL

class Hawk(Indi):
    IMPLICIT_STRATEGY = ST_AGGRESIVE

class Mutant(Indi):
    """
    Ratio of aggresiveness x peacefulness is taken from results 1 on 1 hawks x doves.
    """

    @classmethod
    def get_strategy(cls, opponent_species=None):
        if random.random() <= 0.3:
            return ST_AGGRESIVE
        else:
            return ST_PEACEFUL

class Adaptable(Indi):
    """
    Peaceful against Adaptables otherwise aggresive
    """

    @classmethod
    def get_strategy(cls, opponent_species=None):
        if opponent_species == Adaptable: 
            return ST_PEACEFUL
        else:
            return ST_AGGRESIVE

#Species classes with their initial percentage in the population
SPECIES = {
             Hawk: 0,
             Adaptable: 0, 
             Dove: 1, 
             Mutant: 0
             }

class Pop(object):
    """
    Population - stores indis, performs fights, updates and evolutionary replace
    """
    def __init__(self, species, pop_size):
        self.indis = []
        self.representants = dict(zip(species.keys(), [0] * len(species)))

        for species, percentage in species.items():
            count = int(percentage * pop_size)
            self.representants[species] = count
            self.indis.extend([species() for _ in xrange(count)])

    def update_ages(self):
        for indi in self.indis:
            indi.age += 1

    def perform_fight(self):
        """
        Payoff of indi is payoff accumulated in past 10 FIGHTS_MATURE fights.
        """
        indi1, indi2 = random.sample(self.indis, 2)
        payoff1, payoff2 = self._calc_payoffs(indi1, indi2)
        for indi, payoff in [(indi1, payoff1), (indi2, payoff2)]:
            indi.fights += 1
            indi.payoff += payoff
        
    def perform_evo_replace(self):
        """
        Selects weakest indi and replaces it with random indi.
        """
        weakest = min(self.indis, key=lambda indi: indi.fitness)
        index = self.indis.index(weakest)
        self._replace_indi_by_index(index)

    def print_stats(self, round):
        print "Population statistics in round %d:" % round
        for r, count in self.representants.items():
            print "%s: %d" % (r.get_name(), count) 
        #print top ten fitness
        print "Top10: "
        for indi in sorted(self.indis, key=lambda indi: indi.fitness, reverse=True)[:10]:
            print "%s: %s" % (indi, indi.fitness)

    @staticmethod
    def _calc_payoffs(indi1, indi2):
        strategy1 = indi1.get_strategy(indi2.get_species())
        strategy2 = indi2.get_strategy(indi1.get_species())
        return (PAYOFF_MATRIX[strategy1][strategy2], 
                PAYOFF_MATRIX[strategy2][strategy1])

    def _replace_indi_by_index(self, index, new_indi=None):
        if not new_indi:
            new_indi = random.choice(SPECIES.keys())()
        old_indi = self.indis[index]
        self.indis[index] = new_indi
        self.representants[old_indi.get_species()] -= 1
        self.representants[new_indi.get_species()] += 1
        #print "Replacing dead %s with %s" % (indi, new_indi)

def run():
    pop = Pop(SPECIES, POP_SIZE) 

    for round in xrange(ROUNDS):
        pop.perform_fight()
        pop.update_ages()
        if EVO_REPLACE_PROB and EVO_REPLACE_PROB > random.random():
            pop.perform_evo_replace()

        if round % STATS_FREQ == 0:
            pop.print_stats(round)

if __name__ == "__main__":
    run()

