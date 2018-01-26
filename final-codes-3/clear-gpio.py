import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.output(13, False)
GPIO.output(11, False)
GPIO.output(18, False)

GPIO.cleanup()
