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

# Set up GPIO pins for step and direction
GPIO.setup(STEP_PIN_1, GPIO.OUT)
GPIO.setup(DIR_PIN_1, GPIO.OUT)
GPIO.setup(STEP_PIN_2, GPIO.OUT)
GPIO.setup(DIR_PIN_2, GPIO.OUT)

# Set microstepping mode (1/4 step)
GPIO.setup(MODE_1, GPIO.OUT)
GPIO.setup(MODE_2, GPIO.OUT)
GPIO.output(MODE_1, (0, 1, 0))
GPIO.output(MODE_2, (1, 0, 0))

# Step delay
delay = 0.0208

# Tracking steps for each motor
motor_steps = {1: 0, 2: 0}

def move_motor(motor, steps):
    if motor == 1:
        step_pin, dir_pin = STEP_PIN_1, DIR_PIN_1
    else:
        step_pin, dir_pin = STEP_PIN_2, DIR_PIN_2

    direction = CW if steps > 0 else CCW
    GPIO.output(dir_pin, direction)

    for _ in range(abs(steps)):
        GPIO.output(step_pin, GPIO.HIGH)
        sleep(delay)
        GPIO.output(step_pin, GPIO.LOW)
        sleep(delay)

    motor_steps[motor] += steps

try:
    while True:
        motor = int(input("Enter motor number (1 or 2): "))
        if motor not in [1, 2]:
            print("Invalid motor number. Please enter 1 or 2.")
            continue

        steps = int(input("Enter number of steps: "))
        move_motor(motor, steps)
        print(f"Motor 1 position: {motor_steps[1]} steps")
        print(f"Motor 2 position: {motor_steps[2]} steps")

except KeyboardInterrupt:
    print("Program terminated.")

finally:
    GPIO.cleanup()
