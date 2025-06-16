import time
import keyboard
from playsound import playsound
import os # To interact with the operating system, e.g., check if a file exists

# --- Global constants for file operations ---
BONUS_POOL_FILE = "E:\\Coding\\Python\\Programs\\Qimer\\bonus_pool.txt"
SOUND_FILE_PATH = "E:\\Coding\\Python\\Programs\\Qimer\\tick.wav" # User-defined path

def load_bonus_pool_from_file():
    """Loads the bonus time from a file."""
    if os.path.exists(BONUS_POOL_FILE):
        try:
            with open(BONUS_POOL_FILE, 'r') as f:
                content = f.read().strip()
                if content: # Check if file is not empty
                    return float(content)
        except (ValueError, IOError) as e:
            print(f"Error loading bonus pool from file: {e}. Starting with 0 bonus time.")
    return 0.0

def save_bonus_pool_to_file(amount):
    """Saves the current bonus time to a file."""
    try:
        with open(BONUS_POOL_FILE, 'w') as f:
            f.write(str(amount))
    except IOError as e:
        print(f"Error saving bonus pool to file: {e}")

def run_question_timer():
    """
    Runs a timer for questions with a consistent time limit (input in minutes).
    Maintains state (remaining time) for each question.
    Pressing SPACEBAR advances to the next question and saves remaining time to bonus pool.
    Pressing 'a' transfers all saved time to the current question.
    Pressing 'p' moves to the previous question. If that previous question has less than 10 seconds left,
    it automatically adds all bonus time to it.
    Plays a sound at the end of each question when it's completed (timed out or skipped forward).
    Displays the total actual time spent on questions at the end.
    Allows loading/saving of bonus pool for future sessions.
    """
    print("Welcome to the Question Timer!")

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

    # --- Load saved bonus pool at the start if user chooses ---
    total_excess_time_seconds = 0.0 # Initial bonus pool for the current session

    last_session_bonus = load_bonus_pool_from_file()
    if last_session_bonus > 0:
        print(f"\nINFO: A bonus pool of {last_session_bonus:.1f} seconds was saved from your last session.")
        print("Press 'x' NOW to load this bonus pool, or press any other key (like Enter) to start with an empty bonus pool.")
        
        # This will block until a key is pressed.
        # We suppress=False so the key press isn't consumed and can potentially be used later if needed,
        # though for 'x' as a one-time load, it doesn't matter much.
        pressed_key = keyboard.read_key(suppress=False) 
        
        if pressed_key == 'x':
            total_excess_time_seconds = last_session_bonus
            save_bonus_pool_to_file(0.0) # Clear the file after loading to prevent accidental re-load
            print(f"Bonus pool loaded! Starting this session with {total_excess_time_seconds:.1f} seconds bonus time.")
        else:
            print("Not loading saved bonus. Starting with an empty bonus pool.")
    else:
        print("No saved bonus pool found from previous sessions. Starting with an empty bonus pool.")
        
    time.sleep(0.5) # Give a moment for message to display and key debounce

    # --- Configuration for sound ---
    # SOUND_FILE_PATH is already a global constant
    # --- End sound configuration ---

    # --- Initialize question states ---
    # Each question will store its remaining time and total time spent on it
    question_states = []
    for q_num in range(num_questions):
        question_states.append({
            'initial_limit': time_limit,         # The base time set for the question
            'current_remaining': time_limit,     # Time left for this question (starts at initial_limit, saved/restored)
            'total_time_spent_on_this_q': 0      # Accumulates actual time spent on this specific question
        })
    
    print(f"\n--- Starting Timer for {num_questions} Questions (Each {time_limit_minutes:.1f} minutes) ---")
    print("Press SPACEBAR to **advance to the next question** and save remaining time to bonus pool.")
    print("Press 'a' to **transfer all bonus time to the current question**.")
    print("Press 'p' to **move to the previous question** (adds bonus time if < 10s left).")
    # Initial display of bonus pool, will be updated during the timer loop
    print(f"Current Bonus Pool: {total_excess_time_seconds:.1f} seconds") 

    current_question_num = 1 # We use 1-based indexing for display

    # --- Main loop to manage navigation between questions ---
    while current_question_num >= 1 and current_question_num <= num_questions:
        q_index = current_question_num - 1 # 0-based index for the list
        current_q_data = question_states[q_index]

        # If a question has 0 remaining time (e.g., already timed out or skipped with no time left),
        # automatically advance it.
        if current_q_data['current_remaining'] <= 0 and current_q_data['total_time_spent_on_this_q'] > 0:
            current_question_num += 1
            continue # Skip the timer loop for this question

        # Reset segment start time for the current question's active session
        segment_start_time = time.time()
        
        print(f"\n--- Question {current_question_num} ---")
        print(f"Starting with: {current_q_data['current_remaining']:.1f} seconds remaining.")

        # Flag to track how the inner timer loop exits
        action_taken_in_loop = None # 'skipped_forward', 'go_back', 'timed_out'

        # --- Inner loop for the current question's active timer segment ---
        while True:
            # Calculate elapsed time for this *segment* of the question's timer
            elapsed_since_segment_start = time.time() - segment_start_time
            
            # The actual time remaining for the question based on its saved state
            remaining_for_this_question = current_q_data['current_remaining'] - elapsed_since_segment_start

            # --- Handle input keys ---
            if keyboard.is_pressed('a'):
                if total_excess_time_seconds > 0:
                    transfer_amount = total_excess_time_seconds
                    
                    # Add bonus time to the question's remaining time (this is its new limit for this segment)
                    current_q_data['current_remaining'] += transfer_amount 
                    
                    # Adjust segment_start_time to effectively add time to the running countdown
                    # This pushes the "end time" of the current segment further into the future
                    segment_start_time += transfer_amount 
                    
                    total_excess_time_seconds = 0 # Reset bonus pool
                    
                    print(f"\nTransferred {transfer_amount:.1f} seconds! Question {current_question_num} now has {current_q_data['current_remaining']:.1f} seconds remaining. Bonus Pool: {total_excess_time_seconds:.1f}s")
                else:
                    print("\nNo excess time to transfer. Bonus Pool: 0.0s")
                time.sleep(0.15) # Debounce sleep

            if keyboard.is_pressed('p'):
                if current_question_num > 1:
                    print("\n'p' pressed! Moving to previous question.")

                    # Save the current question's remaining time before leaving
                    current_q_data['current_remaining'] = remaining_for_this_question
                    
                    # Add time spent in this segment to this question's total spent time
                    current_q_data['total_time_spent_on_this_q'] += elapsed_since_segment_start

                    # --- Conditionally add bonus time to the previous question ---
                    prev_q_index = current_question_num - 2 # Index of the question we're going back to
                    prev_q_data = question_states[prev_q_index]

                    if prev_q_data['current_remaining'] < 10:
                        if total_excess_time_seconds > 0:
                            transfer_amount = total_excess_time_seconds
                            prev_q_data['current_remaining'] += transfer_amount # Add bonus time to previous question
                            total_excess_time_seconds = 0 # Reset bonus pool
                            print(f"Question {current_question_num-1} had <10s left. Added {transfer_amount:.1f} seconds from bonus pool. Bonus Pool: {total_excess_time_seconds:.1f}s")
                            print(f"Question {current_question_num-1} now has {prev_q_data['current_remaining']:.1f} seconds remaining.")
                        else:
                            print(f"Question {current_question_num-1} had <10s left, but bonus pool is empty. No time added. Bonus Pool: {total_excess_time_seconds:.1f}s")
                    else:
                        print(f"Question {current_question_num-1} has {prev_q_data['current_remaining']:.1f} seconds left. Bonus time not added. Bonus Pool: {total_excess_time_seconds:.1f}s")
                    # --- END NEW LOGIC ---

                    current_question_num -= 1 # Decrement question number
                    action_taken_in_loop = 'go_back'
                    time.sleep(0.15) # Debounce sleep
                    break # Exit inner loop, outer loop will restart with new question_num
                else:
                    print("\nAlready at the first question. Cannot go back.")
                    time.sleep(0.15) # Debounce sleep

            if keyboard.is_pressed('space'):
                # Save the current question's remaining time before skipping
                current_q_data['current_remaining'] = remaining_for_this_question
                
                # Add time spent in this segment to this question's total spent time
                current_q_data['total_time_spent_on_this_q'] += elapsed_since_segment_start

                # Add remaining time to bonus pool only if positive
                if remaining_for_this_question > 0:
                    total_excess_time_seconds += remaining_for_this_question
                    print(f"\nSpacebar pressed! Skipping to next question. Added {remaining_for_this_question:.1f} seconds to Bonus Time Pool ({total_excess_time_seconds:.1f}s total).")
                else:
                    print("\nSpacebar pressed! Skipping to next question (no time left to save). Bonus Pool: {total_excess_time_seconds:.1f}s")

                action_taken_in_loop = 'skipped_forward'
                current_question_num += 1 # Advance question number
                time.sleep(0.15) # Debounce sleep
                break

            # --- Check for natural timer exhaustion ---
            if remaining_for_this_question <= 0:
                print(f"Time remaining: 0.0 seconds", end='\r')
                action_taken_in_loop = 'timed_out'
                
                # Set remaining to 0 and add the full segment duration to total spent
                current_q_data['current_remaining'] = 0 
                current_q_data['total_time_spent_on_this_q'] += elapsed_since_segment_start 
                break # Exit inner loop

            # --- Display remaining time and pause ---
            print(f"Time remaining: {remaining_for_this_question:.1f} seconds", end='\r')
            time.sleep(0.05) # Reduced general polling interval

        # --- After inner timer loop (question ended or navigation occurred) ---
        if action_taken_in_loop == 'timed_out':
            print(f"\nTime's up for Question {current_question_num}!")

        # Play sound only if question completed (timed out or skipped forward)
        if action_taken_in_loop in ['skipped_forward', 'timed_out']:
            try:
                playsound(SOUND_FILE_PATH)
            except Exception as e:
                print(f"Could not play sound: {e}")
                print(f"Please ensure the file '{SOUND_FILE_PATH}' exists and playsound is installed correctly.")
            
            if action_taken_in_loop == 'timed_out': # Add small pause for natural timeout
                 time.sleep(0.5)

    # --- End of main question loop ---

    # Final message after the main loop exits
    if current_question_num > num_questions:
        print("\nAll questions completed!")
    elif current_question_num < 1: # If user went back from Q1, this handles program exit cleanly
        print("\nExiting timer (went back from first question).")
    
    # --- Display total time spent on questions and remaining excess time ---
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

    # --- Save bonus pool at the very end ---
    save_bonus_pool_to_file(total_excess_time_seconds)
    print(f"\nYour current bonus pool ({total_excess_time_seconds:.1f} seconds) has been saved for your next session.")
    
    # --- Pause at the end for viewing details ---
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    run_question_timer()