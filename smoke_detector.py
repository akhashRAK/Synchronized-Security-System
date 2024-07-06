import RPi.GPIO as GPIO
from time import sleep
GPIO.setmode(GPIO.BCM)
GPIO.setup(21,GPIO.IN)

try:
	while True:
		if GPIO.input(21) == GPIO.LOW:
			print("Smoke detected!!")
		else:
			print(" No Smoke detected!!")
		sleep(1)
		
except KeyboardInterrupt:
	print("Turning off..")
	GPIO.cleanup()			
			
			
