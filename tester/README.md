# Tournament Schedule Unit Tester

## Prebuild
Before running this, set the url to your instance of the tournament creator in test.py

## Build and run
```
docker build -t tester .; docker run -it --rm --name tester tester
```

## Simulate Failure

- You can simulate reating duplicate partnerships by swapping these 2 lines in the tournament creator's script.py and redeploying it
```
                if sorted_pair not in used_pairs and all(player not in round_players for player in sorted_pair):
             #  You can replace this line above with the line below to generate duplicate pairs for testing the tester
             #   if all(player not in round_players for player in sorted_pair):
```

- You can create an incorrect partner in the player's schedule by adding an ampersand and a number to one of the names in the game_of_thrones name list and rebuilding/redeploying the tournament creator

```
Arya Stark & 2
```

note - for this reason, you should never have ampersands in any name dictionaries
