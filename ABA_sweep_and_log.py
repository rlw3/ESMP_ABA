from time import sleep, time
import RPi.GPIO as GPIO
import datetime
import threading

# Suppress GPIO warnings
GPIO.setwarnings(False)

# Set GPIO numbering mode
GPIO.setmode(GPIO.BCM)

# Constants for rotation direction and steps
CW = 1  # Clockwise
CCW = 0  # Counter-Clockwise
SPR_1 = 400  # Effective SPR for motor 1 in 1/2 step mode
SPR_2 = 800  # SPR for motor 2 in 1/4 step mode
DEGREES_PER_STEP_1 = 360 / SPR_1
DEGREES_PER_STEP_2 = 360 / SPR_2

# Pin assignments and setup
STEP_PIN_1 = 17
DIR_PIN_1 = 18
MODE_1 = (2, 3, 4)
STEP_PIN_2 = 26
DIR_PIN_2 = 20
MODE_2 = (6, 13, 19)
GPIO.setup([STEP_PIN_1, DIR_PIN_1, STEP_PIN_2, DIR_PIN_2] + list(MODE_1) + list(MODE_2), GPIO.OUT)

# Set microstepping modes
GPIO.output(MODE_1, (1, 0, 0))
GPIO.output(MODE_2, (0, 1, 0))

# Step delay and motor positions initialization
delay = 0.05
motor_positions = {1: 0, 2: 0}

# Initialize the log file
now = datetime.datetime.now()
filename = f"logs/log_{now.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
with open(filename, 'w') as f:
    f.write("Elapsed Time (s), Motor 2 Angle\n")

# Flag to control logging
logging_active = False

# Record the start time
start_time = None

def log_angles_continuously():
    """Logs Motor 2's angle at quarter-second intervals."""
    global logging_active, start_time
    while logging_active:
        elapsed_time = round(time() - start_time, 2)  # Calculate elapsed time since start
        with open(filename, 'a') as f:
            f.write(f"{elapsed_time}, {motor_positions[2]}\n")
        sleep(0.25)  # Log every quarter second

def move_motors_to_angle(target_angle):
    global motor_positions, logging_active, start_time
    
    angle_difference_2 = target_angle - motor_positions[2]
    steps_needed = int(angle_difference_2 / DEGREES_PER_STEP_2)
    GPIO.output(DIR_PIN_1, CW if angle_difference_2 > 0 else CCW)
    GPIO.output(DIR_PIN_2, CW if angle_difference_2 > 0 else CCW)

    # Start logging in a separate thread
    logging_active = True
    start_time = time()  # Record the start time for logging
    logging_thread = threading.Thread(target=log_angles_continuously)
    logging_thread.start()

    for step in range(abs(steps_needed)):
        GPIO.output(STEP_PIN_1, GPIO.HIGH)
        GPIO.output(STEP_PIN_2, GPIO.HIGH)
        sleep(delay)
        GPIO.output(STEP_PIN_1, GPIO.LOW)
        GPIO.output(STEP_PIN_2, GPIO.LOW)
        sleep(delay)

        # Update the position of Motor 2 for each step
        motor_positions[2] += DEGREES_PER_STEP_2 if angle_difference_2 > 0 else -DEGREES_PER_STEP_2

    # Stop logging
    logging_active = False
    logging_thread.join()  # Wait for the logging thread to finish

try:
    while True:
        starting_angle = float(input("Enter starting angle: "))
        motor_positions[1], motor_positions[2] = starting_angle, starting_angle

        end_angle = float(input("Enter end angle: "))
        
        move_motors_to_angle(end_angle)
        
        print(f"Final angle for Motor 1: {motor_positions[1]} degrees")
        print(f"Final angle for Motor 2: {motor_positions[2]} degrees")

        if input("Reset? (yes/no): ").lower() == 'yes':
            move_motors_to_angle(starting_angle)
            print("Motors reset to starting position.")

except KeyboardInterrupt:
    print("\nProgram terminated.")
finally:
    GPIO.cleanup()
