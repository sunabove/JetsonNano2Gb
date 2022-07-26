import os, board, busio
import adafruit_ina219

address = os.popen("i2cdetect -y -r 1 0x42 0x42 | egrep '42' | awk '{print $2}'").read().strip() 
print( f"address = {address}")

i2c = busio.I2C(board.SCL, board.SDA)
ina219 = adafruit_ina219.INA219(i2c)

num = 0.02893574
print (f'{num:.4f}')

print( f"Bus Voltage:   {ina219.bus_voltage:.2f} V" )
print( f"Shunt Voltage: {ina219.shunt_voltage / 1000 } mV" )
print( f"Current:       {ina219.current:.2f} mA" )
