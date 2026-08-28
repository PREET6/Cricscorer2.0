"""
It is a foundation file for all files. User should run this file to run a program.
"""

import os
import sys
import time


#It take the current path of main file
Program_path=os.path.dirname(os.path.abspath(__file__))
#it store this path in python folder path to search for this program packages and file/folders (0=add at very first index)
# This helps Python find all our modules
sys.path.insert(0,Program_path)

#now I can add config in this
import config
from managers.db_manager import DatabaseManager
from managers.match_manager import MatchManager

def clear_screen():
    #It clear terminal before code run. nt= for window and clear= for linux/mac
    os.system("cls"if os.name=="nt" else "clear")

def print_welcome():
    print("="*80)
    print("Welcome to the Cricket Scoring Application".center(60))
    print(f"{config.company}".center(60)+"\n")
    print(f"{config.Developer} Presents ".center(60) + "\n")
    print(f"{config.Project_name}".center(60))
    print(f"{config.Version}".center(60))
    print("="*80)
    print("\nDear User, Your data will be stored to...")
    print(f"• Matches: {config.Matches_dir}")
    print(f"• History: {config.History_dir}")
    print(f"• Database: Postgres {config.Database_config['database']}")
    print("-"*40)

def initialize_database():
    #It check SQlite db and it create tables and all necessary things for Cricscorer
    print("Initializing Database..")
    db_manager=DatabaseManager()
    try:
        print("Database is initiated successfully")
        return db_manager
    except Exception as e:
        print(f"Error {e}")
        return None

def main():
    #Main game function and it eventually contain the full game loop
    
    clear_screen()
    print_welcome()
    print("Loading Application...")
    time.sleep(1)
    print("Let's Initialize the Match...")
    time.sleep(1)
    db=initialize_database()
    if db is None:
        print("Database is not initialized. Please check the log file for more detail.")
        return
    
    print("\n Starting Match...")
    time.sleep(1)


    #Start the match 
    match_manager = MatchManager()
    match_manager.start_match()

    #close db connection'
    db.close()
    print("\n" + "=" * 80)
    print("Thank you for playing!".center(80))
    print("=" * 80)

    

# This is the entry point
# The code below only runs when you execute THIS file directly
# It does NOT run when this file is imported by another file
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram Closed due to Interrupt")
    except Exception as e:
        print(f"\nAn {e} error has occured ")
        print("Please Check log file for more detail")


