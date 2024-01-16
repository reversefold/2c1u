# 2c1u - Two computers, one USB port

The name is a riff on 2p1c, a shorthand for "Two players, one controller", a fun challenge that some speedrunners enjoy.

This project has software and hardware designs which form a USB switch, allowing for automatically moving a USB device between two computers, either through pressing of a hardware button or controlled via software running on the computers. If you plug a USB hub into the port that is switched you can switch, for instance, a keyboard and mouse between two computers, as if you were using software like Synergy.

## Layout
* 2c1u_kicad - KiCAD files for the hardware of the project, including a PCB layout.
* CircuitPy_Adafruit - Software for the Raspberry Pi devices that the hardware uses.
* 2c1u, pyproject.toml, pdm.lock - These constitute the computer software which communicate to the hardware over USB-Serial.

## Hardware
Required hardware:
* 2x [Adafruit Feather RP2040](https://www.adafruit.com/product/4884)
* 2x [TinkerBoy USB 2.0 Hub Breakout](https://www.tinkerboy.xyz/product/tinkerboy-usb-hub-4-port-usb-hub-2-0/)
* 3x [Adafruit 4090 - USB-C Breakout](https://www.adafruit.com/product/4090)
* 2x [Omron G6SK-2-DC5 relays](https://www.mouser.com/ProductDetail/Omron-Electronics/G6SK-2-DC5?qs=Mrnyg3lK62HQss%2FMQAyqbw%3D%3D)
* 2x [PN2222A Transistor](https://www.digikey.com/en/products/detail/nte-electronics-inc/PN2222A/11655004)
* 2x [Tactile Button Switch](https://www.adafruit.com/product/367)
* 1x [Sparkfun Cherry MX Switch Breakout](https://www.sparkfun.com/products/13773)
* 1x Cherry MX Compatible Switch
* 1x Keycap
* 2x 1K resistors
* 2x 10K resistors

I am also using several feather breakout boards for additional output as I had them around to play with:
* 1x [NeoPixel FeatherWing](https://www.adafruit.com/product/2945)
* 1x [Adafruit FeatherWing OLED - 128x64](https://www.adafruit.com/product/4650)
* 1x [FeatherWing Tripler Mini Kit](https://www.adafruit.com/product/3417)

You will additionally need PCB mount headers for the various components and either breadboards or a custom PCB (see fully functional PCB in `2c1u_kicad`). Note that the TinkerBoy USB 2.0 Hub Breakout boards are not breadboard compatible, the holes are not uniformly separated and require some creativity to hook up with a breadboard.

All of the soldering for the PCB are through-hole, as are nearly all of the boards. The one exception is the two data pads on the RP2040 boards. These pads connect to the 2 data pins of the USB connector so they can be used to wire up the RP2040 to the TinkerBoy boards as a USB device.

The Raspberry Pi boards are the brains of the switch. Each one connects to one of the computers as a USB serial device as a control channel. The primary one also controls the relays which switch the USB devices between the two computers.

One USB connector is for the input device to switch between the two hosts. I use a simple USB hub and plug both my keyboard and mouse into it, then plug the hub into the switch. The other 2 USB connectors connect to the two host computers. The TinkerBoy boards act as USB hubs, allowing both the RPi boards and the input devices to be connected via one USB connection. Note that this switch supports USB 2.0 only, so it's only really useful for lower bandwidth devices, like HID devices.

The Cherry MX switch allows switching between the two host computers manually. The two small switch buttons next to the USB connectors on the PCB can be held down while plugging in the associated USB cable to have the RPi start up in developer mode, with a repl usb-serial connection and as usb mass storage.

## Device-side software
The device-side software is written in Python for CircuitPy running on an Adafruit device. For the secondary create a file named `secondary` in the root of the drive.

The `boot.py` file turns on the data interface and turns off the repl interface, as well as turns off the ability of the CircuitPy device to be a USB drive. If you want access to the USB drive and repl interface you can pull pin D5 up (the buttons next to the USB connectors on the PCB are for this).

## Computer-side software
The computer-side software is written in Python and uses pdm for dependency management. Once you've installed pdm, change to the project directory, use the command `pdm install` to have pdm install all of the dependencies, then use the command `pdm run python 2c1u/main.py` to start the software. Until you have the right hardware hooked up it will loop with exceptions about not finding the serial interface.

The code near the top that defines `X_EDGE` configures how the edge of the screen is detected for the two machines, one Windows on the right, and one not Windows on the left.

## History

This project is the culmination of years of thinking and tinkering in my free time. For a long time, I have used projects such as x2vnc and Synergy to have the mouse and keyboard of one computer move to another computer's screen over the network, allowing for easy use of multiple computers with their own screens with a single keyboard and mouse. When I started working from home more often I wanted a way to switch between my personal and work computers seamlessly. Synergy did just that for me for a while but there were always caveats. Slowdown on the computers and random network errors would cause the input to lag or disconnect.

When my work computer was forced to have a full tunnel VPN the fully software-based network solution just wouldn't work reliably any more. The classic solution to this was a KVM, a hardware switch meant to move a keyboard, video, and mouse from one computer to another. I had no need for the video part of this, however, and I had trouble finding anything which could be software controlled. I wanted to mimic what I could do with Synergy, moving my mouse to one side of the monitor and have my mouse and keyboard move seamlessly to the other computer's monitor next to it.
