import bluetooth
import random
import struct
import time
from ble_advertising import advertising_payload
from machine import Pin, PWM, I2C
import time
from MotorDriver import MotorDriver
from micropython import const
import ssd1306

#====== setup the I2C communication
i2c = I2C(1, sda=Pin(18), scl=Pin(19))

# Set up the OLED display (128x64 pixels) on the I2C bus
# SSD1306_I2C is a subclass of FrameBuffer. FrameBuffer provides support for graphics primitives.
## http://docs.micropython.org/en/latest/pyboard/library/framebuf.html#
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

def oledClearWhite():
    # Clear the display by filling it with white and then showing the update
    oled.fill(1)
    oled.show()
    time.sleep(1)  # Wait for 1 second

def oledClearBlack():
    # Clear the display again by filling it with black
    oled.fill(0)
    oled.show()
    time.sleep(1)  # Wait for another second


def display(text, row):
    # Display text on the OLED screen
    oled.text(text, 0, row)  # Display at position (0, 0)  
    oled.show()
    #time.sleep(1)  # Wait for 1 second    

buzzer = PWM(Pin(15))


NOTES = {
    'LEFT': 262,
    'RIGHT': 294,
    'SLOW': 330,
    'MEDIUM': 349,
    'FAST': 392,
    'FORWARD': 440,
    'BACK': 494,
    'LOCK_UNLOCK': 523
}

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

_PIANO_UUID = bluetooth.UUID("952cc3a7-1801-4c07-b141-e1e3964f54b5")
_NOTE_CHAR = (
    bluetooth.UUID("ea30277b-d7a5-4eeb-af70-6179c45d7ee6"),
    _FLAG_READ | _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE,
)
_PIANO_SERVICE = (
    _PIANO_UUID,
    (_NOTE_CHAR,),
)

# Global
speed = 100
forward = True
motorDriver = MotorDriver(True)

class BLERobot:
    def __init__(self, ble, name="ble-piano"):
    
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        
        self.speed = 100
        self.forward = True

        handles = self._ble.gatts_register_services((_PIANO_SERVICE,))
        # print("Registered handles:", handles)

        ((self._handle_note,),) = handles
        self._connections = set()

        self._write_callback = None

        self._payload = advertising_payload(name=name, services=[_PIANO_UUID])
        self._advertise()

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            print("New connection", conn_handle)
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            print("Disconnected", conn_handle)
            self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            value = self._ble.gatts_read(value_handle)
            # print("Write event: conn_handle={}, value_handle={}, value={}".format(conn_handle, value_handle, value))
            if value_handle == self._handle_note and self._write_callback:
                self._write_callback(value)
                

    def is_connected(self):
        return len(self._connections) > 0

    def _advertise(self, interval_us=500000):
        print("Starting advertising")
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def on_write(self, callback):
        self._write_callback = callback

def robot_update(data):
    
    global speed, forward
    #print("Receive:", data)

    decoded_data = data.decode('utf-8').rstrip('*\x00')

    print("Receive:", decoded_data)
    
    if (decoded_data == "FORWARD"):
        print("motor FORWARD")
        forward = True
        motorDriver.MotorRun('MA', forward, speed)
        motorDriver.MotorRun('MB', forward, speed)
        motorDriver.MotorRun('MC', forward, speed)
        motorDriver.MotorRun('MD', forward, speed)
        time.sleep(1) 
        decoded_data = "STOP"        
                        
    if (decoded_data == "BACK"):
        print("motor BACK")
        forward = False
        motorDriver.MotorRun('MA', forward, speed)
        motorDriver.MotorRun('MB', forward, speed)
        motorDriver.MotorRun('MC', forward, speed)
        motorDriver.MotorRun('MD', forward, speed)
        time.sleep(1) 
        decoded_data = "STOP"        
        
    if (decoded_data == "X_LEFT"):
        print("motor LEFT")
        motorDriver.MotorRun('MA', forward, speed * 0.25)
        motorDriver.MotorRun('MB', forward, speed)
        motorDriver.MotorRun('MC', forward, speed * 0.25)
        motorDriver.MotorRun('MD', forward, speed)
        time.sleep(1) 
        decoded_data = "STOP"        
        
    if (decoded_data == "X_RIGHT"):
        print("motor RIGHT")
        motorDriver.MotorRun('MA', forward, speed)
        motorDriver.MotorRun('MB', forward, speed * 0.25)
        motorDriver.MotorRun('MC', forward, speed)
        motorDriver.MotorRun('MD', forward, speed * 0.25)
        time.sleep(1) 
        decoded_data = "STOP"        

    if (decoded_data == "LEFT"):
        print("motor SPIN LEFT")
        motorDriver.MotorRun('MA', not forward, speed)
        motorDriver.MotorRun('MB', forward, speed)
        motorDriver.MotorRun('MC', not forward, speed)
        motorDriver.MotorRun('MD', forward, speed)
        time.sleep(1) 
        decoded_data = "STOP"        

    if (decoded_data == "RIGHT"):
        print("motor SPIN RIGHT")
        motorDriver.MotorRun('MA', forward, speed)
        motorDriver.MotorRun('MB', not forward, speed)
        motorDriver.MotorRun('MC', forward, speed)
        motorDriver.MotorRun('MD', not forward, speed)
        time.sleep(1) 
        decoded_data = "STOP"        
        
    if (decoded_data == "FAST"):
        print("motor FAST")
        speed = 100        
        motorDriver.MotorRun('MA', forward, speed)
        motorDriver.MotorRun('MB', forward, speed)
        motorDriver.MotorRun('MC', forward, speed)
        motorDriver.MotorRun('MD', forward, speed)
        time.sleep(1) 
        decoded_data = "STOP"        
        
    if (decoded_data == "SLOW"):
        print("motor SLOW")
        speed = 60
        motorDriver.MotorRun('MA', forward, speed)
        motorDriver.MotorRun('MB', forward, speed)
        motorDriver.MotorRun('MC', forward, speed)
        motorDriver.MotorRun('MD', forward, speed)
        time.sleep(1) 
        decoded_data = "STOP"
        
    if (decoded_data == "STOP"):
        print("motor A stop")
        motorDriver.MotorStop('MA')  
        motorDriver.MotorStop('MB')
        motorDriver.MotorStop('MC')
        motorDriver.MotorStop('MD') 
                
    if (decoded_data == "ORANGE"):
        print("BUY ORANGES")   
        display("Oranges", 0)
        
    if (decoded_data == "APPLE"):
        print("BUY APPLES")
        display("Apples", 16)
        
    if (decoded_data == "ICECREAM"):
        print("BUY ICE CREAM")
        display("Ice Cream", 32)
        
    if (decoded_data == "CAKE"):
        print("BUY CAKE")
        display("Cake", 48)
        
    if (decoded_data == "EMPTY_CART"):
        print("EMPTY CART")
        oledClearBlack()
                   
        

def demo():
    ble = bluetooth.BLE()
    robot = BLERobot(ble,"pico2w")
    
    oledClearBlack()
    
    #display("Hello robot!", 0)
    time.sleep(1) 

    oledClearBlack()
        
    try:
        
        while True:
            if robot.is_connected():
                robot.on_write(robot_update)        
        
    except KeyboardInterrupt:
        motorDriver.MotorStop('MA')
        motorDriver.MotorStop('MB')
        motorDriver.MotorStop('MC')
        motorDriver.MotorStop('MD')
        
        oledClearBlack()
        
        exit()


if __name__ == "__main__":
    demo()
