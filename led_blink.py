import Jetson.GPIO as GPIO
import time
led_pin = 33
GPIO.setmode(GPIO.BOARD)
GPIO.setup(led_pin, GPIO.OUT)
print("Press CTRL+C when you want the LED to stop blinking")
duration = 3
while True:
    time.sleep(duration)
    GPIO.output(led_pin, GPIO.HIGH)
    print("LED is ON")
    time.sleep(duration)
    GPIO.output(led_pin, GPIO.LOW)
    print("LED is OFF")
