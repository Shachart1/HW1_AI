import search
import random

ids = ["208114744", "206394280"]


class State:
    """
        marineships - dict with name of ship and a tuple for (current index, location array)
        pirateships - dict with name of ship and it's location array
        collected - set of collected treasures
        on_ship - dict where key is ship ID and value is treasures on ship
    """
    def __init__(self, marineships: dict, pirateships: dict, collected: set = None, on_ship: dict = None): #not sure if marine ships is necessary
        self.marineships = marineships
        # current index of marineships in it's movment array.

        # self.marineships_current = dict([(list(marineships.keys())[i], 0) for i in range(len(marineships.keys()))])
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
        self.marine_locations_array = initial.get("marine_ships") #addition for the functions
        self.root = search.Node(State(initial.get("pirate_ships"), root_builder(initial.get("marine_ships"))))

    def root_builder(self, marineships: dict): # I added these so the state saves only the initial location of marine ships
        initial_location = {(key, (0, len(marineships.get(key)))) for key in marineships.keys()}
        return initial_location

    def actions(self, state: State):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        # marine ships will always move
        for ship in state.marineships.keys():
            if state.marineships[ship][0] == len(state.marineships[ship][1]) - 1:
                state.marineships[ship][1].reverse()
                state.marineships[ship][0] = 0
        actions = []
        
        # TODO - implementing these
        actions_by_ship = []
        for ship in self.pirateships.keys():
            actions_by_ship.add(get_actions_for_ship(ship))
        actions = all_permotations(actions_by_ship)
        return actions

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        
        # TODO - implementing these
        new_state = duplicate_state(self, state)
        move_marine(self, new_state, new_marine_location)
        if action[0] == "sail":
            new_state.pirateships[action[1]] = action[2]
        elif action[0] == "collect_treasure":
            new_state.onship[action[1]].add(action[2])
        elif action[0] == "deposit_treasures":
            new_state.collected.add(treasure for treasure in new_state.onship[action[1]])
            new_state.onship[action[1]] = set()  # now the pirateship is empty
        return new_state

    def goal_test(self, state):
        """ Given a state, checks if all treasures have been collected """

        for treasure in self.treasures.keys():
            if treasure not in state.collected:
                return False
        return True

    def h(self, node: search.Node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        node.state.h_value = 0
        return 0
    
    """ action providers """
    # in all of these we can change the elements type from str if we find a better way to represent an action.
    # maybe tuple?
    def move_actions(self, state) -> List[str]:
        raise NotImplementedError
        
    def collect_actions(self, state) -> List[str]:
        raise NotImplementedError
        
    def store_actions(self, state) -> List[str]:
        raise NotImplementedError

    def move_marine(self, new_state: State):
        for ship in new_state.marineships:
            current_index_in_location_array = new_state.marineships[ship][0]
            location_array_size = len(new_state.marineships[ship][1])
            new_state.marineships[ship] = ((current_index_in_location_array + 1), location_array_size)

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""


def create_onepiece_problem(game):
    return OnePieceProblem(game)

