"""
config.py - Configuration file for CRICSCORER
This file holds ALL paths and settings for the application 

"""
import os
from datetime import datetime

#Application Details
Project_name="Cricscorer2.0"
Version= "v2.0"
Developer="PREET CHAUDHARY"
company="JiviOn (A demo Company)"

DEBUG = False

#Get the location of "config.py" by __file__
Base_dir=os.path.dirname(os.path.abspath(__file__))

#Now using "Base_dir" path we make new files/folders if ir not made early
#This help program to run on any computer by automatically making folders withour hardcode address
Data_dir=os.path.join(Base_dir,"data")
Matches_dir=os.path.join(Data_dir,"matches")
History_dir=os.path.join(Data_dir,"history")
Backup_dir=os.path.join(Data_dir,"backup")
Players_dir=os.path.join(Data_dir,"players")

Log_dir=os.path.join(Base_dir,"logs")
#Postgres DATABASE FOR PLAYER RECORDS

Database_config = {
    'host':'localhost',
    'port':5432,
    'database':'cricscorer',
    'user':'postgres',
    'password':'admin123'
}

#Database_file = os.path.join(Data_dir, "cricscorer.db")


#Make Function to  create all folders
def ensure_directories():
    directories=[Data_dir,Matches_dir,History_dir,Backup_dir,Players_dir,Log_dir]

    #for loop to call each variable and make that folder if not exist
    for dir in directories:
        if not os.path.exists(dir):
            os.makedirs(dir,exist_ok=True)#exist_ok=True use to prevent error if file already exist
            print(f"Folder Created: {dir}")

    #create file "match_history.txt" in history folder to store matches as sinle line
    History_file=os.path.join(History_dir,"match_history.txt")
    if not os.path.exists(History_file):
        with open(History_file,"w") as f:
            f.write("="*40 +"\n")
            f.write("CRICSCORER2.0 MATCH HISTORIES \n")
            f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*40 + "\n\n")
            f.write("DATE | TEAM 1 | TEAM 2 | WINNER | SCORE | VENUE\n")
            f.write("-" *80 + "\n")
        print(f"Created History file: {History_file}")
    else:
        print(f" History file already exists: {History_file}")

    print(f"Using Postgres database")

#RUN "ensure directories" to create the above folders/file first before run any code
print("setting up Cricscorer2.0 directories.....")
ensure_directories()
print("Directories setup Completed succesfully")

#Constant Variables
VALID_RUNS = ['0', '1', '2', '3', '4', '5', '6']
VALID_OUTCOMES = ['out', 'wide', 'no-ball', 'bye', 'leg-bye']

#Create function that will make unique match id
def get_match_id():
    return datetime.now().strftime("M%d%m%Y_%H%M%S") #M25062026_125530

#create filename for match
def get_match_filename():
    match_id=get_match_id()[1:]
    return f"Match_{match_id}.txt"
