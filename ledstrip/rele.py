import RPi.GPIO as GPIO
import time


PORT=23
GPIO.setmode(GPIO.BCM)
GPIO.setup(PORT, GPIO.OUT)

for i in range(100):
    print("ON")
    GPIO.output(PORT, 1)
    time.sleep(1)
    print("OFF")
    GPIO.output(PORT, 0)
    time.sleep(1)

