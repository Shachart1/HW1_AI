import search
import ex1

test_game = {
            "map": [
                ['S', 'S', 'I', 'S'],
                ['S', 'S', 'S', 'S'],
                ['B', 'S', 'S', 'S'],
                ['S', 'S', 'S', 'S']
            ],
            "pirate_ship": {"pirate_ship_1": (2, 0)},
            "treasures": {'treasure_1': (0, 2)},
            "marine_ships": {'marine_1': [(1, 1), (3, 0), (2, 2), (2, 1)]}
        }

def main():
    onePiece = ex1.create_onepiece_problem(test_game)
    print("HELLO")
    actions = onePiece.actions(onePiece.root.state)
    print(actions)
    print(actions[1])
    onePiece.root.state.on_ship["pirate_ship_1"].add("treasure_1")
    print(onePiece.result(onePiece.root.state, actions[1]))

    str_of_state = onePiece.root.state.to_hashable()
    print(str_of_state)
    print(ex1.State.from_hashable(str_of_state))

if __name__ == '__main__':
    main()
