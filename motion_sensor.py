from gpiozero import MotionSensor
from signal import pause
motion_sensor= MotionSensor(4)
def motion():
    print("Motion detected")
def no_motion():
    print("No motion")
print("Readying motion sensor..")
motion_sensor.wait_for_no_motion()
print("Sensor ready")

motion_sensor.when_motion= motion
motion_sensor.when_no_motion= no_motion

pause()
    
