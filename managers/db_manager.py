"""
db_manager.py - PostgreSQL Database Manager for CRICSCORER
Handles all database operations for players, teams, and player-team relations
"""

import os
import psycopg2
from psycopg2 import extras
from config import Database_config, DEBUG


class DatabaseManager:
    """
    PostgreSQL Database Manager with RealDictCursor
    (Equivalent to SQLite's row_factory)
    """
    
    def __init__(self):
        """Initialize database connection and create tables"""
        self.db_config = Database_config
        self.connection = None
        self.cursor = None
        self._create_database_if_not_exists()
        self._create_tables()

    def _get_connection(self):
        """
        Get or create database connection with RealDictCursor.
        
        RealDictCursor is the PostgreSQL equivalent of SQLite's row_factory.
        It makes rows return as dictionaries so you can access by column name.
        Example: row['name'] instead of row[0]
        """
        if self.connection is None:
            try:
                # ✅ PostgreSQL connection with RealDictCursor
                self.connection = psycopg2.connect(
                    host=self.db_config['host'],
                    port=self.db_config['port'],
                    database=self.db_config['database'],
                    user=self.db_config['user'],
                    password=self.db_config['password'],
                    cursor_factory=extras.RealDictCursor  # ✅ This replaces row_factory
                )
                self.connection.autocommit = False
                self.cursor = self.connection.cursor()
                
                if DEBUG:
                    print("✅ PostgreSQL connected successfully")
                    
            except psycopg2.Error as e:
                print(f"❌ PostgreSQL connection error: {e}")
                raise
        
        return self.connection

    def _create_database_if_not_exists(self):
        """Create database if it doesn't exist"""
        try:
            # Connect without RealDictCursor for admin operations
            conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database='postgres'
            )
            conn.autocommit = True
            cursor = conn.cursor()
            
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.db_config['database'],))
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute(f"CREATE DATABASE {self.db_config['database']}")
                print(f"✅ Database '{self.db_config['database']}' created")
            
            cursor.close()
            conn.close()
            
        except psycopg2.Error as e:
            print(f"⚠️ Database creation check warning: {e}")

    def _create_tables(self):
        """Create all necessary tables if they don't exist"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # TABLE 1: players
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id SERIAL PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    role TEXT DEFAULT 'Batsman',
                    matches INTEGER DEFAULT 0,
                    runs INTEGER DEFAULT 0,
                    balls_faced INTEGER DEFAULT 0,
                    fours INTEGER DEFAULT 0,
                    sixes INTEGER DEFAULT 0,
                    hundreds INTEGER DEFAULT 0,
                    fifties INTEGER DEFAULT 0,
                    highest_score INTEGER DEFAULT 0,
                    dismissals INTEGER DEFAULT 0,
                    balls_bowled INTEGER DEFAULT 0,
                    runs_conceded INTEGER DEFAULT 0,
                    wickets INTEGER DEFAULT 0,
                    five_wickets INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # TABLE 2: teams
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teams (
                    id SERIAL PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    captain TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # TABLE 3: team_players
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS team_players (
                    id SERIAL PRIMARY KEY,
                    player_id INTEGER REFERENCES players(id) ON DELETE CASCADE,
                    team_id INTEGER REFERENCES teams(id) ON DELETE CASCADE,
                    UNIQUE(player_id, team_id)
                )
            """)

            conn.commit()
            if DEBUG:
                print("✅ PostgreSQL tables created successfully")

        except psycopg2.Error as e:
            conn.rollback()
            print(f"❌ Table creation error: {e}")
            raise

    # ============================================================
    # PLAYER OPERATIONS
    # ============================================================

    def add_player(self, name, role="Batsman"):
        """Add a new player"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO players (name, role) VALUES (%s, %s) RETURNING id", (name, role))
            player_id = cursor.fetchone()['id']  # ✅ Access by column name
            conn.commit()
            if DEBUG:
                print(f"✅ Player '{name}' added (ID: {player_id})")
            return player_id
            
        except psycopg2.IntegrityError:
            conn.rollback()
            if DEBUG:
                print(f"ℹ️ Player '{name}' already exists")
            cursor.execute("SELECT id FROM players WHERE name = %s", (name,))
            result = cursor.fetchone()
            return result['id'] if result else None

    def get_player(self, name=None, player_id=None):
        """Get player by name or ID"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if name:
            cursor.execute("""
                SELECT *, 
                    CASE WHEN balls_faced > 0 THEN (runs * 100.0 / balls_faced) ELSE 0 END as strike_rate,
                    CASE WHEN matches > 0 THEN (runs * 1.0 / matches) ELSE 0 END as batting_avg,
                    CASE WHEN wickets > 0 THEN (runs_conceded * 1.0 / wickets) ELSE 0 END as bowling_avg,
                    (balls_bowled / 6) as overs_bowled
                FROM players WHERE name = %s
            """, (name,))
        elif player_id:
            cursor.execute("""
                SELECT *, 
                    CASE WHEN balls_faced > 0 THEN (runs * 100.0 / balls_faced) ELSE 0 END as strike_rate,
                    CASE WHEN matches > 0 THEN (runs * 1.0 / matches) ELSE 0 END as batting_avg,
                    CASE WHEN wickets > 0 THEN (runs_conceded * 1.0 / wickets) ELSE 0 END as bowling_avg,
                    (balls_bowled / 6) as overs_bowled
                FROM players WHERE id = %s
            """, (player_id,))
        else:
            return None

        result = cursor.fetchone()
        return dict(result) if result else None

    def get_player_id(self, name):
        """Get player ID by name"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM players WHERE name = %s", (name,))
        result = cursor.fetchone()
        return result['id'] if result else None

    def update_batting_stats(self, player_id, runs, balls, fours=0, sixes=0, dismissed=False):
        """Update batting statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT runs, balls_faced, fours, sixes, fifties, hundreds, 
                       highest_score, dismissals, matches 
                FROM players WHERE id = %s
            """, (player_id,))
            
            current = cursor.fetchone()
            if not current:
                if DEBUG:
                    print(f"⚠️ Player ID {player_id} not found")
                return

            # ✅ Access by column name with RealDictCursor
            new_runs = current['runs'] + runs
            new_balls = current['balls_faced'] + balls
            new_fours = current['fours'] + fours
            new_sixes = current['sixes'] + sixes
            new_hundreds = current['hundreds']
            new_fifties = current['fifties']
            new_highest = max(current['highest_score'], runs)
            new_dismissals = current['dismissals'] + (1 if dismissed else 0)
            new_matches = current['matches'] + 1

            if runs >= 100:
                new_hundreds += 1
                print("🎯 CENTURY!!")
            elif runs >= 50:
                new_fifties += 1
                print("🏏 HALF-CENTURY!!")

            cursor.execute("""
                UPDATE players 
                SET runs = %s, balls_faced = %s, fours = %s, sixes = %s,
                    hundreds = %s, fifties = %s, highest_score = %s,
                    dismissals = %s, matches = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (new_runs, new_balls, new_fours, new_sixes,
                  new_hundreds, new_fifties, new_highest,
                  new_dismissals, new_matches, player_id))

            conn.commit()
            if DEBUG:
                print(f"✅ Player (ID: {player_id}) batting stats updated")

        except psycopg2.Error as e:
            conn.rollback()
            print(f"❌ Error updating batting stats: {e}")

    def update_bowling_stats(self, player_id, balls, runs, wickets):
        """Update bowling statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT balls_bowled, runs_conceded, wickets, five_wickets 
                FROM players WHERE id = %s
            """, (player_id,))
            
            current = cursor.fetchone()
            if not current:
                if DEBUG:
                    print(f"⚠️ Player ID {player_id} not found")
                return

            # ✅ Access by column name
            new_balls = current['balls_bowled'] + balls
            new_runs = current['runs_conceded'] + runs
            new_wickets = current['wickets'] + wickets
            new_five_wickets = current['five_wickets']

            if wickets >= 5:
                new_five_wickets += 1
                print("🎯 FIVE-WICKET HAUL!!")

            cursor.execute("""
                UPDATE players 
                SET balls_bowled = %s, runs_conceded = %s, wickets = %s,
                    five_wickets = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (new_balls, new_runs, new_wickets, new_five_wickets, player_id))

            conn.commit()
            if DEBUG:
                print(f"✅ Player (ID: {player_id}) bowling stats updated")

        except psycopg2.Error as e:
            conn.rollback()
            print(f"❌ Error updating bowling stats: {e}")

    def get_all_players(self):
        """Get all players"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *, 
                CASE WHEN balls_faced > 0 THEN (runs * 100.0 / balls_faced) ELSE 0 END as strike_rate,
                (balls_bowled / 6) as overs_bowled
            FROM players ORDER BY name
        """)
        
        return [dict(row) for row in cursor.fetchall()]

    def get_top_batsmans(self, limit=10):
        """Get top batsmen"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, runs, matches,
                CASE WHEN balls_faced > 0 THEN (runs * 100.0 / balls_faced) ELSE 0 END as strike_rate,
                CASE WHEN matches > 0 THEN (runs * 1.0 / matches) ELSE 0 END as batting_avg
            FROM players
            WHERE runs > 0
            ORDER BY runs DESC
            LIMIT %s
        """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]

    def get_top_bowlers(self, limit=10):
        """Get top bowlers"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, wickets, runs_conceded, 
                (balls_bowled * 1.0 / 6) as overs_bowled,
                matches,
                CASE WHEN wickets > 0 THEN (runs_conceded * 1.0 / wickets) ELSE 0 END as bowling_avg
            FROM players
            WHERE wickets > 0
            ORDER BY wickets DESC
            LIMIT %s
        """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]

    # ============================================================
    # TEAM OPERATIONS
    # ============================================================

    def add_team(self, team_name, captain=None):
        """Add a new team"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO teams (name, captain) VALUES (%s, %s) RETURNING id", (team_name, captain))
            team_id = cursor.fetchone()['id']  # ✅ Access by column name
            conn.commit()
            if DEBUG:
                print(f"✅ Team '{team_name}' added (ID: {team_id})")
            return team_id
            
        except psycopg2.IntegrityError:
            conn.rollback()
            if DEBUG:
                print(f"ℹ️ Team '{team_name}' already exists")
            cursor.execute("SELECT id FROM teams WHERE name = %s", (team_name,))
            result = cursor.fetchone()
            return result['id'] if result else None

    def get_team(self, team_name=None, team_id=None):
        """Get team by name or ID"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if team_name:
            cursor.execute("SELECT * FROM teams WHERE name = %s", (team_name,))
        elif team_id:
            cursor.execute("SELECT * FROM teams WHERE id = %s", (team_id,))
        else:
            return None

        result = cursor.fetchone()
        return dict(result) if result else None

    def get_team_id(self, team_name):
        """Get team ID by name"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM teams WHERE name = %s", (team_name,))
        result = cursor.fetchone()
        return result['id'] if result else None

    def add_player_to_team(self, player_id, team_id):
        """Add player to team"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO team_players (player_id, team_id) VALUES (%s, %s)", (player_id, team_id))
            conn.commit()
            if DEBUG:
                print(f"✅ Player {player_id} added to Team {team_id}")
            return True
            
        except psycopg2.IntegrityError:
            conn.rollback()
            if DEBUG:
                print(f"ℹ️ Player {player_id} already exists in Team {team_id}")
            return False

    def get_team_players(self, team_id):
        """Get all players in a team"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.id, p.name, p.role, p.matches, p.runs, p.wickets 
            FROM players p
            JOIN team_players tp ON p.id = tp.player_id
            WHERE tp.team_id = %s
            ORDER BY p.name
        """, (team_id,))
        
        return [dict(row) for row in cursor.fetchall()]

    def remove_player_from_team(self, player_id, team_id):
        """Remove player from team"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM team_players WHERE player_id = %s AND team_id = %s", (player_id, team_id))
        conn.commit()
        if DEBUG:
            print(f"✅ Player {player_id} removed from Team {team_id}")

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
            if DEBUG:
                print("🔒 PostgreSQL connection closed")

    def __del__(self):
        """Cleanup on deletion"""
        self.close()