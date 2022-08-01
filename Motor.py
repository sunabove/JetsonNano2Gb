#coding: utf-8
import Jetson.GPIO as GPIO
import inspect
from time import sleep, time
from math import sqrt

import logging as log
log.basicConfig(
    format='%(asctime)s, %(levelname)-8s [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO
    )

class Motor:

    def __init__(self, ain1=12, ain2=13, ena=6, bin1=20, bin2=21, enb=26, debug=False):
        self.debug = debug

        self.min_speed = 10
        
        self.AIN1 = ain1; self.AIN2 = ain2; self.ENA = ena
        self.BIN1 = bin1; self.BIN2 = bin2; self.ENB = enb
        
        GPIO.setmode(GPIO.BCM)
        for port in [ ain1, ain2, ena, bin1, bin2, enb ] : 
            GPIO.setup(port,GPIO.OUT)
        pass

        self.PWMA = GPIO.PWM(ena, 500)
        self.PWMB = GPIO.PWM(enb, 500)

        self.PA = self.min_speed
        self.PB = self.min_speed

        self.mode = "stop"

        self.PWMA.start( self.PA )
        self.PWMB.start( self.PA ) 

        self.stop()
    pass

    def __del__( self ) :
        self.finish()
    pass

    def finish(self) : 
        log.info(inspect.currentframe().f_code.co_name)

        self._speed = 0 

        if hasattr( self, "PWMA" ) : 
            self.PWMA and self.PWMA.stop()
        pass

        if hasattr( self, "PWMB") :
            self.PWMB and self.PWMB.stop(0)
        pass

        self.PWMA = None
        self.PWMB = None

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        for port in [ self.AIN1, self.AIN2, self.ENA, self.BIN1, self.BIN2, self.ENB ] : 
            GPIO.setmode(GPIO.BCM)
            GPIO.cleanup(port)
        pass
    pass

    def speed_left(self) :
        return self.PA
    pass

    def speed_right(self) :
        return self.PB
    pass

    def speed_min(self) :
        return self.min_speed
    pass

    def speed_down(self, dv = 5) : # 속도 증가
        self.speed_up( -dv )
    pass

    def speed_up(self, dv = 5) : # 속도 증가

        mode = self.mode

        log.info( f"before PA = {self.PA}, right={self.PB}, dv={dv}")

        if mode == "stop" :
            return 
        pass

        left = self.PA + dv

        left = min( max(left, 0 ), 100 )

        self.PA = left

        right = self.PB + dv

        right = min( max(right, 0), 100 )

        self.PB = right

        log.info( f"after PA = {self.PA}, right={self.PB}, dv={dv}")

        if self.PA == 0 and self.PB == 0 :
            self.stop()
        elif mode =="forward" :
            self.forward()
        elif mode == "backward" :
            self.backward()
        elif mode == "left" :
            self.left()
        elif mode == "right" :
            self.right()
        elif mode == "stop" :
            self.stop()
        pass
    pass # -- speed_up

    def forward(self, left=None, right=None):
        self.debug and log.info(inspect.currentframe().f_code.co_name)

        self.mode = "forward" 

        if left is None :
            left = self.min_speed
        pass

        self.move( left, right )
    pass # -- forward
    
    def move(self, left = None, right=None):
        # self.debug and log.info(inspect.currentframe().f_code.co_name)
        
        if left is None :
            left = self.PA
        pass

        if right is None :
            right = left
        pass

        if self.PWMA is None or self.PWMB is None :
            return
        pass

        self.PA = left
        self.PB = right

        self.PWMA.ChangeDutyCycle( abs( left ) )
        self.PWMB.ChangeDutyCycle( abs( right ) )

        if left >= 0 :
            GPIO.output(self.AIN1, GPIO.LOW)
            GPIO.output(self.AIN2, GPIO.HIGH)
        else :
            GPIO.output(self.AIN1, GPIO.HIGH)
            GPIO.output(self.AIN2, GPIO.LOW)
        pass
        
        if right >= 0 : 
            GPIO.output(self.BIN1, GPIO.LOW)
            GPIO.output(self.BIN2, GPIO.HIGH)
        else :
            GPIO.output(self.BIN1, GPIO.HIGH)
            GPIO.output(self.BIN2, GPIO.LOW)
        pass
    pass

    def backward(self, left=None, right=None):
        self.debug and log.info(inspect.currentframe().f_code.co_name)

        self.mode = "backward"
        min_speed = self.min_speed

        if left is None :
            left = max( abs( self.PA ), self.min_speed )
        pass

        if left is not None and right is None :
            right = left
        pass

        self.move( -left, -right )
    pass 

    def left(self, turn_speed=20):
        self.debug and log.info(inspect.currentframe().f_code.co_name)

        self.mode = "left" 

        if turn_speed is None :
            turn_speed = 20
        pass

        self.move( -turn_speed, turn_speed )
    pass 

    def right(self, turn_speed=20):
        self.debug and log.info(inspect.currentframe().f_code.co_name)

        self.mode = "right"

        if turn_speed is None :
            turn_speed = 20
        pass

        self.move( turn_speed, -turn_speed )
    pass

    def stop_motor(self):
        self.stop()
    pass

    def stop(self):
        self.debug and log.info(inspect.currentframe().f_code.co_name)

        self.mode = "stop"

        if self.PWMA :
            self.PWMA.ChangeDutyCycle(0)        
            GPIO.output(self.AIN1, GPIO.LOW)
            GPIO.output(self.AIN2, GPIO.LOW)
        pass

        if self.PWMB :
            self.PWMB.ChangeDutyCycle(0)        
            GPIO.output(self.BIN1, GPIO.LOW)
            GPIO.output(self.BIN2, GPIO.LOW)
        pass

        self.PA = 0
        self.PB = 0
    pass

    def back(self) :
        self.backward()
    pass 

    def test_all(self, duration=4) :    
        self.forward()
        sleep(duration)
        self.backward()
        sleep(duration)
        self.left()
        sleep(duration)
        self.right()
        sleep(duration)
        self.stop()
    pass

pass

if __name__=='__main__':
    log.info( "Hello" )

    GPIO.setwarnings(False)
    GPIO.cleanup()
    
    motor = Motor(debug=True)

    try:
        motor.test_all(duration=3)        
    except KeyboardInterrupt:
        print( "" )
    pass 
    
    motor.finish()
    
    sleep( 0.5 )

    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup()

    log.info( "Good bye!" )
pass
