import search
import ex1

test_game = {
            "map": [
                ['S', 'S', 'I', 'S'],
                ['S', 'S', 'S', 'S'],
                ['B', 'S', 'S', 'S'],
                ['S', 'S', 'S', 'S']
            ],
            "pirate_ships": {"pirate_ship_1": (2, 0), "pirate_ship_2": (2, 0), "pirate_ship_3": (2, 0)},
            "treasures": {'treasure_1': (0, 2)},
            "marine_ships": {'marine_1': [(3, 3)]}
        }

def main():
    onePiece = ex1.create_onepiece_problem(test_game)
    print("HELLO")
    actions = onePiece.actions(onePiece.root.state)
    print(actions)
    print(actions[1])
    print(search.astar_search(onePiece))

if __name__ == '__main__':
    main()
