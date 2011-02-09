"""
solution to proggitquiz 4: http://proggitquiz.com/challenge/4/
"""

import sys
import random
from math import exp

def calc_distance(coord1, coord2):
    return abs(coord1[0] - coord2[0]) + abs(coord1[1] - coord2[1])

class Disp():
    def __init__(self, coord):
        self.coord = coord

    def get_coord(self):
        return self.coord

    def move(self, new_coord):
        self.coord = new_coord

    def __str__(self):
        return "d%s" % str(self.coord)

class City():
    def __init__(self, coord):
        self.coord = coord

    def get_coord(self):
        return self.coord

    def __str__(self):
        return "c%s" % str(self.coord)

class World(object):

    def __init__(self, width, height, disp_num, cities):
        if (disp_num + len(cities)) > width * height:
            print "too many cities and dispensers for too small grid"
            sys.exit(1)
        self.width = width
        self.height = height
        self.cities = cities

        #TODO inefficient
        cities_coords = set([city.get_coord() for city in self.cities])
        all_coords = [(row, col) for row in xrange(self.height) for col in xrange(self.width) 
                                      if (row, col) not in cities_coords]
        disps = [Disp(coord) for coord in random.sample(all_coords, disp_num)]
        self._init(disps)

    def _init(self, disps):
        self.disps = disps
        self.occupied = set([elem.get_coord() for elem in self.cities + self.disps])
        #total distance from all houses to nearest dispensers
        self.total_distance = self._calc_total_distance()

    def get_solution(self):
        return [disp.get_coord() for disp in self.disps]

    def plug_in_solution(self, solution):
        disps = [Disp(coord) for coord in solution]
        #check positions
        assert(True)
        self._init(disps)

    def to_nice_str(self):
        elems = self.cities + self.disps
        output = [] 
        for row in xrange(self.height):
            for col in xrange(self.width):
                coord = (row, col)
                #TODO inefficient
                present_elems = filter(lambda e: e.get_coord() == coord, elems)
                assert(len(present_elems) in [0, 1])
                if present_elems:
                    output.append(isinstance(present_elems[0], City) and "P" or "d")
                else:
                    output.append(".")
            output.append("\n")
        return "".join(output)

    def move_disp(self, disp, new_disp_coord):
        #print map(str, self.occupied)
        #print disp.get_coord(), new_disp_coord
        if new_disp_coord not in self.occupied:
            self.occupied.remove(disp.get_coord())
            disp.move(new_disp_coord)
            self.occupied.add(new_disp_coord)
            #TODO inefficient - we calculate total distance every step again
            self.total_distance = self._calc_total_distance()
            return True
        return False

    def get_fitness(self):
        return self.total_distance

    def _calc_total_distance(self):
        total_distance = 0
        for city in self.cities:
            closest_disp = calc_distance(self.disps[0].get_coord(), city.get_coord())
            for disp in self.disps[1:]:
                dist = calc_distance(disp.get_coord(), city.get_coord()) 
                closest_disp = min(closest_disp, dist)
            total_distance += closest_disp
        return total_distance

    def __str__(self):
        return "\n size:%sx%s\n total distance: %d \n cities:%s\n dispensers:%s" % \
             (self.height, self.width, self.total_distance, map(str, self.cities), map(str, self.disps))

    @classmethod
    def from_lines(cls, world_lines):
        size, disp_num = world_lines[0].split()
        width, height = size.split("x")

        row = 0
        cities = []
        for line in world_lines[1:]:
            col = 0
            for c in line:
                if c == 'P':
                    cities.append(City((row, col)))
                col += 1
            row += 1 
        return cls(int(width), int(height), int(disp_num), cities)

def accept_func(fitness_diff, temp):
    return exp(fitness_diff/temp)

def get_new_coord(coord, height, width, temp):  
    hstep = random.randint(1, max(int(height * temp), 1))
    wstep = random.randint(1, max(int(width * temp), 1))
    hdir, wdir = random.choice([1, -1]), random.choice([1, -1])
    #print temp, hstep, wstep
    new_coord = (coord[0] + hstep * hdir, coord[1] + wstep * wdir)
    if (new_coord[0] >= 0 and new_coord[1] >= 0) and (new_coord[0] < height and new_coord[1] < width):
        #print "distance: %s" % calc_distance(new_coord, coord)
        return new_coord
    return None
    
def get_random_coord(coord, height, width, temp):  
    return (random.randint(0, height - 1), random.randint(0, width - 1)) 

def run(world, iters, print_results_freq, restart_threshold):
    print "running search on world: %s" % world
    current_fitness = best_fitness = world.get_fitness() 
    best_solution = world.get_solution()
    invalid_coords_num = 0
    restarts_num = 0
    restart_counter = 0
    #heurs
    temp_min = 4 
    temp = temp_max = 10 
    for i in xrange(10, iters):
        if i % print_results_freq == 0:
            print "iter %d current fitness: %f best fitness: %f" % (i, current_fitness, best_fitness)
        temp = max(temp_min, 0.9998 * temp)
        #try to move random disp
        disp = random.choice(world.disps)
        old_coord = disp.get_coord()
        new_coord = get_new_coord(old_coord, world.height, world.width, 1 - float(i)/iters)
        if not new_coord:
            invalid_coords_num += 1
            continue
        if not world.move_disp(disp, new_coord):
            continue
        if accept_func(current_fitness - world.get_fitness(), temp) > random.random():
            current_fitness = world.get_fitness()
            if current_fitness < best_fitness:
                best_fitness = current_fitness
                best_solution = world.get_solution()
                restart_counter = 0
            else:
                if restart_counter >= restart_threshold:
                    current_fitness = best_fitness
                    world.plug_in_solution(best_solution)
                    restarts_num += 1
                restart_counter += 1
        else:
            #rollback
            rollback = world.move_disp(disp, old_coord)
            assert(rollback)

    #print results
    world.plug_in_solution(best_solution)
    print "invalid coords: %s" % invalid_coords_num
    print "restarts: %s" % restarts_num
    print best_fitness, map(str, best_solution)
    print world.to_nice_str(), world.get_fitness()

def search(fp):
    world = World.from_lines(open(fp, "r").readlines())
    run(world, 10000, 100, 25)

if __name__ == '__main__':
    search(sys.argv[1])


