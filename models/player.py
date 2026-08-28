"""
IT GIVES PLAYER STATISTICS THAT REPRESENT DURING SCORING AND IN DATABASE
UPDATE, DELETE, DISPLAY PLAYER STATS
"""

from managers.db_manager import DatabaseManager

class Player:
    def __init__(self,name,role="Ratsman",player_id=None,db_manager = None):
        #Check player existing or not if not then create new player

        self.name=name
        self.role=role
        if db_manager:
            self.db = db_manager
            self.own_db = False
        else:
            self.db = DatabaseManager()
            self.own_db = True

        #Check player exist or not
        existing=self.db.get_player(name)
        if existing:
            #display detail of player 
            self.player_id = existing["id"]
            self._load_stats(existing)
            #print(f"Loading Player {name} (ID: {self.player_id})")
        else:
            #create new player
            self.player_id=self.db.add_player(name,role)
            self._reset_stats()
            #print(f"Add new player {name} (ID: {self.player_id})")

    def _reset_stats(self):
        """Reset all statistics to zero for a new player."""
        # Career stats
        self.matches = 0
        self.runs = 0
        self.balls_faced = 0
        self.fours = 0
        self.sixes = 0
        self.hundreds = 0
        self.fifties = 0
        self.highest_score = 0
        self.dismissals = 0
        self.balls_bowled = 0
        self.runs_conceded = 0
        self.wickets = 0
        self.five_wickets = 0
        
        # Current match stats (reset each match)
        self.current_runs = 0
        self.current_balls = 0
        self.current_fours = 0
        self.current_sixes = 0
        self.current_is_out = False
        self.current_bowling_balls = 0
        self.current_bowling_runs = 0
        self.current_bowling_wickets = 0

    def _load_stats(self,data):
        """Load stats from database into the object."""
        self.matches = data.get('matches', 0)
        self.runs = data.get('runs', 0)
        self.balls_faced = data.get('balls_faced', 0)
        self.fours = data.get('fours', 0)
        self.sixes = data.get('sixes', 0)
        self.hundreds = data.get('hundreds', 0)
        self.fifties = data.get('fifties', 0)
        self.highest_score = data.get('highest_score', 0)
        self.dismissals = data.get('dismissals', 0)
        self.balls_bowled = data.get('balls_bowled', 0)
        self.runs_conceded = data.get('runs_conceded', 0)
        self.wickets = data.get('wickets', 0)
        self.five_wickets = data.get('five_wickets', 0)

    #-------Batting-------
    def add_batting_innings(self, runs, balls, fours=0,sixes=0,dismissed=False):
        #add batting innings data to databse and display updated data after match
        #this is call after match to update the data of match

        self.db.update_batting_stats(self.player_id,runs,balls,fours,sixes,dismissed)

        #reload the data to update / sync db regulary during the scoring
        updated_data=self.db.get_player(player_id=self.player_id)
        if updated_data:
            self._load_stats(updated_data)

    def get_batting_average(self):
        if self.dismissals==0:
            return 0.00
        return round(self.runs/self.dismissals,2)

    def get_strike_rate(self):
        if self.balls_faced==0:
            return 0.00
        return round((self.runs/self.balls_faced)*100,2)

    #---------Bowling------
    def add_bowling_figures(self,balls,runs,wickets):
        #add bowling innings data to db and display it
        #this also call after match completion

        self.db.update_bowling_stats(self.player_id,balls,runs,wickets)

        #reload the data to sync during scoring
        updated_data=self.db.get_player(player_id=self.player_id)
        if updated_data:
            self._load_stats(updated_data)

    def get_economy_rate(self):
        if self.balls_bowled==0:
            return 0.00
        over=self.balls_bowled/6
        return round(self.runs_conceded/over,2)

    def get_bowling_average(self):
        if self.wickets==0:
            return 0.00
        return round(self.runs_conceded/self.wickets,2)


    def for_new_match(self):
        #Reset all the current values to 0 to store data/record of new match 
        #it call at start of the match scoring

        self.current_runs = 0
        self.current_balls = 0
        self.current_fours = 0
        self.current_sixes = 0
        self.current_is_out = False
        self.current_bowling_balls = 0
        self.current_bowling_runs = 0
        self.current_bowling_wickets = 0

    def add_runs(self, runs, balls=1, fours=0 ,sixes=0):
        #This is add runs in scorboard per ball in current match stat, if extra then bowl count to 0

        self.current_runs+=runs
        self.current_balls+=balls
        self.current_fours+=fours
        self.current_sixes+=sixes

    def add_bowling_ball(self,runs,wickets=0):
        #same as add_run but this is for bowling 

        self.current_bowling_balls+=1
        self.current_bowling_runs+=runs
        self.current_bowling_wickets+=wickets

    def mark_out(self):
        #it call if batsman out
        self.current_is_out=True

    def get_current_summary(self):
        #Display Current MATCH STAT of player
        return {
            'runs': self.current_runs,
            'balls': self.current_balls,
            'fours': self.current_fours,
            'sixes': self.current_sixes,
            'is_out': self.current_is_out,
            'strike_rate': self.get_current_strike_rate(),
            'bowling_balls': self.current_bowling_balls,
            'bowling_runs': self.current_bowling_runs,
            'bowling_wickets': self.current_bowling_wickets,
        }
    
    def get_current_strike_rate(self):
        #Calculate current match strike rate
        if self.current_balls==0:
            return 0.00
        return round((self.current_runs/self.current_balls)*100,2)

    def display_summary(self):
        """Display career summary in a readable format."""
        print(f"\n  {self.name} ({self.role})")
        print("-" * 40)
        print(f"  Matches:   {self.matches}")
        print(f"  Runs:      {self.runs}")
        print(f"  Avg:       {self.get_batting_average()}")
        print(f"  SR:        {self.get_strike_rate()}")
        print(f"  Hundreds:  {self.hundreds}")
        print(f"  Fifties:   {self.fifties}")
        print(f"  HS:        {self.highest_score}")
        print(f"  Fours:     {self.fours}")
        print(f"  Sixes:     {self.sixes}")
        print("-" * 40)
        print(f"  Wickets:   {self.wickets}")
        print(f"  Economy:   {self.get_economy_rate()}")
        print(f"  Bowling Avg: {self.get_bowling_average()}")
        print(f"  5-Wkts:    {self.five_wickets}")

    def __str__(self):
        #Simple string to display player
        return f"{self.name} ({self.role})"
    def __repr__(self):
        #Respresnt deatils info of player for debugging
        return f"Player(Name: {self.name}, Role: {self.role},  ID: {self.player_id})"
    def __del__(self):
        """Clean up only if we own the connection"""
        if hasattr(self, 'own_db') and self.own_db:
            self.db.close()