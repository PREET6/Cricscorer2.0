"""Represent the Cricket team with players and Captain
   Also uses DB to update and Display records
"""

from managers.db_manager import DatabaseManager

class Team:
    """
    Respresnt Team and player
    Add/Remove PLAYER from team
    Playing 11
    """
    def __init__(self,name,captain=None):    
        #Check if team exist or not if notthen add new team otherwise load team detail

        self.name=name
        self.captain=captain
        self.db=DatabaseManager()
        self.players=[]

        #check existence
        existing=self.db.get_team(name)
        if existing:
            self.team_id = existing["id"]
            self.captain = existing.get("Captain: ", captain)
            self._load_team_players()
        else:
            self.team_id = self.db.add_team(name,captain)
            

    def _load_team_players(self):
        #load players of a particular team

        from models.player import Player  #Import here to avoid circular import error

        player_data= self.db.get_team_players(self.team_id)

        self.players =[]

        for data in player_data:
            player = Player(data['name'],data['role'],player_id=data['id']) #create player obj for each player in a team
            self.players.append(player)


    def add_player(self,player):
        #Add a player to the team and internal team list

        if player in self.players:
            return False

        #Add to DB
        success= self.db.add_player_to_team(player.player_id, self.team_id)  

        if success:
            #ADD TO internal list
            self.players.append(player)
            return True
        return False

    def remove_player(self, player):
        #Remove player from a team

        if player not in self.players:
            return False

        success= self.db.remove_player_from_team(player.player_id,self.team_id)
        if success:
            self.players.remove(player)
            return True
        return False

    def get_players(self):
        #Display all players of a team
        return self.players

    def get_player_count(self):
        #Dsiplay number of players in a team
        return len(self.players)

    def get_captain(self):
        #Display name of captain
        return self.captain

    def set_captain(self,captain_name):
        #Set the name of captain
        # NOTE: This is set captain name in internally not in DB yet. 

        self.captain = captain_name

    def is_full(self):
        #check if team is full or not, Maximum Squad = 15 players

        return len(self.players)>=15

    def get_playing_11(self):
        #Display Playing 11 of a team   BUT for now I just take first 11 players in playing xi

        return self.players[:11]


    def display_team(self):
        #Display complete team line-up 
        print("-" * 40)
        print(f"Team Name: {self.name}")
        print(f"Captain: {self.captain}")
        if not self.players:
            print('There is no player in this team')
        print(f"Total PLayers: {len(self.players)}")
        print("-" * 40)

        for i,player in enumerate(self.players,1): #enumerate- automatically increment i = 1,2,3,.....
            captain_mark= " (C)" if player.name == self.captain else ""

         # {i:2}- i=1,2,3,.... sr. no and :2 use to make it alligned by saying it take 2 space wide
            print(f"  {i:2}. {player.name}{captain_mark}")
            print(f"      Role: {player.role}") #give 6 spaces to alligned exactly below player name
            print(f"      Runs: {player.runs} | Wickets: {player.wickets}")
            print() 

    def display_playing_11(self):
        #Display playing 11 of a team

        print("-" * 40)
        print(f"Team {self.name} - Playing XI")
        print("-" * 40)

        xi=self.get_playing_11()

        for i,player in enumerate(xi,1):
            captain_mark= " (C)" if player.name == self.captain else ""
            print(f"  {i:2}. {player.name}{captain_mark}")


    def display_summary(self):
        """Display team summary"""
        print(f"\nTeam: {self.name}")
        print(f"   Captain: {self.captain}")
        print(f"   Players: {len(self.players)}/15")

        if self.players:
            total_runs= sum(p.runs for p in self.players)
            total_wickets= sum(p.wickets for p in self.players)
            print(f"Total Runs: {total_runs}")
            print(f"Total Wickets: {total_wickets}")


    def __str__(self):
        """Simple string representation"""
        return f"{self.name} (Captain: {self.captain}, Players: {len(self.players)})"
    
    def __repr__(self):
        """Detailed representation for debugging"""
        return f"Team(name='{self.name}', captain='{self.captain}', players={len(self.players)})"
    

        