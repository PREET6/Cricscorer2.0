"""
test_setup.py - Verify your project structure is correct
Run this to check if everything is working
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print(" TESTING CRICSCORER SETUP")
print("=" * 60)

# ============================================
# TEST 1: Check if config loads
# ============================================
print("\nTesting config import...")
try:
    import config
    print("Config imported successfully")
    print(f"      Project: {config.Project_name}")
    print(f"      Version: {config.Version}")
    print(f"      DEVELOPER: {config.Developer}")
    print(f"      COMPANY: {config.company}")
except Exception as e:
    print(f"Config error: {e}")
    sys.exit(1)

# ============================================
# TEST 2: Check if folders were created
# ============================================
print("\nChecking directories...")
folders_to_check = [
    ('Data Directory', config.Data_dir),
    ('Matches Directory', config.Matches_dir),
    ('History Directory', config.History_dir),
    ('Players Directory', config.Players_dir),
    ('Backup Directory', config.Backup_dir),
    ('Logs Directory', config.Log_dir),
]

all_exist = True
for name, folder_path in folders_to_check:
    if os.path.exists(folder_path):
        print(f"{name}: {folder_path}")
    else:
        print(f"{name}: {folder_path} - MISSING!")
        all_exist = False

# ============================================
# TEST 3: Check if files were created
# ============================================
print("\nChecking files...")
history_file = os.path.join(config.History_dir, 'match_history.txt')
Db_record = config.Database_file

if os.path.exists(history_file):
    print(f"History file: {history_file}")
    # Read first few lines
    with open(history_file, 'r') as f:
        lines = f.readlines()
        print(f"Lines: {len(lines)}")
        if lines:
            print(f"First line: {lines[0].strip()[:50]}...")
else:
    print(f"History file missing: {history_file}")

if os.path.exists(Db_record):
    print(f"Players Records Storage: {Db_record}")
    print(f"Cricscorer Database: {Db_record}")
    print(f"Size: {os.path.getsize(Db_record)} Bytes")
else:
    print(f"Database is Missing {Db_record}")

# ============================================
# TEST 4: Test helper functions
# ============================================
print("\nTesting helper functions...")
try:
    match_id = config.get_match_id()
    print(f" get_match_id(): {match_id}")
    
    filename = config.get_match_filename()
    print(f"get_match_filename(): {filename}")
    
    print(f"VALID_RUNS: {config.VALID_RUNS}")
    print(f"VALID_OUTCOMES: {config.VALID_OUTCOMES}")
except Exception as e:
    print(f"Helper function error: {e}")

# ============================================
# TEST 5: Test main.py runs
# ============================================
print("\nTesting main.py...")
try:
    import main
    print("main.py imported successfully")
except Exception as e:
    print(f"main.py error: {e}")

# ============================================
# FINAL RESULT
# ============================================
print("\n" + "=" * 60)
if all_exist:
    print("ALL TESTS PASSED! Your setup is ready.")
    print("You can now run: python main.py")
else:
    print("Some tests failed. Please check the errors above.")
    print("Try running: python config.py")
print("=" * 60)
