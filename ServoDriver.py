import machine
import utime

class ServoDriver():
    def __init__(self):
        # Initialize PWM on pin GP15
        self.servo = machine.PWM(machine.Pin(15))
        self.servo.freq(50)  # Set the frequency to 50Hz
        self.open = False
        self.reset()

    # Function to map angle to duty cycle
    def angle_to_duty(self, angle):
        min_duty = 1638  # Corresponds to 0.5ms pulse (0°)
        max_duty = 8192  # Corresponds to 2.5ms pulse (180°)
        duty = int(min_duty + (angle / 180) * (max_duty - min_duty))
        return duty

    def reset(self):        
        self.servo.duty_u16(self.angle_to_duty(180))
        self.open = False
        
    def isOpen(self):        
        return self.open        
        
    def up(self):
        # Move servo from 180° back to 0°
        for angle in range(180, 90, -1):
            self.servo.duty_u16(self.angle_to_duty(angle))
            utime.sleep_ms(20)
            self.open = True
            
        
    def down(self):
        # Move servo from 0° to 180°
        for angle in range(90, 180, 1):
            self.servo.duty_u16(self.angle_to_duty(angle))
            utime.sleep_ms(20)
            self.open = False
        

def test():
    servo = ServoDriver()

    servo.reset()
    
    print("Open: " + str(servo.isOpen()))
        
    servo.up()
    
    print("Open: " + str(servo.isOpen()))
    
    servo.down()
    
    print("Open: " + str(servo.isOpen()))


if __name__ == "__main__":
    test()
        
                                                             
