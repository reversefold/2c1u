import os
import time

import board
import digitalio
import neopixel
import supervisor

print("listening...")

RED = (255, 0, 0)
# YELLOW = (255, 150, 0)
# GREEN = (0, 255, 0)
# CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
# WHITE = (255, 255, 255)
# OFF = (0, 0, 0)

try:
    os.stat("work")
    WORK = True
    print("work")
except OSError:
    WORK = False

MAIN = not WORK

if MAIN:
    try:
        import adafruit_displayio_ssd1306
        import adafruit_display_text.label
        import displayio
        import terminalio

        displayio.release_displays()
        i2c = board.I2C()
        display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
        display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)
    except RuntimeError as exc:
        print("Error initializing display: %r" % (exc,))
        display = None


def update_display(text):
    if not display:
        return
    # Make the display context
    splash = displayio.Group()
    display.show(splash)

    color_bitmap = displayio.Bitmap(128, 32, 1)
    color_palette = displayio.Palette(1)
    color_palette[0] = 0xFFFFFF  # White

    bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
    splash.append(bg_sprite)

    # Draw a smaller inner rectangle
    inner_bitmap = displayio.Bitmap(118, 24, 1)
    inner_palette = displayio.Palette(1)
    inner_palette[0] = 0x000000  # Black
    inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=5, y=4)
    splash.append(inner_sprite)

    # Draw a label
    text_area = adafruit_display_text.label.Label(terminalio.FONT, text=text, color=0xFFFF00, x=int(128 / 2 - len(text) / 2 * 6), y=15)
    splash.append(text_area)


if MAIN:
    button = digitalio.DigitalInOut(board.D5)
    button.switch_to_input(pull=digitalio.Pull.DOWN)


if MAIN:
    pixels = neopixel.NeoPixel(board.D6, 8 * 4, brightness=0.05, auto_write=False)
    pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.05, auto_write=False)
else:
    pixels = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.05, auto_write=False)

# switch_to_0 = digitalio.DigitalInOut(board.D12)
# switch_to_0.switch_to_output()
# switch_to_1 = digitalio.DigitalInOut(board.D13)
# switch_to_1.switch_to_output()

switch = digitalio.DigitalInOut(board.D4 if MAIN else board.D11)
switch.switch_to_output()

switch_in = digitalio.DigitalInOut(board.D25)
switch_in.switch_to_input(pull=digitalio.Pull.DOWN)

#output_enable = digitalio.DigitalInOut(board.A2)
#output_enable.switch_to_output()


def _wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3, 0)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3, 0)


def wheel(pos):
    col = _wheel(pos)
    return tuple(int(c / 10) for c in col)


last_out = 0
timer = 0
PERIOD = 100
COLOR_RATIO = 0.5

def mix_colors(color1, color2):
    color = tuple(color1[i] * COLOR_RATIO + color2[i] * (1 - COLOR_RATIO) for i in (0, 1, 2))
    return color

