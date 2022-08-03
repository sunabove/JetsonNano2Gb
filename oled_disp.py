import sys
from os import path
sys.path.append( path.dirname(path.realpath(__file__)) )

from time import sleep 
import traceback, os, socket, datetime, threading 
import psutil, shutil, numpy as np

from PIL import Image, ImageOps, ImageDraw, ImageFont

import board, busio
import adafruit_ssd1306, adafruit_ina219

print( "Initializaing SSD1306_I2C ...", flush=True )
i2c = busio.I2C(board.SCL, board.SDA)
oled_disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
print( "Initializaing INA219 ...", flush=True )
ina219 = adafruit_ina219.INA219(i2c)

oled_alive = True 
oled_font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMono.ttf", 16, encoding="unic") 
img_path = path.join( path.dirname(path.realpath(__file__)), 'oled_logo.png' )

def stop() :
    global oled_alive
    oled_alive = 0

    w = oled_disp.width
    h = oled_disp.height
    
    image = Image.new('1', [w, h], "WHITE")
    draw = ImageDraw.Draw(image)

    text = "SHUTDOWN"

    size = oled_font.getbbox(text)
    tw = size[2]
    th = size[3]

    # text center align
    x = (w - tw)//2
    y = (h - th)//2
    
    draw.rectangle( [0, 0, w -1, h -1], fill=1, outline = 0)
    draw.text( [x, y], text, font = oled_font, fill = 0) 
    
    oled_disp.image( image )

    oled_disp.invert(1)      # display inverted
    oled_disp.fill( 1 )
    oled_disp.poweroff()
pass # -- stop

pass # -- stop

def start() :
    try:
        global oled_alive

        oled_alive = True 

        # Initialize library.
        
        oled_disp.poweron()
        oled_disp.fill( 0 )
        oled_disp.show()

        oled_disp.invert(1)      # display inverted

        w = oled_disp.width
        h = oled_disp.height

        # open logo image
        print( f"img_path = {img_path}" )         
        logo_image = None

        if path.exists( img_path ) : 
            logo_image = Image.open( img_path )

            im = logo_image
            # convert to grayscale
            logo_image = ImageOps.grayscale( logo_image )
            # rescale to show width height
            logo_image = logo_image.resize( [w, int( im.size[1]*w/im.size[0] ) ] )

            print( f"logo_image size = {logo_image.size}" )
        else :
            print( f"logo image[{img_path}] does not exist." )
        pass

        # Create blank image for drawing.
        image = Image.new('1', [w, h], "WHITE")
        draw = ImageDraw.Draw(image)
        
        def display_oled_info( idx = 0 ) :
            if idx >= 0 : 
                idx = idx % 9
            pass

            text = f""

            if idx < 0 : # shutdown
                text = "SHUTDOWN"
            elif idx == 0 : # current time
                text = datetime.datetime.now().strftime("%p %H:%M:%S")
            elif idx == 1 : # hostname
                hostname = os.popen("hostname").read().strip().split()[0]
        
                text = f"{hostname}"
            elif idx == 2 : # ip address
                hostnames = os.popen("hostname -I").read().strip().split()
                ipaddr = hostnames[0]

                for host in hostnames :
                    if host.startswith( "192." ):
                        ipaddr = host
                        break
                    pass
                pass
        
                text = f"{ipaddr}"
            elif idx == 3 : # disk usage
                # Disk usage

                total, used, free = shutil.disk_usage("/")
                total //= (2**30)
                used //= (2**30)
                free //= (2**30)
                pct = used*100/total

                text = f"Disk: {pct:02.1f}%"
            elif idx == 4 : # CPU
                pct = psutil.cpu_percent()

                text = f"CPU: {pct:02.1f}%"
            elif idx == 5 : # RAM
                pct = psutil.virtual_memory()[2] 

                text = f"RAM: {pct:02.1f}%"
            elif idx == 6 : # VOLTAGE
                text = f"Voltage: {ina219.bus_voltage:.2f}V"
            elif idx == 7 : # VOLTAGE
                text = f"Current: {abs(ina219.current):.0f}mA"
            elif idx == 8 and logo_image is not None : # Logo Image
                # show image by scrolling up by n pixel
                
                size = logo_image.size
                ranges = [ np.arange( 0, size[1] + 1, 1 ), np.arange( size[1], -1, -1 ) ] 
                for rng in ranges : 
                    for y in rng :
                        if not oled_alive :
                            break
                        pass

                        im = Image.new('1', (w, h), 0 ) # create a new blank image
                        im_draw = ImageDraw.Draw( im )
                        im_draw.rectangle( [0, 0, w -1, h -1], fill=1, outline = 1)
                        
                        y2 = y + h 
                        if y2 > logo_image.size[1] :
                            y2 = logo_image.size[1]
                        pass
                        
                        crop = logo_image.crop( [0, y, w, y2 ] )

                        im.paste( crop, box=[0, 0, w, y2 - y ] ) 
                        
                        if oled_alive :
                            oled_disp.image( im )
                            oled_disp.show()
                        pass

                        sleep( 0.1 )
                    pass
                pass
            pass

            print( f"text = {text}")

            if text : 
                # text width
                text_size = oled_font.getbbox(text)
                print( f"text_size = {text_size}" )
                tw = text_size[2]
                th = text_size[3]

                # text center align
                x = (w - tw)//2
                y = (h - th)//2
                
                if x > -1 : 
                    draw.rectangle( [0, 0, w -1, h -1], fill=1, outline = 0)
                    draw.text( [x, y], text, font = oled_font, fill = 0) 

                    oled_disp.image( image )
                    oled_disp.show()
                else :
                    for x in range( 5, - (tw - w + 5*3), -1 ) : 
                        draw.rectangle( [0, 0, w -1, h -1], fill=1, outline = 0)
                        draw.text( [x, y], text, font = oled_font, fill = 0) 

                        oled_disp.image( image )
                        oled_disp.show() 
                        sleep( 0.1 )
                    pass
                pass
                
            pass

            sleep(2.5)

            if idx >= 0 : 
                print ("Turn off screen to prevent heating oled.")
                oled_disp.fill( 1 )
                oled_disp.show()
            pass

            sleep(1)
        pass

        idx = 0
        while oled_alive :
            display_oled_info(idx = idx) 
            idx += 1

            idx %= 1000
        pass

        stop()

    except IOError as e:
        oled_disp.fill( 1 )
        oled_disp.show()

        print(e)    
    except KeyboardInterrupt:
        oled_disp.fill( 1 )
        oled_disp.show()

        print("ctrl + c:")
    finally:
        stop()
    pass
pass  # -- start

import signal
signal.signal( signal.SIGTERM, stop )   

if __name__ == '__main__':
    import sys

    argv = sys.argv

    if len( argv ) > 1 and argv[1] == 'stop' :
        stop()
    else :
        thread = threading.Thread(target=start, daemon=True)
        thread.start()
        thread.join()
    pass
pass