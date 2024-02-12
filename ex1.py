import search
import random
from typing import List
from itertools import product
from collections import deque

ids = ["", ""]


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
            "marineships": str(self.marineships),
            "pirateships": str(self.pirateships),
            "collected": str(self.collected),
            "on_ship": str(self.on_ship),
        }
        return str(state_dict)

    @classmethod
    def from_hashable(cls, hashable_string: str):
        state_dictionary = eval(hashable_string)
        marineships = dict(sorted(eval(state_dictionary["marineships"]).items()))
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
        marins = {key: (0, initial.get("marine_ships").get(key)) for key in initial.get("marine_ships").keys()}
        pirates = initial.get(
            "pirate_ships")  # TODO - VERY IMPORTANT CHECK WHAT THIS KEY IS!!!!! IT IS NOT CONSISTENT IN THEIR TESTS!!!!!!!
        self.root = search.Node(State(marins, pirates).to_hashable())
        self.columns = len(self.maps[0])
        self.rows = len(self.maps)
        self.base = initial.get("pirate_ships")[list(pirates.keys())[
            0]]  # TODO - VERY IMPORTANT CHECK WHAT THIS KEY IS!!!!! IT IS NOT CONSISTENT IN THEIR TESTS!!!!!!!
        self.treasure_holders = {key: set() for key in self.treasures.keys()}
        self.distances = self.manhattan_distances(self.maps, self.base)
        island_location_frame = [(treasure,
                                  self.min_manhattan_around(self.distances,
                                                            int(self.treasures[treasure][0]),
                                                            int(self.treasures[treasure][1])))
                                 for treasure in self.treasures.keys()]
        self.island_location_frame_dict = {key: value for (key, value) in island_location_frame}

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
                new_state.pirateships[action[1]] = action[2]
                new_state.pirateships = dict(sorted(new_state.pirateships.items()))
                self.pirates_marine_encounter(new_state, action[1], action[2])
            elif action[0] == "collect_treasure":
                new_state.on_ship[action[1]].append(action[2])
                new_state.on_ship = dict(sorted(
                    new_state.on_ship.items()))  # first sort by key values so ship_1 will be before ship_2 for example
                for ship in new_state.on_ship:
                    new_state.on_ship[ship] = sorted(new_state.on_ship[ship])  # sort each list of treasures inside
                self.treasure_holders[action[2]] = self.treasure_holders[action[2]].union({action[1]})
            elif action[0] == "deposit_treasures":
                # here i wanted to add the other dict with who owns the ship
                for treasure in new_state.on_ship[action[1]]:
                    if treasure not in new_state.collected:
                        new_state.collected.append(treasure)
                        new_state.collected = sorted(new_state.collected)
                    self.treasure_holders[treasure] = self.treasure_holders[treasure].difference({action[1]})
                new_state.on_ship[action[1]] = []  # now the pirateship is empty

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
        treasures_on_ships = set()

        for ship in new_state.on_ship.keys():
            treasures_on_ships = treasures_on_ships.union(new_state.on_ship[ship])
        treasures_on_islands_count = len(self.treasures.keys()) - len(treasures_on_ships.union(new_state.collected))
        return max(self.h_1(node),
                   self.h_2(node)/(len(treasures_on_ships) + 1),
                   self.h_bfs(node) / (treasures_on_islands_count + 1))

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

    def min_manhattan_around(self, distances, row, col):
        frame = self.possible_frame(row, col)
        frame_distances = []
        if frame:
            for element in frame:
                frame_distances.append(distances[element[0]][element[1]])
        else:
            frame_distances = [float('inf')]
        return min(frame_distances)

    def h_bfs(self, node):
        new_state = State.from_hashable(node.state)
        sum = 0
        for treasure in self.treasures.keys():
            for ship in new_state.pirateships.keys():
                if treasure in new_state.on_ship[ship]:
                    if treasure == "treasure_2":
                        test = 5        # TO TEST OUT THE BFS
                    sum += self.bfs_distance_to_base(new_state, ship)
        return float(sum)/len(new_state.pirateships.keys())

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

        # Calculate Manhattan distances for each cell from 'B'
        distances = [[abs(i - b_row) + abs(j - b_col) for j in range(cols)] for i in range(rows)]

        return distances

    # def manhattan_distance_blocked(self, map, start, blocked):
    #     rows, cols = len(map), len(map[0])
    #     distances = [[float('inf')] * cols for _ in range(rows)]
    #     visited = [[False] * cols for _ in range(rows)]
    #
    #     queue = [(start[0], start[1], 0)]  # (row, col, distance)
    #     distances[start[0]][start[1]] = 0
    #
    #     while queue:
    #         current_row, current_col, current_distance = queue.pop(0)
    #         visited[current_row][current_col] = True
    #
    #         neighbors = [
    #             (current_row - 1, current_col),
    #             (current_row + 1, current_col),
    #             (current_row, current_col - 1),
    #             (current_row, current_col + 1),
    #         ]
    #
    #         for neighbor_row, neighbor_col in neighbors:
    #             if 0 <= neighbor_row < rows and 0 <= neighbor_col < cols and not visited[neighbor_row][neighbor_col] and \
    #                     map[neighbor_row][neighbor_col] != blocked:
    #                 new_distance = current_distance + 1
    #                 if new_distance < distances[neighbor_row][neighbor_col]:
    #                     distances[neighbor_row][neighbor_col] = new_distance
    #                     queue.append((neighbor_row, neighbor_col, new_distance))
    #
    #     return distances

    def bfs_distance_to_base(self, new_state: State, ship: str):
        ship_location = new_state.pirateships[ship]
        # Create initial node
        initial_node = search.Node(parent=None, state=ship_location)

        # Initialize queue for BFS
        queue = deque([initial_node])

        # Set to keep track of visited states
        visited = set()

        # Perform BFS - from here on 'state' refers to location in the map...
        while queue:
            # Get the front node from the queue
            current_node = queue.popleft()
            current_state = current_node.state

            # Check if goal state is reached
            if self.maps[current_state[0]][current_state[1]] == 'B':
                return current_node.depth  # Return the distance

            # Mark current state as visited
            visited.add(tuple(current_state))

            # Generate possible next states
            next_states = [state
                           for state in self.possible_frame(current_state[0], current_state[1])
                           if self.maps[state[0]][state[1]] != 'I']

            # Create child nodes for next states
            for state in next_states:
                if tuple(state) not in visited:
                    child_node = search.Node(state=state, parent=current_node)
                    queue.append(child_node)

        # If goal state is not reachable
        return float("inf")

        def generate_next_states(current_state):
            # Example function to generate next possible states
            next_states = []
            # Add your logic to generate next states here
            return next_states

        # Example usage:
        initial_state = [1, 2, 3]
        goal_state = [4, 5, 6]
        goal_node = bfs(initial_state, goal_state)

        if goal_node:
            # Print the path from initial state to goal state
            path = []
            while goal_node:
                path.append(goal_node.state)
                goal_node = goal_node.parent
            path.reverse()
            print("Path from initial state to goal state:", path)
        else:
            print("Goal state is not reachable from the initial state.")


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

    def marine_pirates_encounter(self, new_state: State, location: str):
        for pirate in new_state.pirateships.keys():
            if new_state.pirateships[pirate] == location:
                new_state.on_ship[pirate] = []

    def pirates_marine_encounter(self, new_state: State, pirate: str, location: str):
        for marine in new_state.marineships.keys():
            marine_locations_array = new_state.marineships[marine][1]
            marine_index = new_state.marineships[marine][0]
            if marine_locations_array[marine_index] == location:
                new_state.on_ship[pirate] = []

    def get_actions_for_ship(self, state, ship):
        actions = []
        actions.append(("wait", ship))
        row_index = state.pirateships.get(ship)[0]
        col_index = state.pirateships.get(ship)[1]
        location = [row_index, col_index]

        if self.maps[row_index][col_index] == 'B':  # if current location is at base it can deposit
            actions.append(("deposit_treasures", ship))

        ship_frame = self.possible_frame(row_index, col_index)
        for step in ship_frame:
            if self.maps[step[0]][step[1]] == 'S' or self.maps[step[0]][step[1]] == 'B':
                actions.append(("sail", ship, (step[0], step[1])))  # not sure if necessary to string it

            else:  # if it is "I"
                treasure = self.get_treasure_from_island(state, ship, step)
                if (treasure is not None) and treasure not in state.on_ship[ship] and (len(state.on_ship[ship]) < 2):
                    actions.append(("collect_treasure", ship, treasure))
                    self.treasure_holders[treasure] = self.treasure_holders[treasure].union({ship})

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
            if self.treasures[key] == tuple(step) and key not in state.collected and key not in state.on_ship[ship]:
                return key
        return None

    def duplicate_state(self, state):
        return State(state.marineships, state.pirateships, state.collected, state.on_ship)

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""


def create_onepiece_problem(game):
    return OnePieceProblem(game)
