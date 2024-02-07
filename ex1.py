import search
import random
from itertools import product


ids = ["208114744", "206394280"]

class State:
    """
        marineships - dict with name of ship and it's movement
        pirateships - dict with name of ship and it's location
        collected - set of collected treasures
        on_ship - dict where key is ship ID and value is treasures on ship
    """
    def __init__(self, marineships: dict, pirateships: dict, collected: set = None, on_ship: dict = None): #not sure if marine ships is necessary
        self.marineships = marineships
        # current index of marineships in it's movment array.

        self.marineships_current = dict([(list(marineships.keys())[i], 0) for i in range(len(marineships.keys()))])
        self.pirateships = pirateships
        if collected is None:
            collected = set()
        else:
            self.collected = collected
        if on_ship is None:
            self.onship = dict([(list(pirateships.keys())[i], set()) for i in range(len(pirateships.keys()))]) #not sure if needed argument on_ship
        else:
            self.onship = on_ship
        self.h_value = float('inf')

    # TODO - is this the definitions we want to go with?
    def __lt__(self, other: State):
        return self.h_value < other.h_value

    def __hash__(self):
        return len(collected)

    def __eq__(self, other):
        flag = set(self.marineships.keys()).intersection(set(other.marineships.keys())) == set()
        flag = flag and (self.marineships[key] == other.marineships[key] for key in self.marineships.keys())
        flag = flag and (self.pirateships[key] == other.pirateships[key] for key in self.pirateships.keys())
        flag = flag and (self.collected.intersection(other.collected) == set())
        return flag and (self.on_ship == other.on_ship)


class OnePieceProblem(search.Problem):

    def __init__(self, initial):
        search.Problem.__init__(self, initial)
        """
        static attributes - saved in the entire problem scope since they won't change
        """
        self.treasures = initial.get("treasures")
        self.maps = initial.get("map")
        self.marine_locations = initial.get("marine_ships") #addition for the functions
        self.root = search.Node(State(initial.get("pirate_ships"),root_builder(initial.get("marine_ships"))))
        self.columns = len(self.maps[0])
        self.rows = len(self.maps)


    def root_builder(dict:marineships): # I added these so the state saves only the initial location of marine ships
        initial_location = {key: value[0] for key, value in marineships.items()}
        return initial_location

    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        actions = []
        
        #TODO - implementing these
        actions_by_ship = []
        for ship in self.pirateships.keys():
            actions_by_ship.add(get_actions_for_ship(ship))
        actions = list(product(*actions_by_ship))

        return actions

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        # marine movement will always happen
        for (ship, location) in state.marine_ships:
            if self.marineships_current.get(ship) == location.size:
                location.reverse() # not sure if right function. need to flip the list so that the marines go through their movement list back and forth
                self.marineships_current.put(ship, (marineships_current.get(ship) + 1) % location.size) # to create: 0->1->2->3->1->2->3->1->2->... for an array of size 4
                state.marine_ships.put(ship, location)
            # would increase index after every update of location. if the index passes the size of the array then the % action would reset it to 0(modulo)
            new_marine_location.put(ship, location[marineships_current.get(ship)+1 % location.size])
            marineships_current.put(ship, (marineships_current.get(ship) + 1) % location.size)
        
        #TODO - implementing these
        new_state = duplicate_state(self,state)
        move_marine(self, new_state, new_marine_location)
        move_ship(self, action, new_state)
        collect_treasure(self, action, new_state)
        store_treasure(self, action, new_state)
        return new_state
        

    def goal_test(self, state):
        """ Given a state, checks if all treasures have been collected """

        for treasure in self.treasures.keys():
            if treasure not in state.collected:
                return False
        return True


    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        return 0
        
        
    """ ILAN LOOK HERE!!! """
    
    """ action providers """
    # in all of these we can change the elements type from str if we find a better way to represent an action. maybe tuple?
    def get_actions_for_ship(ship):
        actions = []
        row_index = self.pirateships.get(ship)[0]
        col_index = self.pirateships.get(ship)[1]
        if self.maps[row_index,col_index] == 'B': #if current location is at base it can deposit
            actions.append((ship,("deposit",str(ship),(row_index,col_index))))
        ship_frame = possible_frame(row_index,col_index)
        for step in ship_frame:
            if self.maps[step] == 'S' or self.maps[step] == 'B':
                actions.append((ship, ("sail",str(ship),(step[0],step[1])))) #not sure if necessary to string it
            else: #if it is "I"
                actions.append((ship,("collect",str(ship),(step[0],step[1]))))
        return actions



    def possible_frame(row,col):
        if row == 0:
            if col == (self.columns - 1):
                return [[1,col],[row,col-1]]
            if col == 0:
                return [[row + 1, col +1],[row, col + 1]]
            else:
                return [[row - 1, col],[row, col - 1], [row, col+1]]


        elif row == (self.rows - 1):
            if col == 0:
                return [[row, col + 1],[row -1, col]]

            if col == (self.columns -1): #down right edge
                return [[row, col - 1], [row - 1, col]]

            else:
                return [[row, col - 1], [row - 1, col],[row, col + 1]]
        else:
            return [[row+1,col],[row-1,col],[row,col - 1],[row,col+1]]




    """ action activators """
    # in all of these we need to change 'new_state' based on the action provided
    def move_marine(self, new_state, new_marine_location):
        for ship in self.marineships_current:
            new_state.marineships[ship] = new_marine_location[ship]
    # new_state.marineships[ship] = self.marine_locations.get(ship)[self.new_marine_location.get(ship)]
    # new_marine_location is the new location and not index


    def move_ship(self, action, new_state):
        # for act in action: #assuming it is a tuple of 2/3 indexes, depends on the action
        if act[0] == "sail":
            new_state.pirateships[act[1]] = act[2] #they said that the new location would be the third index of a tuple

    def collect_treasure(self, action, new_state): #we might want to combine these three functions
        # for act in action:
        if act[0] == "collect_treasure":
            new_state.onship[act[1]].add(act[2])

    def deposit_treasures(self, action, new_state):
        # for act in action:
         if act[0] == "deposit_treasures":
            new_state.collected.add(treasure for treasure in new_state.onship[act[1]]) #hopefully it adds the elements of the list and not the list itself
            new_state.onship[act[1]] = set() #now the pirateship is empty

    #potentiallly this function will be instead of the previous three
    def move_ship2(self,action,new_state):
        # for act in action:
            # if act[0] == "wait":
            #     continue
        if act[0] == "sail":
            new_state.pirateships[act[1]] = act[2]
        if act[0] == "collect_treasure":
            new_state.onship[act[1]].add(act[2])
        if act[0] == "deposit_treasures": #might be an "else" but i've thought that the input might have a mistake
            new_state.collected.add(treasure for treasure in new_state.onship[act[1]]) #hopefully it adds the elements of the list and not the list itself
            new_state.onship[act[1]] = [] #now the ship is empty

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""


def create_onepiece_problem(game):
    return OnePieceProblem(game)

