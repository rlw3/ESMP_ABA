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
SPR_1 = 800  # Effective SPR for motor 1 in 1/2 step mode
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
GPIO.output(MODE_1, (0, 1, 0))
GPIO.output(MODE_2, (0, 1, 0))

# Step delay and motor positions initialization
delay = 0.05
motor_positions = {1: 0, 2: 0}

# Get the sample's name from the user
sample_name = input("Enter the sample's name: ")

# Initialize the log file
now = datetime.datetime.now()
filename = f"logs/{sample_name}_log_{now.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
with open(filename, 'w') as f:
    f.write(f"Sample Name: {sample_name}\n")
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
            f.write(f"{elapsed_time}, {motor_positions[2]:.3f}\n")
        sleep(0.25)  # Log every quarter second

def move_motors_by_angle(angle_difference):
    global motor_positions, logging_active, start_time
    
    steps_needed_1 = int(angle_difference / DEGREES_PER_STEP_1)
    steps_needed_2 = int(angle_difference / DEGREES_PER_STEP_2)
    
    GPIO.output(DIR_PIN_1, CW if angle_difference > 0 else CCW)
    GPIO.output(DIR_PIN_2, CW if angle_difference > 0 else CCW)

    # Start logging in a separate thread
    logging_active = True
    start_time = time()  # Record the start time for logging
    logging_thread = threading.Thread(target=log_angles_continuously)
    logging_thread.start()

    for step in range(abs(steps_needed_2)):
        if step < abs(steps_needed_1):
            GPIO.output(STEP_PIN_1, GPIO.HIGH)
        GPIO.output(STEP_PIN_2, GPIO.HIGH)
        sleep(delay)
        GPIO.output(STEP_PIN_1, GPIO.LOW)
        GPIO.output(STEP_PIN_2, GPIO.LOW)
        sleep(delay)

        # Update the position of both motors for each step
        if step < abs(steps_needed_1):
            motor_positions[1] += DEGREES_PER_STEP_1 if angle_difference > 0 else -DEGREES_PER_STEP_1
        motor_positions[2] += DEGREES_PER_STEP_2 if angle_difference > 0 else -DEGREES_PER_STEP_2

    # Allow logging to continue for an additional second after motors stop moving
    sleep(1)
    logging_active = False
    logging_thread.join()  # Wait for the logging thread to finish

try:
    while True:
        starting_angle = float(input("Enter starting angle: "))
        motor_positions[1], motor_positions[2] = starting_angle, starting_angle

        end_angle = float(input("Enter end angle: "))
        
        angle_difference = end_angle - starting_angle
        move_motors_by_angle(angle_difference)
        
        print(f"Sample end angle: {motor_positions[2]:.3f} degrees")

        if input("Reset? (yes/no): ").lower() == 'yes':
            move_motors_by_angle(-angle_difference)
            print("Motors reset to starting position.")
        else:
            break

except KeyboardInterrupt:
    print("\nProgram terminated.")
finally:
    GPIO.cleanup()
