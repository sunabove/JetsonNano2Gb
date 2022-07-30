import board, busio
import adafruit_ina219

i2c = busio.I2C(board.SCL, board.SDA)
ina219 = adafruit_ina219.INA219(i2c)

print( f"Bus Voltage:   {ina219.bus_voltage} V" )
print( f"Shunt Voltage: {ina219.shunt_voltage / 1000 } mV" )
print( f"Current:       {ina219.current} mA" )
