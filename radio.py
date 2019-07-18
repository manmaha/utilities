import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
amp_on = 17
switch = 27
GPIO.setup(switch, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(amp_on, GPIO.OUT)

on = lambda x : GPIO.output(x,GPIO.HIGH)
off = lambda x : GPIO.output(x,GPIO.LOW)
toggle = lambda x : GPIO.output(x, not GPIO.input(x))

def main():
while True:
  GPIO.output(amp_on,GPIO.input(switch))
  sleep(2)
  
      




if __name__ == "__main__":
    main()