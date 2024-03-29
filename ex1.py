import search
import random
from typing import List
from itertools import product
from collections import deque
import json
from bisect import insort
from collections import deque
import math



ids = ["208114744", "206394280"]


class State:
    """
        marineships - dict with name of ship and a tuple for (current index, location array)
        pirateships - dict with name of ship and it's location array
        collected - set of collected treasures
        on_ship - dict where key is ship ID and value is treasures on ship
    """

    def __init__(self, marineships: dict, pirateships: dict,
                 collected: list = None, on_ship: dict = None):  # not sure if marine ships is necessary
        self.marineships = dict(sorted(marineships.items()))
        # current index of marineships in its movement array.

        # self.marineships_current = dict([(list(marineships.keys())[i], 0) for i in range(len(marineships.keys()))])
        self.pirateships = pirateships
        if collected is None:
            self.collected = list()
        else:
            self.collected = collected
        if on_ship is None:
            self.on_ship = dict([(list(pirateships.keys())[i], []) for i in
                                 range(len(pirateships.keys()))])  # not sure if needed argument on_ship
        else:
            self.on_ship = on_ship

    def __str__(self):
        to_print = "marine ships: " + str(self.marineships)
        to_print += "\n pirate ships: " + str(self.pirateships)
        to_print += "\n collected treasures: " + str(self.collected)
        to_print += "\n treasures on ships: " + str(self.on_ship)
        return to_print

    def to_hashable(self):
        state_dict = {
            "marineships": self.marineships,
            "pirateships": self.pirateships,
            "collected": self.collected,
            "on_ship": self.on_ship,
        }
        return json.dumps(state_dict, sort_keys=True)

    @classmethod
    def from_hashable(cls, hashable_string: str):
        state_dictionary = json.loads(hashable_string)
        marineships = dict(sorted(state_dictionary["marineships"].items()))
        pirateships = state_dictionary["pirateships"]
        collected = state_dictionary["collected"]
        on_ship = state_dictionary["on_ship"]
        return cls(marineships, pirateships, collected, on_ship)


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
        marins = {key: (0, initial.get("marine_ships").get(key)) for key in initial.get("marine_ships").keys()}
        pirates = initial.get(
            "pirate_ships")  # TODO - VERY IMPORTANT CHECK WHAT THIS KEY IS!!!!! IT IS NOT CONSISTENT IN THEIR TESTS!!!!!!!
        self.root = search.Node(State(marins, pirates).to_hashable())
        self.columns = len(self.maps[0])
        self.rows = len(self.maps)
        self.base = initial.get("pirate_ships")[list(pirates.keys())[0]]  # TODO - VERY IMPORTANT CHECK WHAT THIS KEY IS!!!!! IT IS NOT CONSISTENT IN THEIR TESTS!!!!!!!
        self.treasure_holders = {key: set() for key in self.treasures.keys()}
        self.distances = self.manhattan_distances(self.maps, self.base)
        island_location_frame = [(treasure,
                                  self.min_manhattan_around(self.distances,
                                                            int(self.treasures[treasure][0]),
                                                            int(self.treasures[treasure][1])))
                                 for treasure in self.treasures.keys()]
        self.island_location_frame_dict = {key: value for (key, value) in island_location_frame}
        self.bfs_distances_map = self.bfs_distance(initial.get("map"))
        for row in range(len(self.bfs_distances_map)):
            for col in range(len(self.bfs_distances_map[0])):
                if self.bfs_distances_map[row][col] == -1:
                    self.bfs_distances_map[row][col] = math.inf

        island_location_frame_bfs = [(treasure,
                                  self.min_manhattan_around(self.bfs_distances_map,
                                                            int(self.treasures[treasure][0]),
                                                            int(self.treasures[treasure][1])))
                                 for treasure in self.treasures.keys()]
        self.island_location_frame_bfs_dict = {key: value for (key, value) in island_location_frame_bfs}
    """ action activators """

    # in all of these we need to change 'new_state' based on the action provided

    def actions(self, state: str):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        new_state = State.from_hashable(state)

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
                current = new_state.pirateships[action[1]]
                new_state.pirateships = dict(sorted(new_state.pirateships.items()))
                new_state.pirateships[action[1]] = action[2]
            elif action[0] == "collect_treasure":
                #new_state.on_ship[action[1]].append(action[2])
                #new_state.on_ship = dict(sorted(
                    #new_state.on_ship.items()))  # first sort by key values so ship_1 will be before ship_2 for example
                for ship in new_state.on_ship:
                    new_state.on_ship[ship] = sorted(new_state.on_ship[ship])  # sort each list of treasures inside
                insort(new_state.on_ship[action[1]], action[2])

                self.treasure_holders[action[2]] = self.treasure_holders[action[2]].union({action[1]})
            elif action[0] == "deposit_treasures":
                # here i wanted to add the other dict with who owns the ship
                for treasure in new_state.on_ship[action[1]]:
                    if treasure not in new_state.collected:
                        insort(new_state.collected, treasure)
                        #new_state.collected = sorted(new_state.collected)
                    self.treasure_holders[treasure] = self.treasure_holders[treasure].difference({action[1]})
                new_state.on_ship[action[1]] = []  # now the pirateship is empty
        self.pirates_marine_encounter(new_state, action[1], new_state.pirateships[action[1]])

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
        return self.h_4(node)

    def h_1(self, node: search.Node):
        new_state = State.from_hashable(node.state)
        uncollected = set(self.treasures.keys()).difference(
            set(new_state.collected).union(set(new_state.on_ship)))  # works only on sets
        return float(len(uncollected) / len(new_state.pirateships))

    def h_2(self, node: search.Node):
        sum = 0
        location_frame_dict = self.island_location_frame_dict
        new_state = State.from_hashable(node.state)
        uncollected_treasures = set(list(self.treasures.keys())).difference(set(new_state.collected))
        for treasure in uncollected_treasures:
            if self.treasure_holders[treasure]:
                treasure_on_ships = [self.min_manhattan_around(self.distances,
                                                               int(new_state.pirateships[ship][0]),
                                                               int(new_state.pirateships[ship][1]))
                                     for ship in self.treasure_holders[treasure]]
                min_treasure_on_ships = min(treasure_on_ships)
                location_frame_dict[treasure] = min(location_frame_dict[treasure], min_treasure_on_ships)
            sum += float(location_frame_dict[treasure])
        return sum / len(new_state.pirateships.keys())

    def h_3(self, node: search.Node):
        sum = 0
        location_frame_dict = self.island_location_frame_dict
        new_state = State.from_hashable(node.state)
        uncollected_treasures = set(list(self.treasures.keys())).difference(set(new_state.collected))
        on_ship_treasures_test = list(new_state.on_ship.values())
        combined_list_of_treasures = list()
        for treasure_list in on_ship_treasures_test:
            combined_list_of_treasures.extend(treasure_list)
        on_ship_treasures_set_test = set()
        if combined_list_of_treasures:
            on_ship_treasures_set_test.union(set(combined_list_of_treasures))
        not_on_ships = set(list(self.treasures.keys()))\
            .difference(set(new_state.collected).union(on_ship_treasures_set_test))

        # Compute min distances for treasures on ships
        for ship in new_state.on_ship.keys():
            ship_helps_flag = False
            for treasure in new_state.on_ship[ship]:
                if location_frame_dict[treasure] < self.distances[int(new_state.pirateships[ship][0])][int(new_state.pirateships[ship][1])]:
                    sum += location_frame_dict[treasure]
                else:
                    ship_helps_flag = True
            if ship_helps_flag:
                sum += self.distances[int(new_state.pirateships[ship][0])][int(new_state.pirateships[ship][1])]

        # add distance from the closest ship to the uncollected treasure
        treasure_island_location = set()
        for treasure in not_on_ships:
            treasure_island_location.add(self.treasures[treasure])
        for treasure_location in treasure_island_location:
            min_distance = float("inf")
            for ship in new_state.pirateships.keys():
                treasure_frame = self.possible_frame(treasure_location[0], treasure_location[1])
                for step in treasure_frame:
                    distance = self.manhattan_distance_a2b(new_state.pirateships[ship], step)
                    min_distance = min(min_distance, distance)
            sum += min_distance + self.distances[treasure_location[0]][treasure_location[1]]
        return sum / (2 * len(new_state.pirateships.keys()))


    def h_4(self, node: search.Node):
        sum = 0
        location_frame_dict = self.island_location_frame_bfs_dict
        new_state = State.from_hashable(node.state)
        uncollected_treasures = set(list(self.treasures.keys())).difference(set(new_state.collected))
        for treasure in uncollected_treasures:
            if self.treasure_holders[treasure]:
                treasure_on_ships = [self.min_manhattan_around(self.bfs_distances_map,
                                                               int(new_state.pirateships[ship][0]),
                                                               int(new_state.pirateships[ship][1]))
                                     for ship in self.treasure_holders[treasure]]
                min_treasure_on_ships = min(treasure_on_ships)
                location_frame_dict[treasure] = min(location_frame_dict[treasure], min_treasure_on_ships)
            sum += float(location_frame_dict[treasure])
        return sum / (2 * len(new_state.pirateships.keys()))    # two treasures on a ship. It's like having two ships



    def min_manhattan_around(self, distances, row, col):
        frame = self.possible_frame(row, col)
        min_distance = float('inf')
        if frame:
            for element in frame:
                if distances[element[0]][element[1]] <= min_distance:
                    min_distance = distances[element[0]][element[1]]
        return min_distance

    def bfs_distance(self, map):
        rows, cols = len(map), len(map[0])
        distance_map = [[-1 for _ in range(cols)] for _ in range(rows)]

        def neighbors(r, c):
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # 4-way connectivity
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and map[nr][nc] != 'I':
                    yield nr, nc

        # Initialize BFS queue
        queue = deque()
        for r in range(rows):
            for c in range(cols):
                if map[r][c] == 'B':
                    queue.append((r, c, 0))  # Append base cells with distance 0
                    distance_map[r][c] = 0  # Distance to self is 0

        # BFS to fill distance_map
        while queue:
            r, c, dist = queue.popleft()
            for nr, nc in neighbors(r, c):
                if distance_map[nr][nc] == -1:  # If not visited
                    distance_map[nr][nc] = dist + 1
                    queue.append((nr, nc, dist + 1))

        return distance_map
    def manhattan_distance_a2b(self, t1, t2):
        return abs(t1[0] - t2[0]) + abs(t1[1] - t2[1])

    def find_closest_treasures(map, treasures):
        def manhattan_distance(t1, t2):
            return abs(t1[0] - t2[0]) + abs(t1[1] - t2[1])

        closest_treasures = {}

        for treasure, location in treasures.items():
            min_distance = float('inf')
            closest_treasure = None
            for other_treasure, other_location in treasures.items():
                if treasure != other_treasure:  # Ensure we're not comparing the same treasure
                    distance = manhattan_distance(location, other_location)
                    if distance < min_distance:
                        min_distance = distance
                        closest_treasure = other_treasure
            closest_treasures[treasure] = (closest_treasure, min_distance)

        return closest_treasures
    def h_test(self, node):
        new_state = State.from_hashable(node.state)
        treasures_on_ships = set()
        for ship in new_state.pirateships.keys():
            treasures_on_ships.union({treasure for treasure in new_state.on_ship[ship]})
        uncollected = set(self.treasures.keys()).difference(set(new_state.collected))  # works only on sets
        return float((20 * len(uncollected) - 10 * len(treasures_on_ships)) / len(new_state.pirateships))


    def manhattan_distances(self, map_array, base):
        rows = len(map_array)
        cols = len(map_array[0]) if rows > 0 else 0

        # Find the coordinates of 'B'
        b_row = int(base[0])
        b_col = int(base[1])

        # Pre-calculate row and column differences
        row_diffs = [abs(i - b_row) for i in range(rows)]
        col_diffs = [abs(j - b_col) for j in range(cols)]

        # Combine differences to calculate Manhattan distances
        distances = [[row_diffs[i] + col_diffs[j] for j in range(cols)] for i in range(rows)]

        return distances

    """ action providers """

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

    def pirates_marine_encounter(self, new_state: State, pirate: str, location: str):
        for marine in new_state.marineships.keys():
            marine_locations_array = new_state.marineships[marine][1]
            marine_index = new_state.marineships[marine][0]
            if tuple(marine_locations_array[marine_index]) == tuple(location):
                new_state.on_ship[pirate] = []

    def get_actions_for_ship(self, state, ship):
        actions = []
        row_index = state.pirateships.get(ship)[0]
        col_index = state.pirateships.get(ship)[1]
        location = [row_index, col_index]

        if self.maps[row_index][col_index] == 'B' and state.on_ship[ship]:  # if current location is at base it can deposit
            actions.append(("deposit_treasures", ship))

        ship_frame = self.possible_frame(row_index, col_index)
        is_marine_encounter_possible = False
        for marine in state.marineships.keys():
            marine_location = state.marineships[marine][1][state.marineships[marine][0]]
            if marine_location in ship_frame:
                is_marine_encounter_possible = True
        for step in ship_frame:
            if self.maps[step[0]][step[1]] == 'S' or self.maps[step[0]][step[1]] == 'B':
                actions.append(("sail", ship, (step[0], step[1])))  # not sure if necessary to string it

            else:  # if it is "I"
                treasure = self.get_treasure_from_island(state, ship, step)
                if (treasure is not None) and treasure not in state.on_ship[ship] and (len(state.on_ship[ship]) < 2):
                    actions.append(("collect_treasure", ship, treasure))
                    self.treasure_holders[treasure] = self.treasure_holders[treasure].union({ship})


        if is_marine_encounter_possible and state.on_ship[ship]:
            actions.append(("wait", ship))
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

    def get_treasure_from_island(self, state, ship, step: List[int]):
        for key in self.treasures.keys():
            if tuple(self.treasures[key]) == tuple(step) and key not in state.collected and key not in state.on_ship[ship]:
                return key
        return None

    def duplicate_state(self, state):
        return State(state.marineships, state.pirateships, state.collected, state.on_ship)

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""


def create_onepiece_problem(game):
    return OnePieceProblem(game)