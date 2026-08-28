"""
test_team.py - Test the Team class
"""

from models.player import Player
from models.team import Team

print("=" * 50)
print("TESTING TEAM CLASS")
print("=" * 50)

# 1. Create players
print("\n1️ Creating players...")
Msd = Player("MS Dhoni", "Wicket-Keeper")
Virat = Player("Virat Kohli", "Batsman")
Rohit = Player("Rohit Sharma", "Batsman")
Bumrah = Player("Jasprit Bumrah", "Bowler")
Pandya = Player("Hardik Pandya", "All-rounder")
Rahul = Player("KL Rahul", "Batsman")
Jadeja = Player("Ravindra Jadeja", "All-rounder")
Shami = Player("Mohammed Shami", "Bowler")
Ashwin = Player("R Ashwin", "Bowler")
Pant = Player("Rishabh Pant", "Wicket-Keeper")
Gill = Player("Shubman Gill", "Batsman")
Surya = Player("Suryakumar Yadav", "Batsman")
Arshdeep = Player("Arshdeep Singh", "Bowler")
Ishan = Player("Ishan Kishan", "Batsman")
Shreyas = Player("Shreyas Iyer", "Batsman")


print(f"    Created {len([Msd, Virat, Rohit, Bumrah, Pandya, Rahul, Jadeja, Shami, Ashwin, Pant, Gill,Surya, Arshdeep, Ishan, Shreyas])} players")

# 2. Create team
print("\n2️ Creating team...")
india = Team("Team India", "MS Dhoni")
print(f"    {india}")

# 3. Add players to team
print("\n3️Adding players to team...")
players = [Msd, Virat, Rohit, Bumrah, Pandya, Rahul, Jadeja, Shami, Ashwin, Pant, Gill,Surya, Arshdeep, Ishan, Shreyas]

for player in players:
    india.add_player(player)
    print(f"   Added {player.name}")

# 4. Display team
print("\n4️ Team lineup:")
india.display_team()

# 5. Display summary
print("\n5️ Team summary:")
india.display_summary()

# 6. Test team limits
print("\n6️ Testing team limits:")
print(f"   Is team full? {india.is_full()}")

# Try to add one more player
Hrashit = Player("Harshit Rana", "Bowler")
if india.is_full():
    print("   Team already has 15 players!")
else:
    india.add_player(Hrashit)
    

print("\n" + "=" * 50)
print(" Team class tests passed!")
print("=" * 50)