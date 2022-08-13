import inputs

pads = inputs.devices.gamepads

if len(pads) < 1 :
    raise Exception("Couldn't find any Gamepads!")
else :
    print( "Gamepads found." )
pass

print( "Power on the joystick and press any key!" )
idx = 0 
while True:
    events = inputs.get_gamepad()
    for e in events:
        print( f"[{idx:04d}] CODE: {e.code}, STATE: {e.state}, TYPE: {e.ev_type}" )
        idx += 1
    pass
pass