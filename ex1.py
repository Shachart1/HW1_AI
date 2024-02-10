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

    def __init__(self, marineships: dict, pirateships: dict,
                 collected: set = None, on_ship: dict = None):  # not sure if marine ships is necessary
        self.marineships = marineships
        # current index of marineships in its movement array.

        # self.marineships_current = dict([(list(marineships.keys())[i], 0) for i in range(len(marineships.keys()))])
        self.pirateships = pirateships
        if collected is None:
            self.collected = set()
        else:
            self.collected = collected
        if on_ship is None:
            self.on_ship = dict([(list(pirateships.keys())[i], set()) for i in
                                 range(len(pirateships.keys()))])  # not sure if needed argument on_ship
        else:
            self.on_ship = on_ship

    # TODO - is this the definitions we want to go with?
    # def __lt__(self, other):
    #     return self.h_value < other.h_value
    #
    # def __hash__(self):
    #     return len(collected)
    #
    # def __eq__(self, other):
    #     flag = set(self.marineships.keys()).intersection(set(other.marineships.keys())) == set()
    #     flag = flag and (self.marineships[key] == other.marineships[key] for key in self.marineships.keys())
    #     flag = flag and (self.pirateships[key] == other.pirateships[key] for key in self.pirateships.keys())
    #     flag = flag and (self.collected.intersection(other.collected) == set())
    #     return flag and (self.on_ship == other.on_ship)

    def __str__(self):
        to_print = "marine ships: " + str(self.marineships)
        to_print += "\n pirate ships: " + str(self.pirateships)
        to_print += "\n collected treasures: " + str(self.collected)
        to_print += "\n treasures on ships: " + str(self.on_ship)
        return to_print

    def to_hashable(self):
        state_dict = {
            "marineships": str(self.marineships),
            "pirateships": str(self.pirateships),
            "collected": str(self.collected),
            "on_ship": str(self.on_ship),
        }
        return str(state_dict)

    @classmethod
    def from_hashable(cls, hashable_string: str):
        state_dictionary = eval(hashable_string)
        marineships = eval(state_dictionary["marineships"])
        pirateships = eval(state_dictionary["pirateships"])
        collected = eval(state_dictionary["collected"])
        on_ship = eval(state_dictionary["on_ship"])
        return State(marineships, pirateships, collected, on_ship)


