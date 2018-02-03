import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.output(11, False)
GPIO.output(13, False)
GPIO.setup(35, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(37, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
while True:
      if(GPIO.input(35) == 1):
            GPIO.output(13, True)
            GPIO.output(11, False)
      elif(GPIO.input(37)== 1):
            GPIO.output(11, True)
            GPIO.output(13, False)
