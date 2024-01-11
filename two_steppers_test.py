from time import sleep
import RPi.GPIO as GPIO

# Suppress GPIO warnings
GPIO.setwarnings(False)

# Set GPIO numbering system
GPIO.setmode(GPIO.BCM)

# Define constants for rotation direction and steps per revolution
CW = 1  # Clockwise
CCW = 0  # Counter-Clockwise
SPR = 800  # Steps per Revolution

# Define pin assignments for stepper 1
STEP_PIN_1 = 17
DIR_PIN_1 = 18
MODE_1 = (2, 3, 4)

# Define pin assignments for stepper 2
STEP_PIN_2 = 26
DIR_PIN_2 = 20
MODE_2 = (6, 13, 19)

# Function to rotate a stepper motor for one full rotation
def rotate_stepper(stepper_step_pin, step_count, delay):
    for _ in range(step_count):
        GPIO.output(stepper_step_pin, GPIO.HIGH)
        sleep(delay)
        GPIO.output(stepper_step_pin, GPIO.LOW)
        sleep(delay)

# Set up GPIO pins for step and direction
GPIO.setup(STEP_PIN_1, GPIO.OUT)
GPIO.setup(DIR_PIN_1, GPIO.OUT)
GPIO.setup(STEP_PIN_2, GPIO.OUT)
GPIO.setup(DIR_PIN_2, GPIO.OUT)

# Set microstepping mode for stepper 1 (1/4 step)
GPIO.setup(MODE_1, GPIO.OUT)
RESOLUTION_1 = {'Full': (0, 0, 0), 'Half': (1, 0, 0), '1/4': (0, 1, 0)}
GPIO.output(MODE_1, RESOLUTION_1['1/4'])

# Set microstepping mode for stepper 2 (1/4 step)
GPIO.setup(MODE_2, GPIO.OUT)
RESOLUTION_2 = {'Full': (0, 0, 0), 'Half': (1, 0, 0), '1/4': (0, 1, 0)}
GPIO.output(MODE_2, RESOLUTION_2['1/4'])

# Step count and delay
step_count = 100
delay = 0.0208

# Rotate stepper 1 clockwise and then counter-clockwise
GPIO.output(DIR_PIN_1, CW)
rotate_stepper(STEP_PIN_1, step_count, delay)
sleep(1)
GPIO.output(DIR_PIN_1, CCW)
rotate_stepper(STEP_PIN_1, step_count, delay)

# Rotate stepper 2 clockwise and then counter-clockwise
GPIO.output(DIR_PIN_2, CW)
rotate_stepper(STEP_PIN_2, step_count, delay)
sleep(1)
GPIO.output(DIR_PIN_2, CCW)
rotate_stepper(STEP_PIN_2, step_count, delay)

# Clean up GPIO settings when done
GPIO.cleanup()
