# 2c1u - Two computers, one USB port

The name is a riff on 2p1c, a shorthand for "Two players, one controller", a fun challenge that some speedrunners enjoy.

This project has software and hardware designs which form a USB switch, allowing for automatically moving a USB device between two computers, either through pressing of a hardware button or controlled via software running on the computers. If you plug a USB hub into the port that is switched you can switch, for instance, a keyboard and mouse between two computers, as if you were using software like Synergy.

## Layout
* 2c1u_kicad - KiCAD files for the hardware of the project, including a PCB layout.
* CircuitPy_Adafruit - Software for the Raspberry Pi devices that the hardware uses.
* 2c1u, pyproject.toml, pdm.lock - These constitute the computer software which communicate to the hardware over USB-Serial.

## History

This project is the culmination of years of thinking and tinkering in my free time. For a long time, I have used projects such as x2vnc and Synergy to have the mouse and keyboard of one computer move to another computer's screen over the network, allowing for easy use of multiple computers with their own screens at once. When I started working from home more often I wanted a way to switch between my personal and work computers seamlessly. Synergy did just that for me for a while but there were always caveats. Slowdown on the computers and random network errors would cause the input to lag or disconnect.

When my work computer was forced to have a full tunnel VPN the fully software-based network solution just wouldn't work reliably any more. The classic solution to this was a KVM, a hardware switch meant to move a keyboard, video, and mouse from one computer to another. I had no need for the video part of this, however, and I had trouble finding anything which could be software controlled. I wanted to mimic what I could do with Synergy, moving my mouse to one side of the monitor and have my mouse and keyboard move seamlessly to the other computer's minotor next to it.
