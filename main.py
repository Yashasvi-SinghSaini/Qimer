import time
import keyboard
from playsound import playsound
import os
import pickle
import csv
from datetime import datetime

# --- Global constants for file operations ---
BONUS_POOL_FILE = "E:\\Coding\\Python\\Programs\\Qimer\\bonus_pool.pkl"
SESSION_DATA_FILE = "E:\\Coding\\Python\\Programs\\Qimer\\session_data.csv"
DAILY_QUESTIONS_TRACKER_FILE = "E:\\Coding\\Python\\Programs\\Qimer\\daily_questions_tracker.pkl"
SOUND_FILE_PATH = "E:\\Coding\\Python\\Programs\\Qimer\\tick.wav" # User-defined path

# --- Daily Question Goals (VARIABLE NAMES CHANGED) ---
GOAL_1 = 100
GOAL_2 = 200
GOAL_3 = 300

# --- Helper functions for loading/saving bonus pool (remains pickle) ---
def load_bonus_pool_from_file():
    """Loads the bonus time from a file."""
    if os.path.exists(BONUS_POOL_FILE):
        try:
            with open(BONUS_POOL_FILE, 'rb') as f:
                content = pickle.load(f)
                if isinstance(content, (int, float)): # Ensure loaded content is a number
                    return float(content)
                else:
                    print(f"Warning: Unexpected data type in bonus pool file ({type(content)}). Starting with 0 bonus time.")
                    return 0.0
        except (EOFError, pickle.UnpicklingError, IOError) as e:
            print(f"Error loading bonus pool from file: {e}. File might be empty or corrupted. Starting with 0 bonus time.")
    return 0.0

def save_bonus_pool_to_file(amount):
    """Saves the current bonus time to a file."""
    try:
        with open(BONUS_POOL_FILE, 'wb') as f:
            pickle.dump(float(amount), f) # Ensure it's saved as a float
    except IOError as e:
        print(f"Error saving bonus pool to file: {e}")

# --- Updated Helper functions for Daily Questions Tracker ---
def load_daily_questions_tracker():
    """Loads daily question count, last recorded date, and celebrated levels."""
    if os.path.exists(DAILY_QUESTIONS_TRACKER_FILE):
        try:
            with open(DAILY_QUESTIONS_TRACKER_FILE, 'rb') as f:
                data = pickle.load(f)
                # Ensure data is a dictionary and has expected keys. Add 'celebrated_levels' if missing for old files.
                if isinstance(data, dict) and 'date' in data and 'count' in data:
                    if 'celebrated_levels' not in data:
                        data['celebrated_levels'] = [] # Initialize for old files
                    return data
                else:
                    print(f"Warning: Unexpected data format in daily tracker file. Resetting.")
        except (EOFError, pickle.UnpackingError, IOError) as e: # Corrected UnpicklingError to UnpackingError for consistency
            print(f"Error loading daily questions tracker: {e}. Starting fresh.")
    return {'date': None, 'count': 0, 'celebrated_levels': []} # Default empty state with new key

def save_daily_questions_tracker(date, count, celebrated_levels):
    """Saves the current daily question count, date, and celebrated levels."""
    try:
        with open(DAILY_QUESTIONS_TRACKER_FILE, 'wb') as f:
            pickle.dump({'date': date, 'count': count, 'celebrated_levels': celebrated_levels}, f)
    except IOError as e:
        print(f"Error saving daily questions tracker: {e}")

