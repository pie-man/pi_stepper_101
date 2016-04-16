import RPi.GPIO as GPIO
import time
from random import random

GPIO.setmode(GPIO.BCM)

class StepperMotor(object):
    """Class for a stepper motor. Defines the pin sequence for
       movement and provides basic movement methods"""
    seq = [
           [1,0,0,0],
           [1,1,0,0],
           [0,1,0,0],
           [0,1,1,0],
           [0,0,1,0],
           [0,0,1,1],
           [0,0,0,1],
           [1,0,0,1]
          ]

    def __init__(self, pins, sequence=seq):
        """Initialises the GPIO pins for the motor"""
        self.pins = pins
        for pin in pins:
            GPIO.setup(pin, GPIO.OUT)
        self.step = 0
        self.seq = sequence
        self.seq_len = len(sequence)

    def advance(self):
        """Moves once through the entire pin sequence forwards"""
        step = self.step + 1
        if step >= self.seq_len:
            step = 0
        self.SetState(self.seq[step])
        self.step = step 
        
    def retard(self):
        """Moves once through the entire pin sequence backwards"""
        step = self.step - 1
        if step < 0:
            step = self.seq_len - 1
        self.SetState(self.seq[step])
        self.step = step 
        
    def move(self,direction):
        """Moves once through the entire pin sequence in
           a direction provided. +ve for 'forwards' -ve for backwards"""
        if direction > 0:
            self.advance()
        else:
            self.retard()

    def SetState(self,state):
        """Sets the pins to a provided state"""
        for count, pin in enumerate(self.pins):
            GPIO.output(pin, state[count])


# Initialise the 2 stepper motors on a 4tronix PiStep Dual Motor control board
motors = {"a":StepperMotor((17,18,27,22)),
          "b":StepperMotor((23,24,25,4))}

def counterclockwise(delay=0.001, steps=100):  
    """Move both motors 'forawrds' steps times through the pin sequence,
       which was counterclockwise for me."""
    for i in range(0, steps):
        for step in range(motors["a"].seq_len):
            motors["a"].advance()
            motors["b"].advance()
            time.sleep(delay)

def clockwise(delay=0.001, steps=100):  
    """Move both motors 'backwards' steps times through the pin sequence,
       which was clockwise for me."""
    for i in range(0, steps):
        for step in range(motors["a"].seq_len):
            motors["a"].retard()
            motors["b"].retard()
            time.sleep(delay)

def opposite_1(delay=0.001, steps=100):
    """Move both motors in opposite directions steps times through
       the pin sequence"""
    for i in range(0, steps):
        for step in range(motors["a"].seq_len):
            motors["a"].advance()
            motors["b"].retard()
            time.sleep(delay)

def opposite_2(delay=0.001, steps=100):
    """Move both motors in opposite directions steps times through
       the pin sequence"""
    for i in range(0, steps):
        for step in range(motors["a"].seq_len):
            motors["a"].retard()
            motors["b"].advance()
            time.sleep(delay)

def boogie_chunk(delay=0.001, steps=100, dir_a=1, dir_b=1):
    """Move both motors in given directions steps times through
       the pin sequence"""
    for i in range(0, steps):
        for step in range(motors["a"].seq_len):
            motors["a"].move(dir_a)
            motors["b"].move(dir_b)
            time.sleep(delay)
    return

def reset_to_start(delay=0.001, pos_a=1, pos_b=1, full_circle=510):
    """Given a current position and the number of 'steps' taken to perform a
       full circle, return to the 'zero' position"""
    (steps_a, dir_a) = quickest_route(pos_a, full_circle)
    (steps_b, dir_b) = quickest_route(pos_b, full_circle)
    first_part = min(steps_a, steps_b) + int(0.5 * abs(steps_a - steps_b))
    boogie_chunk(delay, first_part, dir_a, dir_b)
    if steps_a > steps_b:
        dir_b = 0 - dir_b
    else:
        dir_a = 0 - dir_a
    second_part = int(0.5 * abs(steps_a - steps_b))
    boogie_chunk(delay, second_part, dir_a, dir_b)
    return

def quickest_route(position, full_circle=510):
    """Given a position and the number of 'steps' taken to perform a full circle.
       calculate the quickest route back to the 'zero' position,
       and the direction to take"""
    pos = position % full_circle
    dir = pos - int(0.5 * full_circle)
    dir = dir / abs(dir)
    if dir < 0 or pos == 0:
        steps = pos
    else:
        steps = full_circle - pos
    return (steps, dir)

def set_rand_dir():
    """Pick a random direction"""
    if random() < 0.5:
        direction = 1
    else:
        direction = -1
    return direction

def boogie_control(delay=0.001, limit=1000, chunk=25):
    """Perform a given number of full steps as a series of 'chunks' in a random
       direction. Then return to starting point"""
    pos_a = 0
    pos_b = 0
    steps = limit
    while steps > 0:
        if (limit - steps) % chunk == 0:
            direction_a = set_rand_dir()
            direction_b = set_rand_dir()
        if steps > chunk:
            shift = chunk
        else:
            shift = steps
        boogie_chunk(delay, shift, direction_a, direction_b)
        steps -= shift
        pos_a += direction_a * shift
        pos_b += direction_b * shift
    reset_to_start(delay, pos_a, pos_b)

def demo():
    """Demo the main movement functions"""
    try:
        while True:
            int_delay = raw_input("Delay between steps (milliseconds)?")
            if int_delay == '':
                print "Bye...."
                GPIO.cleanup()
                break
            else:
                delay = int(int_delay) / 1000.0
            steps = int(raw_input("How many steps counterclockwise? "))
            counterclockwise(delay, steps)
            steps = int(raw_input("How many steps clockwise? "))
            clockwise(delay, steps)
            steps = int(raw_input("How many steps opposite? "))
            opposite_1(delay, steps)
            steps = int(raw_input("How many steps back again? "))
            opposite_2(delay, steps)
            steps = int(raw_input("How many steps for random boogie? "))
            boogie_control(delay,steps)
    except:
        GPIO.cleanup()
        raise

if __name__ == "__main__":
    demo()
