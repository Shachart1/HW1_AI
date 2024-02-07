import search
import random
from typing import List
from itertools import product


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
            self.collected = set()
        else:
            self.collected = collected
        if on_ship is None:
            self.on_ship = dict([(list(pirateships.keys())[i], set()) for i in range(len(pirateships.keys()))]) #not sure if needed argument on_ship
        else:
            self.on_ship = on_ship
        self.h_value = float('inf')

    # TODO - is this the definitions we want to go with?
    def __lt__(self, other):
        return self.h_value < other.h_value

    def __hash__(self):
        return len(collected)

    def __eq__(self, other):
        flag = set(self.marineships.keys()).intersection(set(other.marineships.keys())) == set()
        flag = flag and (self.marineships[key] == other.marineships[key] for key in self.marineships.keys())
        flag = flag and (self.pirateships[key] == other.pirateships[key] for key in self.pirateships.keys())
        flag = flag and (self.collected.intersection(other.collected) == set())
        return flag and (self.on_ship == other.on_ship)

    def __str__(self):
        to_print = "marine ships: " + str(self.marineships)
        to_print += "\n pirate ships: " + str(self.pirateships)
        to_print += "\n collected treasures: " + str(self.collected)
        to_print += "\n treasures on ships: " + str(self.on_ship)
        return to_print

class OnePieceProblem(search.Problem):

    def root_builder(self, marineships: dict): # I added these so the state saves only the initial location of marine ships
        initial_location = {(key, (0, len(marineships.get(key)))) for key in marineships.keys()}
        return initial_location

    def __init__(self, initial):
        search.Problem.__init__(self, initial)
        """
        static attributes - saved in the entire problem scope since they won't change
        """
        self.treasures = initial.get("treasures")
        self.maps = initial.get("map")
        self.marine_locations_array = initial.get("marine_ships") #addition for the functions
        marins_test = {key: (0, initial.get("marine_ships").get(key)) for key in
                                                        initial.get("marine_ships").keys()}
        test = initial.get("pirate_ship")
        self.root = search.Node(State(marins_test, test))
        self.columns = len(self.maps[0])
        self.rows = len(self.maps)

    """ action activators """
    # in all of these we need to change 'new_state' based on the action provided

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
        
        #TODO - implementing these
        actions_by_ship = []
        for ship in state.pirateships.keys():
            actions_by_ship.append(self.get_actions_for_ship(state, ship))
        actions = list(product(*actions_by_ship))

        return actions

    def result(self, state, actions):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        
        # TODO - implementing these
        new_state = self.duplicate_state(state)
        self.move_marine(new_state)
        for action in actions:
            if action[0] == "sail":
                new_state.pirateships[action[1]] = action[2]
                self.pirates_marine_encounter(new_state, action[1], action[2])
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


    def h_1(self, node: search.Node):
        uncollected = self.treasures.difference(node.state.collected) # works only on sets
        return len(uncollected)


    """ action providers """
    # in all of these we can change the elements type from str if we find a better way to represent an action. maybe tuple?
    def move_marine(self, new_state: State):
        for ship in new_state.marineships:
            current_index_in_location_array = new_state.marineships[ship][0]
            location_array = new_state.marineships[ship][1]
            current_index_in_location_array += 1
            new_state.marineships[ship] = (current_index_in_location_array,
                                           location_array)
            self.marine_pirates_encounter(new_state, location_array[current_index_in_location_array])

    def marine_pirates_encounter(self, new_state: State, location: str):
        pass

    def pirates_marine_encounter(self, new_state: State, pirate: str, location: str):
        for ship in new_state.marineships:
            pass
        pass

    def get_actions_for_ship(self, state, ship):
        actions = []
        row_index = state.pirateships.get(ship)[0]
        col_index = state.pirateships.get(ship)[1]
        if self.maps[row_index][col_index] == 'B': # if current location is at base it can deposit
            actions.append(("deposit_treasure", ship))
        ship_frame = self.possible_frame(row_index, col_index)
        for step in ship_frame:
            if self.maps[step[0]][step[1]] == 'S' or self.maps[step] == 'B':
                actions.append(("sail", ship, (step[0], step[1]))) # not sure if necessary to string it
            else: # if it is "I"
                treasure = self.get_treasure_from_island(step)
                if treasure:
                    actions.append(("collect", ship, treasure))
        return actions

    def possible_frame(self, row, col):
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
            return [[row+1, col], [row-1, col], [row, col - 1], [row, col+1]]

    def get_treasure_from_island(self, step: List[int]):
        for key in self.treasures.keys():
            if treasures[key] == tuple(step):
                return key
        return None

    def duplicate_state(self, state):
        return State(state.marineships, state.pirateships, state.collected, state.on_ship)

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""


def create_onepiece_problem(game):
    return OnePieceProblem(game)