# Functions for session data (CSV)
def load_session_data_from_csv():
    """Loads all past session data from a CSV file."""
    sessions = []
    if os.path.exists(SESSION_DATA_FILE):
        try:
            with open(SESSION_DATA_FILE, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Convert string values back to their original types
                    try:
                        row['session_num'] = int(row.get('session_num', 0))
                        row['total_time_taken'] = float(row.get('total_time_taken', 0.0))
                        row['avg_time_per_q'] = float(row.get('avg_time_per_q', 0.0))
                        row['bonus_at_end'] = float(row.get('bonus_at_end', 0.0))
                        row['total_questions_in_session'] = int(row.get('total_questions_in_session', 0)) 
                        sessions.append(row)
                    except ValueError as ve:
                        print(f"Warning: Skipping malformed row in CSV: {row} - {ve}")
        except FileNotFoundError:
            print(f"No existing session data CSV file found at '{SESSION_DATA_FILE}'. Starting fresh.")
        except Exception as e: # Catch other potential CSV reading errors
            print(f"Error reading session data CSV file: {e}. Starting with empty session data.")
    return sessions

def save_session_data_to_csv(session_data_dict):
    """Saves a single session's data to the CSV file, appending it."""
    fieldnames = ['session_num', 'subject', 'date', 'total_time_taken', 'avg_time_per_q', 'bonus_at_end', 'total_questions_in_session']
    
    file_exists = os.path.exists(SESSION_DATA_FILE)
    
    try:
        with open(SESSION_DATA_FILE, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader() # Write header only if file is new
            
            writer.writerow(session_data_dict) # Write the new session's data
            
    except IOError as e:
        print(f"Error saving session data to CSV file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while writing to CSV: {e}")

# --- Tiered Animation Functions ---
def clear_screen():
    """Clears the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def animate_small_celebration(goal_value):
    """Plays a small console-based celebration animation."""
    frames = [
        "   🎉   ",
        "  ✨🎉✨ "
    ]
    message = f"CONGRATS! {goal_value} QUESTIONS ACHIEVED!"
    
    clear_screen()
    print("\n\n")
    print("         " + frames[0])
    print(f"     {message}")
    print("\n\n")
    time.sleep(0.5)
    clear_screen()
    print("\n\n")
    print("         " + frames[1])
    print(f"     {message}")
    print("\n\n")
    time.sleep(0.5)
    clear_screen()
    print("\n") # Reset cursor for next prints

def animate_bigger_celebration(goal_value):
    """Plays a bigger console-based celebration animation."""
    frames = [
        "   🌟🌟   ",
        "  ✨🎉✨  ",
        " ✨🎉🎉✨ ",
        "  ✨🎉✨  "
    ]
    messages = [
        "MASSIVE CONGRATULATIONS!",
        f"You hit {goal_value} questions today!",
        "Keep crushing it!"
    ]
    
    for _ in range(2): # Repeat animation a few times
        for frame in frames:
            clear_screen()
            print("\n\n")
            print("         " + frame)
            for msg in messages:
                print(f"     {msg}")
            print("\n\n")
            time.sleep(0.4)
    clear_screen()
    print("\n")

def animate_very_big_celebration(goal_value):
    """Plays a very big console-based celebration animation, lasting ~1 minute."""
    
    celebration_frames = [
        " _^_   _^_ ",
        "//_\\\\_//_\\\\",
        "|-----|-----|",
        "| 🎉 | 🎉 |",
        "|-----|-----|",
        "\\___///___/",
        "  \\_/   \\_/"
    ]
    
    alt_frames = [
        "  * * ",
        " * * * * ",
        " * CONGRATS! * ",
        "  * * "
    ]

    messages = [
        "!!!! UNBELIEVABLE ACCOMPLISHMENT !!!!",
        f"YOU COMPLETED {goal_value} QUESTIONS TODAY!",
        "THIS IS TRULY REMARKABLE. TAKE A MOMENT TO CELEBRATE YOUR DEDICATION!",
        "Your consistency is inspiring. What's next?"
    ]
    
    start_time = time.time()
    duration = 60 # seconds
    frame_delay = 0.5 # seconds per frame

    cycle_count = 0
    while (time.time() - start_time) < duration:
        clear_screen()
        print("\n\n")

        if cycle_count % 2 == 0: # Alternate between main celebration and simpler frames
            for line in celebration_frames:
                print(f"        {line}")
        else:
            for line in alt_frames:
                print(f"        {line}")
        
        print("\n")
        for msg in messages:
            print(f"    {msg}")
        print("\n\n")
        
        time.sleep(frame_delay)
        cycle_count += 1

    clear_screen()
    print("\n")


# --- Main application function ---
def run_question_timer():
    print("Welcome to the Question Timer!")

    # --- Load existing session data (kept for current_session_num calculation) ---
    all_sessions_data = load_session_data_from_csv()
    current_session_num = len(all_sessions_data) + 1

    # --- Initialize bonus pool ---
    total_excess_time_seconds = 0.0 

    # --- Load and update daily questions tracker ---
    daily_stats = load_daily_questions_tracker()
    current_date_str = datetime.now().strftime('%Y-%m-%d')

    # If it's a new day, reset count and celebrated levels
    if daily_stats['date'] != current_date_str:
        daily_questions_completed_today = 0
        celebrated_levels = []
        print(f"\nINFO: New day detected. Daily question count and celebration levels reset.")
    else:
        daily_questions_completed_today = daily_stats['count']
        celebrated_levels = daily_stats['celebrated_levels']
    
    print(f"INFO: Questions completed today so far: {daily_questions_completed_today}")

    # --- Input for Subject for the CURRENT session ---
    subject_map = {'p': 'Physics', 'c': 'Chemistry', 'm': 'Maths'}
    selected_subject = None
    while selected_subject is None:
        subject_input = input(f"\nEnter Subject (P for Physics, C for Chemistry, M for Maths): ").lower()
        if subject_input in subject_map:
            selected_subject = subject_map[subject_input]
        else:
            print("Invalid input. Please enter P, C, or M.")

    # --- Initial setup for number of questions and base time limit ---
    while True:
        try:
            num_questions_str = input("How many questions do you want to do? (Enter 'q' to quit): ")
            if num_questions_str.lower() == 'q':
                print("Exiting timer. Goodbye!")
                return
            num_questions = int(num_questions_str)
            if num_questions <= 0:
                print("Please enter a positive number of questions.")
            else:
                break
        except ValueError:
            print("Invalid input. Please enter a whole number or 'q'.")

    while True:
        try:
            time_limit_minutes_str = input("Enter the base time limit for EACH question (in minutes): ")
            time_limit_minutes = float(time_limit_minutes_str)
            if time_limit_minutes <= 0:
                print("Please enter a positive time limit.")
            else:
                time_limit = time_limit_minutes * 60 # Base time limit in seconds
                break
        except ValueError:
            print("Invalid input. Please enter a number for time.")
    
    # --- BONUS POOL HANDLING WITH keyboard.read_key() ---
    last_session_bonus = load_bonus_pool_from_file()
    if last_session_bonus > 0:
        print(f"\nINFO: A bonus pool of {last_session_bonus:.1f} seconds was saved from your last session.")
        print("Press 'x' NOW to load this bonus pool, or press any other key/Enter to start with an empty bonus pool.")
        
        pressed_key = keyboard.read_key(suppress=False) 
        
        if pressed_key == 'x':
            total_excess_time_seconds = last_session_bonus
            save_bonus_pool_to_file(0.0) # Clear the file after loading to prevent accidental re-load
            print(f"Bonus pool loaded! Starting this session with {total_excess_time_seconds:.1f} seconds bonus time.")
        else:
            print("Not loading saved bonus. Starting with an empty bonus pool.")
    else:
        print("No saved bonus pool found from previous sessions. Starting with an empty bonus pool.")
    # --- END keyboard.read_key() BONUS POOL HANDLING ---

    time.sleep(0.5) # Give a moment for message to display and key debounce

    # --- Configuration for sound ---
    question_states = []
    for q_num in range(num_questions):
        question_states.append({
            'initial_limit': time_limit,         
            'current_remaining': time_limit,     
            'total_time_spent_on_this_q': 0      
        })
    
    print(f"\n--- Starting Timer for {num_questions} Questions (Each {time_limit_minutes:.1f} minutes) ---")
    print("Press SPACEBAR to **advance to the next question** and save remaining time to bonus pool.")
    print("Press 'a' to **transfer all bonus time to the current question** (spends entire pool).")
    print("Press 'p' to **move to the previous question** (adds bonus time if < 10s left).")
    print("Press 'r' to **change the base time limit** for the remaining questions.")
    print(f"Current Bonus Pool: {total_excess_time_seconds:.1f} seconds (updates below)") 

    current_question_num = 1 

    # --- Main loop to manage navigation between questions ---
    while current_question_num >= 1 and current_question_num <= num_questions:
        q_index = current_question_num - 1 
        current_q_data = question_states[q_index]

        if current_q_data['current_remaining'] <= 0 and current_q_data['total_time_spent_on_this_q'] > 0:
            current_question_num += 1
            continue 

        segment_start_time = time.time()
        
        print(f"\n--- Question {current_question_num} ---")
        print(f"Starting with: {current_q_data['current_remaining']:.1f} seconds remaining.")

        action_taken_in_loop = None 

        # --- Inner loop for the current question's active timer segment ---
        while True:
            elapsed_since_segment_start = time.time() - segment_start_time
            remaining_for_this_question = current_q_data['current_remaining'] - elapsed_since_segment_start

            # --- Handle input keys ---
            if keyboard.is_pressed('a'):
                if total_excess_time_seconds > 0:
                    transfer_amount = total_excess_time_seconds
                    current_q_data['current_remaining'] += transfer_amount 
                    total_excess_time_seconds = 0 
                    
                    print(f"\nTransferred {transfer_amount:.1f} seconds! Question {current_question_num} now has {current_q_data['current_remaining']:.1f} seconds remaining. Current Bonus Pool: {total_excess_time_seconds:.1f}s")
                else:
                    print("\nNo excess time to transfer. Current Bonus Pool: 0.0s")
                time.sleep(0.15) 

            if keyboard.is_pressed('r'): 
                current_q_data['current_remaining'] = remaining_for_this_question
                current_q_data['total_time_spent_on_this_q'] += elapsed_since_segment_start

                while True:
                    try:
                        new_time_limit_minutes_str = input("\nEnter the new base time limit for the remaining questions (in minutes): ")
                        new_time_limit_minutes = float(new_time_limit_minutes_str)
                        if new_time_limit_minutes <= 0:
                            print("Please enter a positive time limit.")
                        else:
                            new_time_limit = new_time_limit_minutes * 60 # Base time limit in seconds
                            break
                    except ValueError:
                        print("Invalid input. Please enter a number for time.")
                
                for i in range(current_question_num - 1, num_questions):
                    question_states[i]['initial_limit'] = new_time_limit
                    if i == (current_question_num - 1): 
                        question_states[i]['current_remaining'] = min(question_states[i]['current_remaining'], new_time_limit)
                    else: 
                        question_states[i]['current_remaining'] = new_time_limit

                print(f"Base time limit changed to {new_time_limit_minutes:.1f} minutes for the remaining questions.")
                action_taken_in_loop = 'time_changed' 
                time.sleep(0.15)
                break 

            if keyboard.is_pressed('p'):
                if current_question_num > 1:
                    print("\n'p' pressed! Moving to previous question.")

                    current_q_data['current_remaining'] = remaining_for_this_question
                    current_q_data['total_time_spent_on_this_q'] += elapsed_since_segment_start

                    prev_q_index = current_question_num - 2 
                    prev_q_data = question_states[prev_q_index]

                    if prev_q_data['current_remaining'] < 10:
                        if total_excess_time_seconds > 0:
                            transfer_amount = total_excess_time_seconds
                            prev_q_data['current_remaining'] += transfer_amount 
                            total_excess_time_seconds = 0 
                            print(f"Question {current_question_num-1} had <10s left. Added {transfer_amount:.1f} seconds from bonus pool. Current Bonus Pool: {total_excess_time_seconds:.1f}s")
                            print(f"Question {current_question_num-1} now has {prev_q_data['current_remaining']:.1f} seconds remaining.")
                        else:
                            print(f"Question {current_question_num-1} had <10s left, but bonus pool is empty. No time added. Current Bonus Pool: {total_excess_time_seconds:.1f}s")
                    else:
                        print(f"Question {current_question_num-1} has {prev_q_data['current_remaining']:.1f} seconds left. Bonus time not added. Current Bonus Pool: {total_excess_time_seconds:.1f}s")

                    current_question_num -= 1 
                    action_taken_in_loop = 'go_back'
                    time.sleep(0.15) 
                    break 
                else:
                    print("\nAlready at the first question. Cannot go back.")
                    time.sleep(0.15) 

            if keyboard.is_pressed('space'):
                current_q_data['current_remaining'] = remaining_for_this_question
                current_q_data['total_time_spent_on_this_q'] += elapsed_since_segment_start

                if remaining_for_this_question > 0:
                    total_excess_time_seconds += remaining_for_this_question 
                    print(f"\nSpacebar pressed! Skipping to next question. Added {remaining_for_this_question:.1f} seconds to Bonus Time Pool ({total_excess_time_seconds:.1f}s total).")
                else:
                    print("\nSpacebar pressed! Skipping to next question (no time left to save). Current Bonus Pool: {total_excess_time_seconds:.1f}s")
                
                current_q_data['current_remaining'] = 0.0 

                action_taken_in_loop = 'skipped_forward'
                current_question_num += 1 
                time.sleep(0.15) 
                break

            if remaining_for_this_question <= 0:
                print(f"Time remaining: 0.0 seconds", end='\r')
                action_taken_in_loop = 'timed_out'
                
                current_q_data['current_remaining'] = 0 
                current_q_data['total_time_spent_on_this_q'] += elapsed_since_segment_start 
                break 

            print(f"Time remaining: {remaining_for_this_question:.1f} seconds", end='\r')
            time.sleep(0.05) 

        if action_taken_in_loop == 'timed_out':
            print(f"\nTime's up for Question {current_question_num}!")

        if action_taken_in_loop in ['skipped_forward', 'timed_out', 'go_back', 'time_changed']:
            try:
                playsound(SOUND_FILE_PATH)
            except Exception as e:
                print(f"Could not play sound: {e}")
                print(f"Please ensure the file '{SOUND_FILE_PATH}' exists and playsound is installed correctly.")
            
            if action_taken_in_loop == 'timed_out': 
                 time.sleep(0.5)
            continue 

    # --- End of main question loop ---

    if current_question_num > num_questions:
        print("\nAll questions completed!")
    elif current_question_num < 1: 
        print("\nExiting timer (went back from first question).")
    
    final_total_spent_seconds = sum(q_data['total_time_spent_on_this_q'] for q_data in question_states)

    final_total_minutes = int(final_total_spent_seconds // 60)
    final_total_seconds = int(final_total_spent_seconds % 60)
    print(f"\n--- Total time spent on questions: {final_total_minutes} minutes and {final_total_seconds} seconds ---")
    
    if total_excess_time_seconds > 0:
        excess_minutes = int(total_excess_time_seconds // 60)
        excess_seconds = int(total_excess_time_seconds % 60)
        print(f"--- Remaining Bonus Time in Pool: {excess_minutes} minutes and {excess_seconds} seconds ---")
    else:
        print("--- Bonus Time Pool is empty. ---")

    # --- Update Daily Questions Tracker at session end ---
    daily_questions_completed_today += num_questions # Add questions from this session

    # Check for goal achievements in descending order to trigger the biggest one first
    if daily_questions_completed_today >= GOAL_3 and GOAL_3 not in celebrated_levels:
        print(f"\n!!! DAILY QUESTION GOAL ({GOAL_3}) REACHED !!!")
        animate_very_big_celebration(GOAL_3)
        print(f"CONGRATULATIONS! You've completed {GOAL_3} questions today!")
        celebrated_levels.append(GOAL_3)
    elif daily_questions_completed_today >= GOAL_2 and GOAL_2 not in celebrated_levels:
        print(f"\n!!! DAILY QUESTION GOAL ({GOAL_2}) REACHED !!!")
        animate_bigger_celebration(GOAL_2)
        print(f"CONGRATULATIONS! You've completed {GOAL_2} questions today!")
        celebrated_levels.append(GOAL_2)
    elif daily_questions_completed_today >= GOAL_1 and GOAL_1 not in celebrated_levels:
        print(f"\n!!! DAILY QUESTION GOAL ({GOAL_1}) REACHED !!!")
        animate_small_celebration(GOAL_1)
        print(f"CONGRATULATIONS! You've completed {GOAL_1} questions today!")
        celebrated_levels.append(GOAL_1)

    save_daily_questions_tracker(current_date_str, daily_questions_completed_today, celebrated_levels)
    print(f"Daily questions completed: {daily_questions_completed_today}")
    
    # --- Save current session data to CSV ---
    average_time_per_question = 0.0
    if num_questions > 0: 
        average_time_per_question = final_total_spent_seconds / num_questions
    
    current_session_details = {
        'session_num': current_session_num,
        'subject': selected_subject,
        'date': datetime.now().strftime('%Y-%m-%d'), 
        'total_time_taken': final_total_spent_seconds,
        'avg_time_per_q': average_time_per_question,
        'bonus_at_end': total_excess_time_seconds,
        'total_questions_in_session': num_questions
    }
    
    save_session_data_to_csv(current_session_details) 
    print("Session details recorded successfully in CSV file.")

    save_bonus_pool_to_file(total_excess_time_seconds)
    print(f"Your final bonus pool amount ({total_excess_time_seconds:.1f} seconds) has been saved for your next session.")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    run_question_timer()