class OnePieceProblem(search.Problem):

    def root_builder(self, marineships: dict):
        # I added these so the state saves only the initial location of marine ships
        initial_location = {(key, (0, len(marineships.get(key)))) for key in marineships.keys()}
        return initial_location

    def __init__(self, initial):
        search.Problem.__init__(self, initial)
        """
        static attributes - saved in the entire problem scope since they won't change
        """
        self.treasures = initial.get("treasures")
        self.maps = initial.get("map")
        self.marine_locations_array = initial.get("marine_ships")  # addition for the functions
        marins = {key: (0, initial.get("marine_ships").get(key)) for key in
                  initial.get("marine_ships").keys()}
        pirates = initial.get(
            "pirate_ships")  # TODO - VERY IMPORTANT CHECK WHAT THIS KEY IS!!!!! IT IS NOT CONSISTENT IN THEIR TESTS!!!!!!!
        self.root = search.Node(State(marins, pirates).to_hashable())
        self.columns = len(self.maps[0])
        self.rows = len(self.maps)
        self.base = initial.get("pirate_ships")[list(pirates.keys())[
            0]]  # TODO - VERY IMPORTANT CHECK WHAT THIS KEY IS!!!!! IT IS NOT CONSISTENT IN THEIR TESTS!!!!!!!
        self.treasure_holders = {key: None for key in self.treasures.keys()}

    """ action activators """

    # in all of these we need to change 'new_state' based on the action provided

    def actions(self, state: str):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        new_state = State.from_hashable(state)
        actions = []

        #   TODO - implementing these
        actions_by_ship = []
        for ship in new_state.pirateships.keys():
            actions_by_ship.append(self.get_actions_for_ship(new_state, ship))
        actions = list(product(*actions_by_ship))

        return actions

    def result(self, state: str, actions):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""

        # TODO - implementing these
        new_state = self.duplicate_state(State.from_hashable(state))
        self.move_marine(new_state)
        for action in actions:
            if action[0] == "sail":
                new_state.pirateships[action[1]] = action[2]
                self.pirates_marine_encounter(new_state, action[1], action[2])
            elif action[0] == "collect_treasure":
                new_state.on_ship[action[1]].add(action[2])
            elif action[0] == "deposit_treasures":
                ##### here i wanted to add the other dict with who owns the ship
                for treasure in new_state.onship[action[1]]:
                    new_state.collected.add(treasure)
                    self.treasure_holders[treasure] = None  ######
                new_state.onship[action[1]] = set()  # now the pirateship is empty

        return new_state.to_hashable()

    def goal_test(self, state):
        """ Given a state, checks if all treasures have been collected """
        new_state = State.from_hashable(state)
        for treasure in self.treasures.keys():
            if treasure not in new_state.collected:
                return False
        return True

    def h(self, node: search.Node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        new_state = State.from_hashable(node.state)
        return self.h_test(node)

    def h_1(self, node: search.Node):
        new_state = State.from_hashable(node.state)
        uncollected = set(self.treasures.keys()).difference(new_state.collected)  # works only on sets
        return float(len(uncollected) / len(new_state.pirateships))

    def h_2(self, node: search.Node):
        distances = manhattan_distances(self.maps, self.base)
        location_frame_dict = None
        min_values_dict = None
        sum = None
        for treasure in self.treasures.keys():  # might change here to use the min manhattan function
            location_frame = [(treasure, distances[element[0], element[1]]) for element in
                              possible_frame(self, int(self.treasures[treasure][0]), int(self.treasures[treasure][
                                                                                             1]))]  # it will save a tuple of location,distance for an adjacent cell to the treasure
            location_frame_dict = {key: value for key, value in location_frame}
        for treasure in treasure_dict.keys():
            if self.treasure_holders[treasure] != None:
                new_state = State.from_hashable(Node.state)
                treasure_dict[treasure] = min(treasure_dict[treasure], min_manhattan_around(distances, int(
                    self.new_state.pirateships[self.treasure_holders[treasure]][0]), int(
                    self.new_state.pirateships[self.treasure_holders[treasure]][1]))
                                              )  ## current_State should be saved
                location_frame_dict[treasure].append(distances[int(
                    new_state.pirateships[treasure_holders[treasure]][0]), int(
                    new_state.pirateships[treasure_holders[treasure]][1])])
                min_values_dict[treasure] = {key: min(values) for key, values in location_frame_dict.items()}
                sum.append(float(min_values_dict[treasure] / len(new_state.pirateships.keys())))
        return sum

    def min_manhattan_around(self, distances, row, col):
        frame = possible_frame(row, col)
        frame_distances = []
        if frame != None:
            for element in frame:
                frame_distances.append(distances[element[0], element[1]])
        else:
            frame_distances = float('inf')
        return min(frame_distances)

    def h_test(self, node):
        new_state = State.from_hashable(node.state)
        treasures_on_ships = set()
        for ship in new_state.pirateships.keys():
            treasures_on_ships.union(new_state.on_ship[ship])
        uncollected = set(self.treasures.keys()).difference(new_state.collected)  # works only on sets
        return float((20 * len(uncollected) - 10 * len(treasures_on_ships)) / len(new_state.pirateships))

    def manhattan_distances(map_array, base):
        rows = len(map_array)
        cols = len(map_array[0]) if rows > 0 else 0

        # Find the coordinates of 'B'
        b_row = int(base[0])
        b_col = int(base[1])

        # Calculate Manhattan distances for each cell from 'B'
        distances = [[abs(i - b_row) + abs(j - b_col) for j in range(cols)] for i in range(rows)]

        return distances

    def manhattan_distance_blocked(map, start, blocked):
        rows, cols = len(map), len(map[0])
        distances = [[float('inf')] * cols for _ in range(rows)]
        visited = [[False] * cols for _ in range(rows)]

        queue = [(start[0], start[1], 0)]  # (row, col, distance)
        distances[start[0]][start[1]] = 0

        while queue:
            current_row, current_col, current_distance = queue.pop(0)
            visited[current_row][current_col] = True

            neighbors = [
                (current_row - 1, current_col),
                (current_row + 1, current_col),
                (current_row, current_col - 1),
                (current_row, current_col + 1),
            ]

            for neighbor_row, neighbor_col in neighbors:
                if 0 <= neighbor_row < rows and 0 <= neighbor_col < cols and not visited[neighbor_row][neighbor_col] and \
                        map[neighbor_row][neighbor_col] != blocked:
                    new_distance = current_distance + 1
                    if new_distance < distances[neighbor_row][neighbor_col]:
                        distances[neighbor_row][neighbor_col] = new_distance
                        queue.append((neighbor_row, neighbor_col, new_distance))

        return distances

    """ action providers """

    # in all of these we can change the elements type from str if we find a better way to represent an action. maybe tuple?
    def move_marine(self, new_state: State):
        for ship in new_state.marineships:
            if len(new_state.marineships[ship][1]) == 1:  # the marine stays still
                return

            if new_state.marineships[ship][0] == len(new_state.marineships[ship][1]) - 1:
                new_state.marineships[ship][1].reverse()
                current = new_state.marineships[ship]
                new_state.marineships[ship] = (0, current[1])

            current_index_in_location_array = new_state.marineships[ship][0]
            location_array = new_state.marineships[ship][1]
            current_index_in_location_array += 1
            new_state.marineships[ship] = (current_index_in_location_array,
                                           location_array)
            self.marine_pirates_encounter(new_state, location_array[current_index_in_location_array])

    def marine_pirates_encounter(self, new_state: State, location: str):
        for pirate in new_state.pirateships.keys():
            if new_state.pirateships[pirate] == location:
                new_state.on_ship[pirate] = set()

    def pirates_marine_encounter(self, new_state: State, pirate: str, location: str):
        for marine in new_state.marineships.keys():
            marine_locations_array = new_state.marineships[marine][1]
            marine_index = new_state.marineships[marine][0]
            if marine_locations_array[marine_index] == location:
                new_state.on_ship[pirate] = set()

    def get_actions_for_ship(self, state, ship):
        actions = []
        row_index = state.pirateships.get(ship)[0]
        col_index = state.pirateships.get(ship)[1]
        location = [row_index, col_index]
        if self.maps[row_index][col_index] == 'B':  # if current location is at base it can deposit
            actions.append(("deposit_treasure", ship))
        ship_frame = self.possible_frame(row_index, col_index)
        for step in ship_frame:
            if self.maps[step[0]][step[1]] == 'S' or self.maps[step[0]][step[1]] == 'B':
                actions.append(("sail", ship, (step[0], step[1])))  # not sure if necessary to string it
            else:  # if it is "I"
                treasure = self.get_treasure_from_island(step)
                if treasure:
                    actions.append(("collect", ship, treasure))
                    self.treasure_holders[treasure] = ship
        return actions

    def possible_frame(self, row, col):
        if row == 0:
            if col == (self.columns - 1):
                return [[row + 1, col], [row, col - 1]]  # top right corner
            if col == 0:
                return [[row + 1, col], [row, col + 1]]  # top left corner
            else:
                return [[row + 1, col], [row, col - 1], [row, col + 1]]  # top row


        elif row == (self.rows - 1):
            if col == 0:
                arr = [[row, col + 1], [row - 1, col]]
                return [[row, col + 1], [row - 1, col]]  # bottom left corner

            if col == (self.columns - 1):  # bottom right corner
                return [[row, col - 1], [row - 1, col]]

            else:
                return [[row, col - 1], [row - 1, col], [row, col + 1]]  # bottom row

        elif col == 0:  # left col. without corners...
            return [[row - 1, col], [row + 1, col], [row, col + 1]]

        elif col == self.columns - 1:  # right col. without corners...
            return [[row - 1, col], [row + 1, col], [row, col - 1]]

        else:
            return [[row + 1, col], [row - 1, col], [row, col - 1], [row, col + 1]]

    def get_treasure_from_island(self, step: List[int]):
        for key in self.treasures.keys():
            if self.treasures[key] == tuple(step):
                return key
        return None

    def duplicate_state(self, state):
        return State(state.marineships, state.pirateships, state.collected, state.on_ship)

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""


def create_onepiece_problem(game):
    return OnePieceProblem(game)
