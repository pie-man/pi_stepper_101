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

    def __init__(self, pins):
        self.pins = pins
        for pin in pins:
            GPIO.setup(pin, GPIO.OUT)
        self.step = 0

    def advance(self):
        step = self.step + 1
        if step >= len(self.seq):
            step = 0
        self.setStep(self.seq[step])
        self.step = step 
        
    def retard(self):
        step = self.step - 1
        if step < 0:
            step = len(self.seq) - 1
        self.setStep(self.seq[step])
        self.step = step 
        
    def move(self,direction):
        if direction > 0:
            self.advance()
        else:
            self.retard()

    def setStep(self,state):
        for count, pin in enumerate(self.pins):
            GPIO.output(pin, state[count])

def main():
    motors = {"a":StepperMotor((17,18,27,22)),
              "b":StepperMotor((23,24,25,4))}
    
    def counterclockwise(delay, steps):  
      for i in range(0, steps):
        for step in range(len(StepperMotor.seq)):
            motors["a"].advance()
            motors["b"].advance()
            time.sleep(delay)
    
    def clockwise(delay, steps):  
      for i in range(0, steps):
        for step in range(len(StepperMotor.seq)):
            motors["a"].retard()
            motors["b"].retard()
            time.sleep(delay)
    
    def opposite_1(delay, steps):
      for i in range(0, steps):
        for step in range(len(StepperMotor.seq)):
            motors["a"].advance()
            motors["b"].retard()
            time.sleep(delay)
    
    def opposite_2(delay, steps):
      for i in range(0, steps):
        for step in range(len(StepperMotor.seq)):
            motors["a"].retard()
            motors["b"].advance()
            time.sleep(delay)

    try:
      while True:
        delay = raw_input("Delay between steps (milliseconds)?")
        if delay == '':
            print "Bye...."
            GPIO.cleanup()
            break
        steps = raw_input("How many steps counterclockwise? ")
        counterclockwise(int(delay) / 1000.0, int(steps))
        steps = raw_input("How many steps clockwise? ")
        clockwise(int(delay) / 1000.0, int(steps))
        steps = raw_input("How many steps opposite? ")
        opposite_1(int(delay) / 1000.0, int(steps))
        steps = raw_input("How many steps back again? ")
        opposite_2(int(delay) / 1000.0, int(steps))
        steps = raw_input("How many steps for random boogie? ")
        limit = int(steps)
        count = 0
        pos_a = 0
        pos_b = 0
        while count < limit:
            if count % 100 == 0:
                if random() < 0.5:
                    direction_a = 1
                else:
                    direction_a = -1
                if random() < 0.5:
                    direction_b = 1
                else:
                    direction_b = -1
                print("direction_a = {0:4d}, direction_b = {1:4d}".format(direction_a,direction_b))
            count += 1
            motors["a"].move(direction_a)
            pos_a += direction_a
            motors["b"].move(direction_b)
            pos_b += direction_b
            time.sleep(int(delay)/1000.0)
        if pos_a != 0:
            direction_a = 0 - (pos_a / abs(pos_a))
        if pos_b != 0:
            direction_b = 0 - (pos_b / abs(pos_b))
        print("pos_a = {0:4d}, pos_b = {1:4d}".format(pos_a,pos_b))
        while abs(pos_a) > 0 or abs(pos_b) > 0:
            if pos_a != 0:
                motors["a"].move(direction_a)
                pos_a += direction_a
            if pos_b != 0:
                motors["b"].move(direction_b)
                pos_b += direction_b
            time.sleep(int(delay)/1000.0)
        print("pos_a = {0:4d}, pos_b = {1:4d}".format(pos_a,pos_b))
    except:
        GPIO.cleanup()
        raise

if __name__ == "__main__":
    main()
