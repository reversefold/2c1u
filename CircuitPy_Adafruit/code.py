import os
import time

import board
import digitalio
import neopixel
import supervisor
import usb_cdc


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
    os.stat("secondary")
    SECONDARY = True
    print("secondary")
except OSError:
    SECONDARY = False

PRIMARY = not SECONDARY


if PRIMARY:
    button = digitalio.DigitalInOut(board.D9)
    button.switch_to_input(pull=digitalio.Pull.DOWN)


if PRIMARY:
    pixels = neopixel.NeoPixel(board.D6, 8 * 4, brightness=0.05, auto_write=False)
    pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.05, auto_write=False)
else:
    pixels = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.05, auto_write=False)

switch_to_0_out = digitalio.DigitalInOut(board.D13)
switch_to_0_out.switch_to_output()
switch_to_1_out = digitalio.DigitalInOut(board.D12)
switch_to_1_out.switch_to_output()

switch = digitalio.DigitalInOut(board.D4 if PRIMARY else board.D11)
switch.switch_to_output()

switch_in = digitalio.DigitalInOut(board.D25)
switch_in.switch_to_input(pull=digitalio.Pull.DOWN)

# output_enable = digitalio.DigitalInOut(board.A2)
# output_enable.switch_to_output()


if PRIMARY:
    try:
        import adafruit_displayio_sh1107

        # import adafruit_displayio_ssd1306
        import adafruit_display_text.label
        import displayio
        import terminalio

        displayio.release_displays()
        i2c = board.I2C()
        display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
        # display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)
        display = adafruit_displayio_sh1107.SH1107(display_bus, width=128, height=64)
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
    inner_sprite = displayio.TileGrid(
        inner_bitmap, pixel_shader=inner_palette, x=5, y=4
    )
    splash.append(inner_sprite)

    # Draw a label
    text_area = adafruit_display_text.label.Label(
        terminalio.FONT,
        text=text,
        color=0xFFFF00,
        x=int(128 / 2 - len(text) / 2 * 6),
        y=15,
    )
    splash.append(text_area)


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
    color = tuple(
        color1[i] * COLOR_RATIO + color2[i] * (1 - COLOR_RATIO) for i in (0, 1, 2)
    )
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
            rainbow_color = _wheel(
                (
                    (x + y) * 255.0 / 16
                    + (1 if switch.value else -1) * timer * 255.0 / PERIOD
                )
                % 256
            )
            col = mix_colors(color, rainbow_color)
            if (
                not switch.value
                and (y == 3 or (x, y) in ((6, 2), (5, 1), (4, 0)))
                or switch.value
                and (y == 0 or (x, y) in ((1, 1), (2, 2), (3, 3)))
            ):
                col = tuple(c // 6 for c in color)  # mix_colors(rainbow_color, col)
            pixels[y * 8 + x] = col
    # pixels[0] = (255,0,0)
    # pixels[1] = (0,255,0)
    pixels.show()
    if PRIMARY:
        pixel[0] = pixels[0]
        pixel.show()

    timer = (timer + 1) % PERIOD


if PRIMARY:
    update_display("primary")

pressed = (
    pressed_now
) = (
    got_input
) = swin = switch_to_1 = switch_to_0 = switch_to_1_now = switch_to_0_now = False
v = button.value if PRIMARY else None
serial_in = ""
while True:
    time.sleep(0.01)

    switch_to_1_now = False
    switch_to_0_now = False
    pressed_now = False

    # if supervisor.runtime.serial_bytes_available:
    #     value = input().strip()
    value = ""
    while usb_cdc.data.in_waiting > 0:
        try:
            char = usb_cdc.data.read(1).decode("UTF-8")
        except Exception:
            print("Bad char %r" % (char,))
            continue
        if char == "\n" or char == "\r":
            value = serial_in
            serial_in = ""
            break
        serial_in += char

    if value != "":
        got_input = True
        print("RX: {}".format(value))
        if value == "switch":
            switch_to_1_now = True
            print("switch_to_1_now")
    else:
        got_input = False

    if PRIMARY:
        pressed_now = button.value
        if pressed_now != pressed and pressed_now:
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
        if is_update:
            if v:
                switch_to_1_out.value = True
            else:
                switch_to_0_out.value = True

            switch.value = v

        update_pixels(RED if got_input else BLUE if v else PURPLE)
        if is_update:
            update_display("secondary" if v else "primary")

            time.sleep(0.1)
            switch_to_1_out.value = switch_to_0_out.value = False

    if SECONDARY:
        v = switch_to_1_now
        pixels.fill(RED if got_input else BLUE if v else PURPLE)
        pixels.show()
        switch.value = v
        if v:
            time.sleep(0.49)
