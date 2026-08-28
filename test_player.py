# Test the "player.py" file

from models.player import Player


print("=" * 50)
print("Testing Player.py FILE ")
print("=" * 50)

#1.
print("Creating Players..")
Msd=Player("Ms Dhoni", "Wicket-Keeper")
Virat=Player("Virat Kohli", "Batsman")
Bumrah=Player("Jasprit Bumrah","Bowler")

print("Demo Players: \n")
print(Msd)
print(Virat)
print(Bumrah,"\n")

#2.
print("Add Batting Inning")
Msd.add_batting_innings(87,61,fours=6,sixes=3,dismissed=False)
Virat.add_batting_innings(45,34,fours=3,sixes=2,dismissed=True)

#3.
print("Adding Bowling Inning")
Bumrah.add_bowling_figures(36,46,3)

#4.
print("\nDisplay PLayer Career Stat\n")
Msd.display_summary()
Virat.display_summary()
Bumrah.display_summary()

#5.
print("=" * 50)
print("Player Class test Passed!!")
print("=" * 50)



