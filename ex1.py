import search
import random
import heapq


ids = ["208114744", "206394280"]


class State:
    """
        marineships - dict with name of ship and it's movment
        pirateships - dict with name of ship and it's location
        collected - set of collected treasures
        on_ship - list of treasures on the ship(matrix if multi ships)
    """
    def __init__(self, dict: marineships, dict: pirateships, set: collected = {}, List: on_ship = {}): #not sure if marine ships is necessary
        self.marineships = marineships
        # current index of marineships in it's movment array.
        self.marineships_current = dict(keys = list(marineships.keys), values = list([0] * marinships.keys.size))
        self.pirateships = pirateships
        self.collected = collected
        self.onship = dict(keys = list(pirateships.keys), values = list([0] * pirateships.keys.size)) #not sure if needed argument on_ship

    def __hash__(self):
        raise NotImplementedError




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

    def root_builder(dict:marineships): # I added these so the state saves only the initial location of marine ships
        initial_location = {key: value[0] for key, value in marineships.items()}
        return initial_location

    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        actions = []
        
        #TODO - implementing these
        actions.add(move_actions(self, state))
        actions.add(collect_actions(self, state))
        actions.add(store_actions(self, state))
        return actions

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        # marine movement will always happen
        for (ship, location) in state.marine_ships:
            if self.marineships_current.get(ship) == location.size:
                location.reverse # not sure if right function. need to flip the list so that the marines go through their movement list back and forth
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
    def move_actions(self, state) -> List[str]:
        raise NotImplementedError
        
    def collect_actions(self, state) -> List[str]:
        raise NotImplementedError
        
    def store_actions(self, state) -> List[str]:
        raise NotImplementedError
        
    """ action activators """
    # in all of these we need to change 'new_state' based on the action provided
    def move_marine(self, new_state, new_marine_location):
        for ship in self.marineships_current:
            new_state.marineships[ship] = self.marine_locations.get(ship)[self.new_marine_location.get(ship)]

    def move_ship(self, action, new_state):
        for act in action: #assuming it is a tuple of 2/3 indexes, depends on the action
            if act[0] == "sail":
                new_state.pirateships[act[1]] = act[2] #they said that the new location would be the third index of a tuple

        raise NotImplementedError
    
    def collect_treasure(self, action, new_state): #we might want to combine these three functions
        for act in action:
            if act[0] == "collect_treasure":
                new_state.onship[act[1]].append(act[2])

        raise NotImplementedError
        
    def deposit_treasures(self, action, new_state):
        for act in action:
            if act[0] == "deposit_treasures":
                new_state.collected.add(treasure for treasure in new_state.onship[act[1]]) #hopefully it adds the elements of the list and not the list itself
                new_state.onship[act[1]] = [] #now the pirateship is empty
        raise NotImplementedError

    #potentiallly this function will be instead of the previous three
    def move_ship2(self,action,new_state):
        for act in action:
            if act[0] == "wait":
                continue
            if act[0] == "sail":
                new_state.pirateships[act[1]] = act[2]
            if act[0] == "collect_treasure":
                new_state.onship[act[1]].append(act[2])
            if act[0] == "deposit_treasures": #might be an "else" but i've thought that the input might have a mistake
                new_state.collected.add(treasure for treasure in new_state.onship[act[1]]) #hopefully it adds the elements of the list and not the list itself
                new_state.onship[act[1]] = [] #now the ship is empty

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""


def create_onepiece_problem(game):
    return OnePieceProblem(game)

