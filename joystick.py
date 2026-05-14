import machine  # Import hardware control module
import time  # Import time module


class Joystick(object):
    
    def __init__(self):
        
        
        GP27 = 27
        GP26 = 26
        GP22 = 22
        # Initialize X and Y axes of the joystick
        self.x_joystick = machine.ADC(GP27)
        self.y_joystick = machine.ADC(GP26)

        # Initialize joystick switch with pull-up resistor
        self.z_switch = machine.Pin(GP22, machine.Pin.IN, machine.Pin.PULL_UP)
        
        self.x_point = 0        
        self.y_point = 0
        self.z_point = 0

    def scan(self):
        
        x = self.x_joystick.read_u16()  # Read X-axis value
        y = self.y_joystick.read_u16()  # Read Y-axis value
        z = self.z_switch.value()  # Read switch state

        # Print joystick values and switch state
        #print("X: ", x, " Y: ", y)
        #print("SW: ", z)
        
        if (x > 40000):
            print("DOWN")
            if self.x_point < 50:            
                self.x_point = self.x_point + 1
            
        if (x < 30000):
            print("UP")
            if self.x_point > -50:            
                self.x_point = self.x_point - 1
            
        if (y > 40000):
            print("LEFT")
            if self.y_point > -50:
                self.y_point = self.y_point - 1
            
        if (y < 20000):
            print("RIGHT")
            if self.y_point < 50:
                self.y_point = self.y_point + 1
                
        if (z == 0):
            print("FIRE!")
            self.z_point = True
        else:
            self.z_point = False
            
        result = (self.x_point, self.y_point, self.z_point)
        
        return result
            
def main():
    
    joystick = Joystick()
        
    while True:
        point = joystick.scan()
        
        print(point)
        
        time.sleep_ms(100)
        
if __name__ == "__main__":
    main()            
                
                
