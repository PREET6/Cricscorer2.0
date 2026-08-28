"""
It control the full match flow from starting to end of the match
"""

import os
import config
import time
from datetime import datetime
from models.player import Player
from models.team import Team
from managers.db_manager import DatabaseManager

class MatchManager:
    #It is the main controller of the match from toss to result

    def __init__(self):

        self.match_id =None
        self.venue = None
        self.overs = None

        #Teams
        self.team1= None
        self.team2= None
        self.batting_team = None
        self.bowling_team= None

        #Current Inning
        self.current_innings = None

        #store match data fo rsaving
        self.match_data = {}

        self.db= DatabaseManager()

    def start_match(self):
        #Start a new match
        print("\n" + "="*50)
        print("Let's Start the Match".center(20))
        print("="*50)
        #Step 1,2,3
        self.get_match_details()
        self.create_teams()
        self.conduct_toss()

        #1st Innings
        print("\n" + "-"*50)
        print(f"{self.batting_team.name} Batting First")
        print("="*50)

        innings1= self.play_innings(self.batting_team,self.bowling_team,1)

        #2nd Innings
        print("\n" + "="*50)
        print(f"{self.bowling_team.name} Batting Now") #doubt
        print(f"TARGET:  {innings1['runs']+1} Runs")
        print("="*50)

        innings2= self.play_innings(self.bowling_team,self.batting_team,2,target=innings1['runs']+1)

        #Display Result
        self.display_result(innings1,innings2)

        #save match
        self.save_match(innings1,innings2)


    def get_match_details(self):
        #Get match details from user
        print("\n Match Details\n")
        self.venue=input("Enter match venue: ").strip()
        while not self.venue:
            print("Venue cannot be empty!")
            self.venue=input("Enter match venue: ").strip()

        #overs
        while True:
            try:
                self.overs= int(input("Enter number of Overs (1-20): "))
                if 1<=self.overs <=20:
                    break
                print("Please Enter Between 1 to 20")
            except ValueError:
                print("Please enter a valid number")

        self.match_id=config.get_match_id()

        print("-"*50)
        print(f"Match ID: {self.match_id}")
        print(f"Venue: {self.venue}")
        print(f"Overs: {self.overs}")


    def create_teams(self):
        # create team with option to load from DB
        print("-"*50)
        print("Create Teams")
        print("-"*50)

        #team1
        print("\n Team 1")
        self.team1= self._get_or_create_team('Team 1')

        #team2
        print("\n Team 2")
        self.team2= self._get_or_create_team("Team 2")

        print("-"*50)
        print("Teams Ready!!")
        self.team1.display_summary() #doubt
        self.team2.display_summary()



    def _get_or_create_team(self,team_label):
        '''Get team from DB or Create new one based in user input
           Select xi by user       
        '''
        while True:
            team_name= input(f"Enter {team_label} name: ").strip()
            while not team_name:
                print("Team name cannot be empty!!")
                team_name= input(f"Enter {team_label} name: ").strip()

            existing_team= self.db.get_team(team_name)

            if existing_team:
                print(f"\n Team {team_name} found in Database")
                return self._load_existing_team(team_name, team_label)
            else:
                print(f"Team {team_name} not found in Database")
                create_choice= input("Do you want to create new team (y/n): ").strip().lower()
                if create_choice == "y":
                    return self._create_new_team(team_name,team_label)
                else:
                    print("Try another name")
                    continue


    def _load_existing_team(self,team_name, team_label):
        # Load existing team from DB and let user select playing XI
        team_data= self.db.get_team(team_name)
        team_id= team_data['id']
        all_players_data= self.db.get_team_players(team_id)

        if not all_players_data:
            print(f"Team {team_name} has no players in Database")
            print("Let's Create a new team instead")
            return self._create_new_team(team_name, team_label)

        print(f"\n Found {len(all_players_data)} players in {team_name}")
        print("-"*40)

        for i, player_data in enumerate(all_players_data,1):
            role= player_data.get("role")
            print(f"  {i:2}. {player_data['name']} ({role})")
        print("-"*40)
        print(f"\n Select Playing XI for {team_label}")
        print("NOTE: Enter player numbers seperated by commas (eg: 1,3,4,5,..)")

        while True:
            try:
                sel=input("Enter numbers: ").strip()
                if not sel:
                    print("Please enter numbers for Playing XI")
                    continue

                #check user select exact 11 or not
                sel_indices = [int(x.strip()) for x in sel.split(",")]
                if len(sel_indices) != 11:
                    print(f"Please select exactly 11 players (you selected only {len(sel_indices)})")
                    continue

                #Check i fall player number are valid or not
                valid_range= all(1<= i <= len(all_players_data) for i in sel_indices)
                if not valid_range:
                    print(f"Please enter number between 1 and {len(all_players_data)}")
                    continue

                #check for duplication
                if len(set(sel_indices)) != len(sel_indices): #set() - convert to set which remove duplicate values by default
                    print("Duplicate number detected! Please check again")
                    continue
                break

            except ValueError:
                print("Please enter valid numbers seperated by commas!")

        #create team object
        team_obj = Team(team_name)

        #add selected player to the team
        for i in sel_indices:
            player_data=all_players_data[i-1] #to start with index 0

            #create Player obj from existing data
            player=Player(player_data["name"], player_data['role'], player_id=player_data["id"],db_manager=self.db)
            team_obj.add_player(player) #doubt

            #ask fo rcaptain
        print(f"\n Choose Captain for {team_name}")
        for i , player in enumerate(team_obj.players,1):
            print(f"  {i:2}. {player.name}")

        while True:
            try:
                choice = int(input("Enter Captain Number (1-11): "))
                if 1 <= choice <= len(team_obj.players):
                    team_obj.captain = team_obj.players[choice -1].name
                    print(f"{team_obj.captain} is the Captain")
                    break
                print("Invalid choice!!")
            except ValueError:
                print("Please enter a number!")
        return team_obj



    def _create_new_team(self,team_name, team_label):
        #Create a new input as per user input and save it in DB
        print("-"*40)
        print(f"Enter 11 Players for {team_name}")
        print("-"*40)

        team_obj = Team(team_name)

        for i in range(11):
            while True:
                player_name= input(f"Player {i+1} name: ").strip()

                if player_name:
                    break
                print("Enter the valid player name!!")

            print("Role: (1) Batsman   (2) Bowler   (3) All-rounder   (4) Wicket-Keeper")

            role_choice = input("Enter Role (1-4): ").strip()
            role_map = {
                "1": "Batsman",
                "2": "Bowler",
                "3": "All-rounder",
                "4": "Wicket-Keeper"
            }

            role = role_map.get(role_choice,"Batsman")

            #Create player and add it in db
            player = Player(player_name, role)
            team_obj.add_player(player)
            print(f" {player_name} ({role}) added to Database Successfully")

        #set captain
        print(f"\n Choose captain for {team_name}")
        for i, player in enumerate(team_obj.players,1):
            print(f"  {i:2}. {player.name}")

        while True:
            try:
                choice = int(input("Enter captain number (1-11): "))
                if 1<= choice <= len(team_obj.players):
                    team_obj.captain = team_obj.players[choice -1].name
                    print(f"{team_obj.captain} is the Captain")
                    break
                print("Invalid Choice")
            except ValueError:
                print("Please Enter a number!!")
        print(f"\n Team '{team_name}' created and saved to database!")
        return team_obj

    def conduct_toss(self):
        #Toss
        print("-"*40)
        print("           TOSS TME")
        print("-"*40)
        import random
        import time
        toss_winner= random.choice([self.team1, self.team2])
        time.sleep(2)
        print(f" \n {toss_winner.name} won the toss!")

        #get decision
        print(f"What do you want to do first? ")
        print("  (1) Bat First")
        print("  (2) Bowl First")

        while True:
            choice = int(input("Enter your Choice (1/2): ").strip())

            if choice == 1:
                self.batting_team = toss_winner
                if toss_winner == self.team1:
                    self.bowling_team = self.team2
                else:
                    self.bowling_team = self.team1
                print(f"{toss_winner.name} will BAT first")
                break
            elif choice == 2:
                self.bowling_team = toss_winner
                if toss_winner == self.team1:
                    self.batting_team = self.team2
                else:
                    self.batting_team = self.team1
                print(f"{toss_winner.name} will BOWL first")
                break
            else:
                print("Invalid Inpit!!")

    def play_innings(self,batting_team, bowling_team, innings_number, target=None):
        #Play on inning
        from config import VALID_RUNS, VALID_OUTCOMES

        #innitialize inning data
        innings = {
            'batting_team': batting_team.name,
            'bowling_team': bowling_team.name,
            'runs': 0,
            'wickets': 0,
            'balls': 0,
            'overs': 0,
            'target': target,
            'batsmen_stats': {},
            'bowlers_stats': {},
            'fall_of_wickets': [],
            'partnership_runs': 0,
            'partnership_balls':0
        }

        #Reset player current match stat
        for player in batting_team.players:
            player.for_new_match()
        for player in bowling_team.players:
            player.for_new_match()

        #innitialize stats dictionaries
        for player in batting_team.players:
            innings["batsmen_stats"][player.player_id] = {
                'name': player.name,
                'runs': 0,
                'balls': 0,
                'fours': 0,
                'sixes': 0,
                'out': False,
                'strike_rate': 0
            }

        for player in bowling_team.players:
            innings["bowlers_stats"][player.player_id]={
                "name":player.name,
                "balls":0,
                "runs":0,
                "wickets":0,
                "economy":0
            }

        #User select opening batsman
        print("\n" + "=" * 60)
        print(f" {batting_team.name} - Innings {innings_number}")
        print("=" * 60)
        
        print("\n Select OPENING BATSMEN:")
        print("-" * 40)

        for i,player in enumerate(batting_team.players,1):
            print(f"  {i:2}. {player.name} ({player.role})")
        print("-" * 40)

        #select first batsman
        while True:
            try:
                choice1 = int(input("\nSelect Batsman 1 (enter number): "))
                if 1 <= choice1 <= len(batting_team.players):
                    break
                print(f" Please enter between 1 and {len(batting_team.players)}")
            except ValueError:
                print(" Please enter a valid number!")
    
        # Select second batsman
        while True:
            try:
                choice2 = int(input("Select Batsman 2 (enter number): "))
                if 1 <= choice2 <= len(batting_team.players) and choice2 != choice1:
                    break
                elif choice2 == choice1:
                    print(" Cannot select the same player twice!")
                else:
                    print(f" Please enter between 1 and {len(batting_team.players)}")
            except ValueError:
                print(" Please enter a valid number!")

        current_batsman = batting_team.players[choice1-1]
        print(f"Striker Batsman: {current_batsman.name}")
        other_batsman = batting_team.players[choice2-1]
        print(f"Non-Striker Batsman: {other_batsman.name}")

        #create remaining batsman lineup
        batting_order=[]
        for player in batting_team.players:
            if player != current_batsman and player != other_batsman:
                batting_order.append(player)

        # User select onpening Bowler
        print("\n Select Opening Bowler")
        print("-"*40)
        for i,player in enumerate(bowling_team.players,1):
            print(f"  {i:2}. {player.name} ({player.role})")
        print("-"*40)

        #   Select Bowler
        while True:
            try:
                bowler_choice = int(input("\nSelect Bowler (enter number): "))
                if 1 <= bowler_choice <= len(bowling_team.players):
                    break
                print(f" Please enter between 1 and {len(bowling_team.players)}")
            except ValueError:
                print(" Please enter a valid number!")
        
        current_bowler = bowling_team.players[bowler_choice - 1]
        print(f"\n Opening Bowler: {current_bowler.name}")

        #store batting order for future batsmen
        next_batsman_index = 0

        #over tracking
        overs_completed = 0
        balls_in_over = 0
        max_balls = self.overs * 6

        #   MAIN MATCH LOOP 
        while innings["balls"]<max_balls and innings["wickets"]<10:

            if innings["balls"] >= max_balls:
                print(f"\n {self.overs} overs completed!")
                break
            #check if target raeached
            if target and innings["runs"] >= target:
                print("\n Target Reached")
                break
            #display current score
            self.display_score(innings, current_batsman, other_batsman, current_bowler, innings_number)

            #get ball input
            print(f"\n Ball {innings['balls']+1}/{max_balls}")
            ball_input = input("Enter Score (0 - 6, out, wide): ").strip().lower()

            result = self.process_ball(ball_input, batting_team, bowling_team, current_batsman, other_batsman, current_bowler, innings, innings_number)
            if result:
                runs_scored = result.get('runs',0)
                is_wicket = result.get('wicket', False)
                is_extra = result.get('extra', False)

                innings["runs"]+=runs_scored

                if is_wicket:
                    innings["wickets"] += 1
                    innings["fall_of_wickets"].append({
                        "wicket_number": innings["wickets"],
                        "batsman": current_batsman.name,
                        "runs": current_batsman.current_runs,
                        "balls": current_batsman.current_balls,
                        "score": f"{innings['runs']}/{innings['wickets']}"
                    })

                    print(f"\n {current_batsman.name} is OUT !!")

                    #  Reset partnership on wicket
                    innings["partnership_runs"] = 0
                    innings["partnership_balls"] = 0

                    #  Check if there are batsmen left
                    if len(batting_order) > 0:
                        print(f"\n Select Next Batsman")
                        print("-" * 40)

                        for i, player in enumerate(batting_order, 1):
                            print(f"  {i}. {player.name} ({player.role})")
                        print("-" * 40)

                        while True:
                            try:
                                next_choice = int(input("Select next batsman (enter number): "))
                                if 1 <= next_choice <= len(batting_order):
                                    #  Get the new batsman
                                    current_batsman = batting_order[next_choice - 1]
                                    
                                    #  Remove from batting order
                                    batting_order.pop(next_choice - 1)
                                    
                                    print(f"\n New Batsman: {current_batsman.name}")
                                    print(f" Non-Striker: {other_batsman.name}")
                                    break
                                print(f" Please enter between 1 and {len(batting_order)}")
                            except ValueError:
                                print("Please enter a valid number!")
                    else:
                        print("\n🏏 ALL OUT!")
                        break

                #Count ball
                if not is_extra:
                    innings["balls"]+=1
                    balls_in_over+=1

                    #Update Partnership
                    innings["partnership_runs"] += runs_scored
                    innings["partnership_balls"] += 1
                    innings["overs"] = overs_completed + (balls_in_over / 10)

                    if innings["balls"] >= max_balls:
                            print(f"\n {self.overs} overs completed!")
                            break

                    #ROTATE strike
                    if runs_scored % 2 == 1:
                        current_batsman, other_batsman = other_batsman, current_batsman


                #end of over
                if balls_in_over >= 6:
                    overs_completed += 1
                    balls_in_over = 0
                    #innings["overs"] = overs_completed + (balls_in_over / 10)

                    #Change strike after over
                    current_batsman, other_batsman = other_batsman, current_batsman

                    #user select next bowler
                    print(f"\n End Of Over {overs_completed}")
                    self.display_score(innings, current_batsman, other_batsman, current_bowler, innings_number)
                
                    print(f"\n Select NEXT BOWLER for Over {overs_completed + 1}:")
                    print("-" * 40)

                    for i,player in enumerate(bowling_team.players,1):
                        stats = innings["bowlers_stats"].get(player.player_id, {})
                        overs_bowled = stats.get('balls',0)/6
                        wickets= stats.get('wickets',0)
                        runs = stats.get('runs', 0)
                        print(f"  {i:2}. {player.name} ({overs_bowled:.1f} ov, {wickets} wkts, {runs} runs)")
                    print("-"*40)

                    #select bowler
                    while True:
                        try:
                            bowler_choice = int(input("Select Bowler (enter number): "))
                            if 1 <= bowler_choice <= len(bowling_team.players):
                                current_bowler = bowling_team.players[bowler_choice - 1]
                                print(f"\n New bowler: {current_bowler.name}")
                                break
                            print(f" Please enter between 1 and {len(bowling_team.players)}")
                        except ValueError:
                            print(" Please enter a valid number!")
                    time.sleep(1)
        print("\n" + "=" * 60)
        print(f" INNINGS {innings_number} COMPLETE")
        print("=" * 60)
        print(f"Score: {innings['runs']}/{innings['wickets']}")
        print(f"Overs: {innings['overs']:.1f}")
        
        return innings

    def process_ball(self, ball_input, batting_team, bowling_team, current_batsman, other_batsman, current_bowler, innings, innings_number):
        #Process a single ball with user input
        from config import VALID_RUNS, VALID_OUTCOMES
        result={}

        if ball_input in VALID_RUNS:
            runs = int(ball_input)
            result['runs'] = runs
            result['extra'] = False
            result['wicket'] = False

            #update batsman
            current_batsman.add_runs(runs, 1, fours=1 if runs==4 else 0, sixes=1 if runs == 6 else 0)

            #update innings stat
            innings['batsmen_stats'][current_batsman.player_id]['runs'] += runs
            innings['batsmen_stats'][current_batsman.player_id]['balls'] += 1
            if runs == 4:
                innings['batsmen_stats'][current_batsman.player_id]['fours'] += 1
                print("Its FOUR!")
            elif runs == 6:
                innings['batsmen_stats'][current_batsman.player_id]['sixes'] += 1
                print("Its SIX!")

            #UPDATE BOWLER
            current_bowler.add_bowling_ball(runs,0)
            innings['bowlers_stats'][current_bowler.player_id]['balls'] += 1
            innings['bowlers_stats'][current_bowler.player_id]['runs'] += runs

        #Check if Wicket
        elif ball_input == "out":
            result['wicket'] = True
            innings['bowlers_stats'][current_bowler.player_id]['balls'] += 1
            innings['bowlers_stats'][current_bowler.player_id]['wickets'] += 1
            current_batsman.mark_out()
            innings['batsmen_stats'][current_batsman.player_id]['out'] = True
            result["runs"] = 0
            result["extra"] = False
            print("Its OUT!")

        elif ball_input in ['wide','no ball']:
            result["runs"] =1
            result["extra"] = True
            result["wicket"] = False

            innings['bowlers_stats'][current_bowler.player_id]['runs'] += 1

            #innings['runs'] += 1 #addextra run
            print(f" {ball_input.upper()}! 1 extra run!")

        else:
            print("Invalid INPUT! please try again.")
            return None
        return result


    def display_score(self, innings, current_batsman, other_batsman, current_bowler, innings_number):
        #Display Current SCOREBOARD
        import os

        #clear screen for live scoreboard
        os.system("cls" if os.name == "nt" else "clear")

        print("="*70)
        print(f"{innings['batting_team']} - Innings {innings_number}".center(25))
        print("="*70)

        #current score
        print(f"\n SCORE: {innings['runs']}/{innings['wickets']}")
        print(f" Overs: {innings['overs']:.1f}")

        if innings.get('target'):
            target = innings['target']
            runs_needed= target - innings['runs']
            balls_remaining = (self.overs *6) - innings['balls']
            print(f"TARGET: {target} runs")
            print(f" NEED: {runs_needed} runs in {balls_remaining} balls")

            if balls_remaining >0:
                print(f"RR: {(runs_needed * 6) / balls_remaining:.2f}")
        print("-"*70)

        #current batsman
        print("\n CURRENT BATSMEN")
        if current_batsman:
            print(f"  {current_batsman.name}: {current_batsman.current_runs} ({current_batsman.current_balls})")
            print(f"     Fours: {current_batsman.current_fours}, Sixes: {current_batsman.current_sixes}")

        if other_batsman:
            print(f"  {other_batsman.name}: {other_batsman.current_runs} ({other_batsman.current_balls})")
            print(f"     Fours: {other_batsman.current_fours}, Sixes: {other_batsman.current_sixes}")

        #current bowler
        if current_bowler:
            bowler_stats = innings['bowlers_stats'].get(current_bowler.player_id,{})
            print(f"  {current_bowler.name}: {bowler_stats.get('balls',0)} balls, {bowler_stats.get('runs',0)} runs, {bowler_stats.get('wickets',0)} wickets")
        print("-"*70)

        #fall of wickets
        if innings.get("fall_of_wickets"):
            print("\n FALL OF WICKETS")
            for w in innings['fall_of_wickets'][-5:]: #show last 5 wkts
                print(f"  {w['wicket_number']}. {w['batsman']} - {w['score']}")

        print("-"*70)

        #Partnership
        print("\n CURRENT PARTNERSHIP")
        if 'partnership_runs' in innings and innings['partnership_runs'] is not None:
            # Use partnership from innings
            partnership_runs = innings.get('partnership_runs',0)
            partnership_balls = innings.get('partnership_balls',0)
        else:
            # Fallback to old method (for compatibility)
            if current_batsman and other_batsman:
                partnership_runs = current_batsman.current_runs + other_batsman.current_runs
                partnership_balls = current_batsman.current_balls + other_batsman.current_balls
            else:
                partnership_runs = 0
                partnership_balls = 0

        if partnership_balls == 0:
            print("  (New Partnership)")
        else:
            print(f"  {partnership_runs} runs off {partnership_balls} balls")
            if partnership_balls > 0:
                print(f"  Partnership Run Rate: {(partnership_runs * 6) / partnership_balls:.2f}")


    #DisplaY Match Result
    def display_result(self, innings1, innings2):
        print("\n" + "=" * 70)
        print("           MATCH RESULT")
        print("=" * 70)

        print(f"\n {innings1['batting_team']}: {innings1['runs']}/{innings1['wickets']} in {innings1['overs']:.1f} overs")
        print(f" {innings2['batting_team']}: {innings2['runs']}/{innings2['wickets']} in {innings2['overs']:.1f} overs")

        print("\n"+"-"*70)

        if innings1['runs'] > innings2['runs']:
            winner = innings1['batting_team']
            margin = innings1['runs'] - innings2['runs']
            print(f"  {winner} WON BY {margin} RUNS!")

        elif innings2['runs'] > innings1['runs']:
            winner = innings2['batting_team']
            margin = innings2['runs'] - innings1['runs']
            wickets_left = 10 - innings2['wickets']
            print(f"  {winner} WON BY {wickets_left} WICKETS!")

        else:
            print(" MATCH TIED!")

        print('-'*70)

        #store match data for saving
        self.match_data = {
            'team1': innings1['batting_team'],
            'team2': innings2['batting_team'],
            'team1_score': innings1['runs'],
            'team1_wickets': innings1['wickets'],
            'team1_overs': innings1['overs'],
            'team2_score': innings2['runs'],
            'team2_wickets': innings2['wickets'],
            'team2_overs': innings2['overs'],
            'winner': winner if innings1['runs'] != innings2['runs'] else None,
            'match_id': self.match_id,
            'venue': self.venue,
            'overs': self.overs
        }


    #Save match data
    def save_match(self, innings1, innings2):
        # save macth scor eto txt and update history txt file
        print("\n SAVING MATCH....")

        filename = config.get_match_filename()
        filepath = os.path.join(config.Matches_dir, filename)
        
        #save full scoreboard
        self.save_scorecard(innings1, innings2, filepath)

        #update history
        self.update_history(innings1, innings2)

        print(f" Match saved: {filepath}")


    ##Save complete match scorecard as txt
    def save_scorecard(self, innings1, innings2, filepath):
        with open(filepath,'w') as f:
            f.write("=" * 80 + "\n")
            f.write("                    CRICSCORER - MATCH SCORECARD\n".center(80))
            f.write("=" * 80 + "\n\n")
            f.write(f"Match ID: {self.match_id}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Venue: {self.venue}\n")
            f.write(f"Format: {self.overs} Overs\n\n")
            
            f.write("-" * 80 + "\n")
            f.write("TEAM LINEUPS\n")
            f.write("-" * 80 + "\n\n")

            #TEAM 1
            f.write(f"Team 1: {innings1['batting_team']}\n")
            f.write("PLayers: ")
            players = self.team1.get_players()
            f.write(",".join([p.name for p in players]) + "\n")
            f.write(f" Captain: {self.team1.captain}\n\n")

            #TEAM 2
            f.write(f"Team 2: {innings2['batting_team']}\n")
            f.write("Players: ")
            players = self.team2.get_players()
            f.write(", ".join([p.name for p in players]) + "\n")
            f.write(f"Captain: {self.team2.captain}\n\n")
            
            f.write("-" * 80 + "\n")
            f.write("INNINGS 1\n")
            f.write("-" * 80 + "\n\n")

            f.write(f"Batting: {innings1['batting_team']}\n")
            f.write(f"Score: {innings1['runs']}/{innings1['wickets']} in {innings1['overs']:.1f} overs\n\n")
            
            # Batsmen stats
            f.write("Batting Scorecard:\n")
            f.write("-" * 70 + "\n")
            f.write("Player              Runs  Balls  4s  6s  SR\n")
            f.write("-" * 70 + "\n")

            for player_id, stats in innings1['batsmen_stats'].items():
                name = stats['name'][:18]
                sr= (stats['runs'] * 100 / stats['balls']) if stats['balls']>0 else 0
                out = 'Out' if stats['out'] else 'Not Out'

                f.write(f"{name:<18} {stats['runs']:>4}  {stats['balls']:>4}   {stats['fours']:>2}   {stats['sixes']:>2}  {sr:>5.1f}  {out}\n")

                f.write("\n" + "-" * 80 + "\n")
            #BOWLING INNINGS 1
            f.write("\n")
            f.write("BOWLING SCORECARD:\n")
            f.write("-" * 70 + "\n")
            f.write("Bowler              Overs  Balls  Runs  Wickets  Economy\n")
            f.write("-" * 70 + "\n")

            for player_id, stats in innings1['bowlers_stats'].items():
                name = stats['name'][:18]
                balls = stats.get('balls', 0)
                overs = balls // 6
                remaining_balls = balls % 6
                overs_display = f"{overs}.{remaining_balls}"
                runs = stats.get('runs', 0)
                wickets = stats.get('wickets', 0)
                economy = (runs * 6 / balls) if balls > 0 else 0
                f.write(f"{name:<18}  {overs_display:>4}  {balls:>4}  {runs:>4}  {wickets:>6}  {economy:>7.2f}\n")

            f.write("\n")

            # Fall of Wickets
            if innings1.get('fall_of_wickets'):
                f.write("FALL OF WICKETS:\n")
                f.write("-" * 40 + "\n")
                for w in innings1['fall_of_wickets']:
                    f.write(f"  {w['wicket_number']}. {w['batsman']} - {w['score']}\n")
                f.write("\n")

            f.write("-" * 80 + "\n")

        # INNING  2
            f.write("INNINGS 2\n")
            f.write("-" * 80 + "\n\n")
            
            f.write(f"Batting: {innings2['batting_team']}\n")
            f.write(f"Score: {innings2['runs']}/{innings2['wickets']} in {innings2['overs']:.1f} overs\n\n")

            # Batsmen stats for innings 2
            f.write("Batting Scorecard:\n")
            f.write("-" * 70 + "\n")
            f.write("Player              Runs  Balls  4s  6s  SR\n")
            f.write("-" * 70 + "\n")
            
            for player_id, stats in innings2['batsmen_stats'].items():
                name = stats['name'][:18]
                sr = (stats['runs'] * 100 / stats['balls']) if stats['balls'] > 0 else 0
                out = "Out" if stats['out'] else "Not Out"
                f.write(f"{name:<18} {stats['runs']:>4}  {stats['balls']:>4}   {stats['fours']:>2}   {stats['sixes']:>2}  {sr:>5.1f}  {out}\n")
            
                f.write("\n" + "-" * 80 + "\n")
                # ✅ BOWLING STATS for INNINGS 2
            f.write("\n")
            f.write("BOWLING SCORECARD:\n")
            f.write("-" * 70 + "\n")
            f.write("Bowler              Overs  Balls  Runs  Wickets  Economy\n")
            f.write("-" * 70 + "\n")

            for player_id, stats in innings2['bowlers_stats'].items():
                name = stats['name'][:18]
                balls = stats.get('balls', 0)
                overs = balls // 6
                remaining_balls = balls % 6
                overs_display = f"{overs}.{remaining_balls}"
                runs = stats.get('runs', 0)
                wickets = stats.get('wickets', 0)
                economy = (runs * 6 / balls) if balls > 0 else 0
                f.write(f"{name:<18}  {overs_display:>4}  {balls:>4}  {runs:>4}  {wickets:>6}  {economy:>7.2f}\n")

            f.write("\n")

            # Fall of Wickets
            if innings2.get('fall_of_wickets'):
                f.write("FALL OF WICKETS:\n")
                f.write("-" * 40 + "\n")
                for w in innings2['fall_of_wickets']:
                    f.write(f"  {w['wicket_number']}. {w['batsman']} - {w['score']}\n")
                f.write("\n")

            f.write("-" * 80 + "\n")

            f.write("RESULT\n")
            f.write("-" * 80 + "\n\n")

            if self.match_data['winner']:
                winner = self.match_data['winner']
                if winner == innings1['batting_team']:
                    margin = innings1['runs'] - innings2['runs']
                    f.write(f"Winner: {winner}\n")
                    f.write(f"Margin: Won by {margin} runs\n")
                else:
                    wickets_left = 10 - innings2['wickets']
                    f.write(f"Winner: {winner}\n")
                    f.write(f"Margin: Won by {wickets_left} wickets\n")
            else:
                f.write("Match Tied\n")


            f.write("\n" + "=" * 80 + "\n")
            f.write("END OF SCORECARD\n".center(80))
            f.write("=" * 80 + "\n")


    #Update match history file
    def update_history(self, innings1, innings2):
        history_file= os.path.join(config.History_dir, 'match_history.txt')

        #Winner
        if innings1['runs'] > innings2['runs']:
            winner = innings1['batting_team']
            result = f"{winner} won by {innings1['runs'] - innings2['runs']} runs"
        elif innings2['runs'] > innings1['runs']:
            winner = innings2['batting_team']
            wickets_left = 10 - innings2['wickets']
            result = f"{winner} won by {wickets_left} wickets"
        else:
            winner = "Tie"
            result = "Match Tied"

        #format history file

        history_line = (f"{datetime.now().strftime('%Y-%m-%d')} | "
                        f"{innings1['batting_team']} vs {innings2['batting_team']} | "
                        f"{winner} | "
                        f"{innings1['runs']}/{innings1['wickets']} vs {innings2['runs']}/{innings2['wickets']} | "
                        f"{self.venue}\n"
                        )

        #append to history file
        with open(history_file, 'a') as f:
            f.write(history_line)

        print(f" Hostory File Updated: {history_file}")









    

