# Foosball-Tournament

## Instructions

In order to run this program, all that is needed are the **Tournament.py**, **Play.py**, and **Participants.txt** files. Specify the participants competing in **Participants.txt**. Each participant is separated by line. There can only be an even number of players. Then, run **Play.py**. This requires having Python installed. This can be run through either an IDE such as PyCharm, or from the command line prompt (preferable option). Navigate to the directory that these files exist in and type

> python3 Play.py

This will bring up an application to input the scores of the game. By default, there is no minimum amount of rounds that need to be played until there is an option to stop. However, this can be altered with the -r command. So one can type 

> python3 Play.py -r 7

to specify that a minimum of 7 rounds will be played. Then when enough rounds have been played, press "Finish" and the teams will be printed. These are what the program determines are the most fair teams. The ordering is that is given is based on the average of the two players. Ideally, the single elimination bracket would start here. As of now, I have not implemented a bracket manager. So for now, this part of the tournament will still have to be done manually. It is something I will get to doing at some point.

## Future Work

The next thing on my list is to implement an all-time rankings system. This will take the results of a tournament and incorporate them into an all-time leaderboard. Then future tournaments could determine pairings based on these all-time rankings (give the user the option to use this or not). An xlsx file will be created after a tournament to display the all-time rankings.

