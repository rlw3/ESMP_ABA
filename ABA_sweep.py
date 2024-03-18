from time import sleep
import RPi.GPIO as GPIO

# Suppress GPIO warnings
GPIO.setwarnings(False)

# Set GPIO numbering mode
GPIO.setmode(GPIO.BCM)

# Constants for rotation direction
CW = 1  # Clockwise
CCW = 0  # Counter-Clockwise
SPR_1 = 400  # Effective SPR for motor 1 in 1/2 step mode
SPR_2 = 800  # SPR for motor 2 in 1/4 step mode
DEGREES_PER_STEP_1 = 360 / SPR_1
DEGREES_PER_STEP_2 = 360 / SPR_2

# Pin assignments
STEP_PIN_1 = 17
DIR_PIN_1 = 18
MODE_1 = (2, 3, 4)  # Motor 1 microstepping pins
STEP_PIN_2 = 26
DIR_PIN_2 = 20
MODE_2 = (6, 13, 19)  # Motor 2 microstepping pins

# Setup GPIO pins
GPIO.setup([STEP_PIN_1, DIR_PIN_1, STEP_PIN_2, DIR_PIN_2] + list(MODE_1) + list(MODE_2), GPIO.OUT)

# Set microstepping modes
GPIO.output(MODE_1, (1, 0, 0))  # 1/2 step for motor 1
GPIO.output(MODE_2, (0, 1, 0))  # 1/4 step for motor 2

# Step delay for pacing the motor steps
delay = 0.05

# Motor positions in degrees, initialized to 0
motor_positions = {1: 0, 2: 0}

def move_motors_to_angle(target_angle):
    global motor_positions
    
    # Calculate the angle difference from the current position to the target for Motor 2
    angle_difference_2 = target_angle - motor_positions[2]
    
    # Calculate steps needed based on Motor 2's DEGREES_PER_STEP_2
    steps_needed = int(angle_difference_2 / DEGREES_PER_STEP_2)

    # Determine direction for each motor
    GPIO.output(DIR_PIN_1, CW if angle_difference_2 > 0 else CCW)
    GPIO.output(DIR_PIN_2, CW if angle_difference_2 > 0 else CCW)

    # Perform steps for both motors, using the same step count
    for step in range(abs(steps_needed)):
        GPIO.output(STEP_PIN_1, GPIO.HIGH)
        GPIO.output(STEP_PIN_2, GPIO.HIGH)
        sleep(delay)
        GPIO.output(STEP_PIN_1, GPIO.LOW)
        GPIO.output(STEP_PIN_2, GPIO.LOW)
        sleep(delay)

    # Update motor positions based on the steps taken
    motor_positions[1] += steps_needed * DEGREES_PER_STEP_1
    motor_positions[2] += steps_needed * DEGREES_PER_STEP_2

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