def update_pixels(color):
    global last_out, timer

    # t = float(timer if timer < PERIOD / 2 else PERIOD - timer)  # PERIOD / 2 - (timer - PERIOD / 2))
    # pixels.brightness = t / (PERIOD / 2) * 0.04 + 0.01
    # m = 1 # (t / (PERIOD / 2)) / 2.0 + 0.5
    # color = tuple(int(v * m) for v in color)

    # ts = time.time()
    # if ts != last_out:
    #     print(">", ts, color)
    #     last_out = ts
    # pixels.fill(color)  #  * int(ts % 5 / 5.0)
    for x in range(len(pixels) // 4):
        # col = tuple(int(v * (((x + 7.0 * timer / PERIOD) % 7.0) / 7.0 * 0.5 + 0.5)) for v in color)
        for y in range(len(pixels) // 8):
            rainbow_color = _wheel(((x + y) * 255.0 / 16 + timer * 255.0 / PERIOD) % 256)
            col = mix_colors(color, rainbow_color)
            if (
                not switch.value and (y == 3 or (x, y) in ((6, 2), (5, 1), (4, 0)))
                or switch.value and (y == 0 or (x, y) in ((1, 1), (2, 2), (3, 3)))
            ):
                col = tuple(c // 6 for c in color)  # mix_colors(rainbow_color, col)
            pixels[y * 8 + x] = col
    # pixels[0] = (255,0,0)
    # pixels[1] = (0,255,0)
    pixels.show()
    if MAIN:
        pixel[0] = pixels[0]
        pixel.show()

    timer = (timer + 1) % PERIOD

if MAIN:
    update_display("primary")

pressed = pressed_now = got_input = swin = switch_to_1 = switch_to_0 = switch_to_1_now = switch_to_0_now = False
v = button.value if MAIN else None
while True:
    time.sleep(0.01)

    switch_to_1_now = False
    switch_to_0_now = False
    pressed_now = False

    if supervisor.runtime.serial_bytes_available:
        value = input().strip()
        # Sometimes Windows sends an extra (or missing) newline - ignore them
        if value != "":
            got_input = True
            print("RX: {}".format(value))
            if value == "switch":
                switch_to_1_now = True
                print("switch_to_1_now")
    else:
        got_input = False
    
    if MAIN:
        pressed_now = button.value
        if pressed_now != pressed:
            v = not v
        pressed = pressed_now
        switch_to_0_now = switch_in.value
        if switch_to_0_now and not switch_to_0:
            v = False
        switch_to_0 = switch_to_0_now

        if switch_to_1_now and not switch_to_1:
            v = True
        switch_to_1 = switch_to_1_now
        is_update = v != switch.value
        switch.value = v
        update_pixels(RED if got_input else BLUE if v else PURPLE)
        if is_update:
            update_display("secondary" if v else "primary")

    if WORK:
        v = switch_to_1_now
        pixels.fill(RED if got_input else BLUE if v else PURPLE)
        pixels.show()
        switch.value = v
        if v:
            time.sleep(0.49)


"""
from analogio import AnalogIn

analog_in = AnalogIn(board.A2)



def get_voltage(pin):
    return (pin.value * 3.3) / 65536


while True:
    print((get_voltage(analog_in),))
    time.sleep(0.1)
"""

# import time
# import audioio
# import board
# import digitalio
# from adafruit_circuitplayground import cp

# # button = digitalio.DigitalInOut(board.D4)
# # button.direction = digitalio.Direction.INPUT
# # button.switch_to_input(pull=digitalio.Pull.UP)

# wave_file = open("StreetChicken.wav", "rb")
# wave = audioio.WaveFile(wave_file)
# audio = audioio.AudioOut(board.A0)

# while True:
#     audio.play(wave)

#     # This allows you to do other things while the audio plays!
#     t = time.monotonic()
#     while time.monotonic() - t < 6:
#         pass

#     audio.pause()
#     print("Waiting for button press to continue!")
#     # while not button.value:
#     while not cp.button_a:
#         pass
#     audio.resume()
#     while audio.playing:
#         pass
#     print("Done!")

# #Turtle Gizmo Square
# #==| Turtle Gizmo Setup start |========================================
# import board
# # import busio
# import displayio
# # from adafruit_st7789 import ST7789
# from adafruit_turtle import turtle
# displayio.release_displays()
# # spi = busio.SPI(board.SCL, MOSI=board.SDA)
# # display_bus = displayio.FourWire(spi, command=board.TX, chip_select=board.RX)
# # display = ST7789(display_bus, width=240, height=240, rowstart=80,
# #                  backlight_pin=board.A3, rotation=180)
# from adafruit_gizmo import tft_gizmo

# # Create the TFT Gizmo display
# display = tft_gizmo.TFT_Gizmo()

# from turtle import turtle

# turtle = turtle(display)

# import math
# DRAGON_FACTOR = 1.0 / math.sqrt(2)


# def dragon(i, l):
#     turtle.left(45 * i)
#     _dragon(i, l, True)


# def _dragon(i, l, r):
#     if i == 0:
#         turtle.forward(l)
#         return
#     l *= DRAGON_FACTOR
#     _dragon(i - 1, l, True)
#     turtle.right(90 * (1 if r else -1))
#     _dragon(i - 1, l, False)

# turtle.goto(-75, 0)
# turtle.setheading(90)
# turtle.pendown()
# dragon(6, 150)

# # Circuit Playground NeoPixel
# import time
# import board
# import neopixel

# pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.2, auto_write=False)
# NUM_PIXELS = 144
# pixelstrip = neopixel.NeoPixel(board.A3, NUM_PIXELS, brightness=1.0, auto_write=False, pixel_order=(1, 0, 2, 3))

# # choose which demos to play
# # 1 means play, 0 means don't!
# color_chase_demo = 0
# flash_demo = 0
# rainbow_demo = 0
# rainbow_cycle_demo = 1


# def wheel(pos):
#     col = _wheel(pos)
#     return tuple(int(c / 10) for c in col)


# def _wheel(pos):
#     # Input a value 0 to 255 to get a color value.
#     # The colours are a transition r - g - b - back to r.
#     if pos < 0 or pos > 255:
#         return (0, 0, 0)
#     if pos < 85:
#         return (255 - pos * 3, pos * 3, 0, 0)
#     if pos < 170:
#         pos -= 85
#         return (0, 255 - pos * 3, pos * 3, 0)
#     pos -= 170
#     return (pos * 3, 0, 255 - pos * 3, 0)


# def color_chase(color, wait):
#     for i in range(10):
#         pixels[i] = color
#         time.sleep(wait)
#         pixels.show()
#     time.sleep(0.5)


# def rainbow_cycle(wait):
#     for j in range(255):
#         for i in range(NUM_PIXELS):
#             rc_index = (i * 512 // NUM_PIXELS) + j * 4
#             pixelstrip[i] = wheel(rc_index & 255)
#         pixelstrip.show()
#         # time.sleep(wait)


# def rainbow(wait):
#     for j in range(255):
#         for i in range(len(pixels)):
#             idx = int(i + j)
#             pixels[i] = wheel(idx & 255)
#         pixels.show()
#         time.sleep(wait)


# RED = (255, 0, 0)
# YELLOW = (255, 150, 0)
# GREEN = (0, 255, 0)
# CYAN = (0, 255, 255)
# BLUE = (0, 0, 255)
# PURPLE = (180, 0, 255)
# WHITE = (255, 255, 255)
# OFF = (0, 0, 0)

# while True:
#     if color_chase_demo:
#         color_chase(RED, 0.1)  # Increase the number to slow down the color chase
#         color_chase(YELLOW, 0.1)
#         color_chase(GREEN, 0.1)
#         color_chase(CYAN, 0.1)
#         color_chase(BLUE, 0.1)
#         color_chase(PURPLE, 0.1)
#         color_chase(OFF, 0.1)

#     if flash_demo:
#         pixels.fill(RED)
#         pixels.show()
#         # Increase or decrease to change the speed of the solid color change.
#         time.sleep(1)
#         pixels.fill(GREEN)
#         pixels.show()
#         time.sleep(1)
#         pixels.fill(BLUE)
#         pixels.show()
#         time.sleep(1)
#         pixels.fill(WHITE)
#         pixels.show()
#         time.sleep(1)

#     if rainbow_cycle_demo:
#         rainbow_cycle(0.0)  # Increase the number to slow down the rainbow.

#     if rainbow_demo:
#         rainbow(0.05)  # Increase the number to slow down the rainbow.
