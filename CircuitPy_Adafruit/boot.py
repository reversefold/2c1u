import board
import digitalio
import usb_cdc
import storage

button = digitalio.DigitalInOut(board.D5)
button.switch_to_input(pull=digitalio.Pull.DOWN)

if button.value:
    usb_cdc.enable(console=True, data=True)
    storage.enable_usb_drive()
else:
    usb_cdc.enable(console=False, data=True)
    storage.disable_usb_drive()
