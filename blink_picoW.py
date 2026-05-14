import machine
import time

greenledPin = 0 #"Green LED"
greenled = machine.Pin(greenledPin, machine.Pin.OUT)


redledPin = 1 #"Red LED"
redled = machine.Pin(redledPin, machine.Pin.OUT)

while True:
  greenled.value(True)  #turn on the LED
  time.sleep(1)   #wait for one second
  greenled.value(False)  #turn off the LED
  time.sleep(1)   #wait for one second
  # comment change green light
  redled.value(True)  #turn on the LED
  time.sleep(1)   #wait for one second
  redled.value(False)  #turn off the LED
  time.sleep(1)   #wait for one second