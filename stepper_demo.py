import RPi.GPIO as GPIO
import time
from random import random

GPIO.setmode(GPIO.BCM)

class StepperMotor(object):
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
        self.pins = pins
        for pin in pins:
            GPIO.setup(pin, GPIO.OUT)
        self.step = 0
        self.seq = sequence
        self.seq_len = len(sequence)

    def advance(self):
        step = self.step + 1
        if step >= self.seq_len:
            step = 0
        self.MoveStep(self.seq[step])
        self.step = step 
        
    def retard(self):
        step = self.step - 1
        if step < 0:
            step = self.seq_len - 1
        self.MoveStep(self.seq[step])
        self.step = step 
        
    def move(self,direction):
        if direction > 0:
            self.advance()
        else:
            self.retard()

    def MoveStep(self,state):
        for count, pin in enumerate(self.pins):
            GPIO.output(pin, state[count])

motors = {"a":StepperMotor((17,18,27,22)),
          "b":StepperMotor((23,24,25,4))}

def counterclockwise(delay, steps):  
  for i in range(0, steps):
    for step in range(motors["a"].seq_len):
        motors["a"].advance()
        motors["b"].advance()
        time.sleep(delay)

def clockwise(delay, steps):  
  for i in range(0, steps):
    for step in range(motors["a"].seq_len):
        motors["a"].retard()
        motors["b"].retard()
        time.sleep(delay)

def opposite_1(delay, steps):
  for i in range(0, steps):
    for step in range(motors["a"].seq_len):
        motors["a"].advance()
        motors["b"].retard()
        time.sleep(delay)

def opposite_2(delay, steps):
  for i in range(0, steps):
    for step in range(motors["a"].seq_len):
        motors["a"].retard()
        motors["b"].advance()
        time.sleep(delay)

def boogie_chunk(delay=0.001, steps=1, dir_a=1, dir_b=1):
  for i in range(0, steps):
    for step in range(motors["a"].seq_len):
        motors["a"].move(dir_a)
        motors["b"].move(dir_b)
        time.sleep(delay)
  return

def reset_to_start(delay=0.001, pos_a=1, pos_b=1, full_circle=510):
    (steps_a, dir_a) = quickest_route(pos_a, full_circle)
    (steps_b, dir_b) = quickest_route(pos_b, full_circle)
    print("steps_a = {0:4d}, steps_b = {1:4d}".format(steps_a,steps_b))
    first_part = min(steps_a, steps_b) + int(0.5 * abs(steps_a - steps_b))
    print("pos_a = {0:4d}, pos_b = {1:4d}".format(pos_a,pos_b))
    print("first_part = {0:4d} : dir_a = {1:4d}, dir_b = {2:4d}".format(first_part, dir_a, dir_b))
    boogie_chunk(delay, first_part, dir_a, dir_b)
    if steps_a > steps_b:
        dir_b = 0 - dir_b
    else:
        dir_a = 0 - dir_a
    second_part = int(0.5 * abs(steps_a - steps_b))
    print("second_part = {0:4d} : dir_a = {1:4d}, dir_b = {2:4d}".format(second_part, dir_a, dir_b))
    boogie_chunk(delay, second_part, dir_a, dir_b)
    return

def quickest_route(position, full_circle=510):
    pos = position % full_circle
    dir = pos - int(0.5 * full_circle)
    dir = dir / abs(dir)
    if dir < 0 or pos == 0:
        steps = pos
    else:
        steps = full_circle - pos
    return (steps, dir)

def set_rand_dir():
    if random() < 0.5:
        direction = 1
    else:
        direction = -1
    return direction

def main():
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
        limit = steps
        count = 0
        chunk = 100
        pos_a = 0
        pos_b = 0
        while steps > 0:
            if (limit - steps) % chunk == 0:
                direction_a = set_rand_dir()
                direction_b = set_rand_dir()
                print("direction_a = {0:4d}, direction_b = {1:4d}".format(direction_a,direction_b))
            if steps > chunk:
                shift = chunk
            else:
                shift = steps
            boogie_chunk(delay, shift, direction_a, direction_b)
            steps -= shift
            pos_a += direction_a * shift
            pos_b += direction_b * shift
        reset_to_start(delay, pos_a, pos_b)
    except:
        GPIO.cleanup()
        raise

if __name__ == "__main__":
    main()
