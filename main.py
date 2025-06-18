import time
import keyboard
from playsound import playsound
import os
import pickle
import csv

# --- Global constants for file operations ---
BONUS_POOL_FILE = "E:\\Coding\\Python\\Programs\\Qimer\\bonus_pool.pkl"
SESSION_DATA_FILE = "E:\\Coding\\Python\\Programs\\Qimer\\session_data.csv"
SOUND_FILE_PATH = "E:\\Coding\\Python\\Programs\\Qimer\\tick.wav" # User-defined path

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
                        # Subject is already a string, no conversion needed
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
    fieldnames = ['session_num', 'subject', 'total_time_taken', 'avg_time_per_q', 'bonus_at_end', 'total_questions_in_session']
    
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


# --- Main application function ---
def run_question_timer():
    print("Welcome to the Question Timer!")

    # --- Load existing session data (kept for current_session_num calculation) ---
    all_sessions_data = load_session_data_from_csv()
    current_session_num = len(all_sessions_data) + 1

    # --- Initializing bonus pool to 0.0, will be loaded if user chooses ---
    total_excess_time_seconds = 0.0 

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
        
        # This will block until a key is pressed
        # Note: keyboard.read_key() can sometimes capture system keys,
        # so for this specific interaction, it's generally robust.
        pressed_key = keyboard.read_key(suppress=False) # suppress=False to allow key to function normally after this
        
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

            # 'x' key functionality is now only at startup prompt, removed from here

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

        if action_taken_in_loop in ['skipped_forward', 'timed_out']:
            try:
                playsound(SOUND_FILE_PATH)
            except Exception as e:
                print(f"Could not play sound: {e}")
                print(f"Please ensure the file '{SOUND_FILE_PATH}' exists and playsound is installed correctly.")
            
            if action_taken_in_loop == 'timed_out': 
                 time.sleep(0.5)

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

    # --- Save current session data to CSV ---
    average_time_per_question = 0.0
    if num_questions > 0: 
        average_time_per_question = final_total_spent_seconds / num_questions
    
    current_session_details = {
        'session_num': current_session_num,
        'subject': selected_subject,
        'total_time_taken': final_total_spent_seconds,
        'avg_time_per_q': average_time_per_question,
        'bonus_at_end': total_excess_time_seconds,
        'total_questions_in_session': num_questions
    }
    
    save_session_data_to_csv(current_session_details) 
    print("\nSession details recorded successfully in CSV file.")

    save_bonus_pool_to_file(total_excess_time_seconds)
    print(f"Your final bonus pool amount ({total_excess_time_seconds:.1f} seconds) has been saved for your next session.")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    run_question_timer()