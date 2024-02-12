import search
import ex1t

test_game = {
            "map": [
                ['S', 'S', 'I', 'S'],
                ['S', 'S', 'S', 'S'],
                ['B', 'S', 'S', 'S'],
                ['S', 'S', 'S', 'S']
            ],
            "pirate_ships": {"pirate_ship_1": (2, 0)},
            "treasures": {'treasure_1': (0, 2)},
            "marine_ships": {'marine_1': [(3, 3), (3, 4)]}
        }

def main():
    onePiece = ex1t.create_onepiece_problem(test_game)
    state = onePiece.hashable_to_state(onePiece.initial)
    # state["collected_treasures"]["pirate_ship_1"] = "treasure_1"
    print(state)
    actions = onePiece.actions(onePiece.state_to_hashable(state))
    print(actions[0])
    new_state = onePiece.result(onePiece.state_to_hashable(state), actions[0])
    print(onePiece.result(onePiece.state_to_hashable(new_state), actions[0]))
    # print(search.astar_search(onePiece))

if __name__ == '__main__':
    main()
