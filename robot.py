# Robot Routines
# Manish Mahajan
# 4 Sep 2017

import RPi.GPIO as GPIO
import time
from sys import argv
import sensors
import motors
import signal
import sys


Obstruction_Type = ['LEFT', 'STRAIGHT', 'RIGHT']
Obstruction_Tolerance = 15.00 # in cm
Backup_Time = 0.5 # in seconds
Backup_Speed =  15

roaming = False # is the robot roaming or stationary

# Robot is an object comprising of a list of sensors and actuators 
# methods are actions that a robot is capable of

class robot(object):
  def __init__(self,motors, sensors):
    self.motors = motors
    self.sensors = sensors
    pass
  
  #motion methods
  def stop(self):
    for m in self.motors:
      m.stop()
    pass
  
  #forward/backward motion
  def move_straight(self,speed=motors.MAXSPEED,direction=True, runTime=motors.FOREVER):
    motors.timed_move(self.motors,speed,direction,runTime)
    pass

  def move_back(self,speed=motors.MAXSPEED,direction=True,runTime=motors.FOREVER):
    motors.timed_move(self.motors,speed,False,runTime)
    pass

  #Sensor methods
  def sense(self):
    #returns list of sensor readings, in this case distance readings
    # of left, front and right sensor
    values=[]
    for sensor in self.sensors:
      values.append(sensor.sense())
    print('Sensor Readings are :', values)
    return values
  
class RobotOne(robot): # simple 2 wheeled robot
# has two motors
# has three ultrasonic sensors
  def __init__(self,motors,sensors):
    super(RobotOne,self).__init__(motors,sensors) #do all the usual set up
    self.motors = motors
    self.sensors = sensors
    self.leftMotor=motors[0]
    self.rightMotor=motors[1]
    self.leftSensor = sensors[0]
    self.frontSensor = sensors[1]
    self.rightSensor = sensors[2]
    self.values = self.sense() # sensor values
    pass  
  
  #motion methods
  def move_left(self,speed,direction=True,runTime=motors.FOREVER):
  # move back if direction False and put time for short move
    self.leftMotor.stop()
    self.rightMotor.forward(speed,direction)
    if runTime != motors.FOREVER:
      start_time = time.time()
      end_time = start_time
      while end_time - start_time < runTime:
        end_time = time.time()  
      for m in self.motors : m.stop()

  def avoid_right(self):
    self.move_left(Backup_Speed*0.5,True,Backup_Time*0.5)
    pass
  
  def move_right(self,speed, direction=True,runTime=motors.FOREVER):
  # move back if direction False and put time for short move  
    self.rightMotor.stop()
    self.leftMotor.forward(speed,direction)
    if runTime != motors.FOREVER:
      start_time = time.time()
      end_time = start_time
      while end_time - start_time < runTime:
        end_time = time.time()  
      for m in self.motors : m.stop()  

  def avoid_left(self):
    self.move_right(Backup_Speed*0.5,True,Backup_Time*0.5)
    pass
  
  def avoid_front(self):
  # avoid obstacle to the front
   self.move_back(Backup_Speed*2,True,Backup_Time*2)# go back far away
   values = self.sense()
   self.stop() 
   if values[0]>values[2]: #right obstacle is closer
     self.avoid_right()
   else:
     self.avoid_left()
   pass

  def stop(self):
  # stops all motors
    for m in self.motors : 
      m.brake()
      m.stop()      

  def obstruction(self):
  # returns, False for no obstruction, 'LEFT','FORWARD','RIGHT' for left, forward and right
    values = self.sense()
    if min(values) > Obstruction_Tolerance:
      print ('no obstruction found')
      return False
    else:
      print ('obstruction type', Obstruction_Type[values.index(min(values))])
      return Obstruction_Type[values.index(min(values))]  
    pass
  
  def back_up(self, obstruction_type):
  # back up if an obstruction of obstruction_type is found
    if obstruction_type: # not False
      self.stop()
      chooser = {
        'LEFT':self.avoid_left,
        'RIGHT':self.avoid_right,
        'STRAIGHT':self.avoid_front
        }
      chooser[obstruction_type]()
      self.back_up(self.obstruction())  
      pass

  def roam(self):
  # robot roams and avoids obstacles
    self.back_up(self.obstruction()) 
    self.move_straight(motors.MAXSPEED*0.4,True,1.5)
     

def signal_handler(signum, frame):
        print('You pressed Ctrl+C!')
        GPIO.cleanup()
        sys.exit(0)    

def button_handler(pin):
	global roaming
	roaming = not roaming
        
def main():
  # test and run the the Robot
  # motor GPIO Pins
  GPIO.setmode(GPIO.BCM)
  GPIO.setwarnings(False)
  StdByPin = 14  # this is the common pin
  leftMotorPins = [12,23,24] # fill up with GPIO pins, PWMA, AIn1, AIn2
  rightMotorPins = [13,25,26] # same as above
  leftMotorPins.append(StdByPin)
  rightMotorPins.append(StdByPin)
  
  #Sensor GPIO Pins
  trig = 4     # common trig pin
  echo_left = 17 #left sensor echo pin
  echo_fwd = 27 #forward sensor echo pin
  echo_right = 22   #right sensor echo pin
  
  #button pins
  button_pin = 18
  GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  
  #set up motors and sensors
  Motors = [motors.motor(leftMotorPins,'Left'),motors.motor(rightMotorPins,'Right')]
  Sensors = [sensors.ultrasonic_sensor([trig,echo_left]), sensors.ultrasonic_sensor([trig,echo_fwd]), sensors.ultrasonic_sensor([trig,echo_right])]
  
  #set up robot
  PiOde = RobotOne(Motors,Sensors)
  
  signal.signal(signal.SIGINT, signal_handler)
  
  
  GPIO.add_event_detect(button_pin, GPIO.RISING, bouncetime = 200)
  GPIO.add_event_callback(button_pin, button_handler)
  #previous_button_state = False
  while True: # do forever
    #button,previous_button_state = buttons.button_pressed(button_pin,previous_button_state)
    if roaming:
      PiOde.roam()
      print('roaming')
    else:
      PiOde.stop()
      print('stopped')
  
  
  GPIO.cleanup()


if __name__ == "__main__":
    main()
