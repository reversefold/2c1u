import asyncio
import datetime
import glob
import logging
import sys

import adafruit_board_toolkit.circuitpython_serial
import serial_asyncio
import serial.serialutil
import pyautogui


logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

zero_time_threshold = datetime.timedelta(seconds=1)
ser_write = None

loop = asyncio.get_event_loop()


if sys.platform.startswith("win"):
    X_THRESHOLD = 0
else:
    X_THRESHOLD = 2559

EDGE_THRESHOLD = 500


ser_read = ser_write = None


async def serial_write():
    global ser_read, ser_write

    while True:
        while not ser_write:
            LOG.info("Waiting for serial connection")
            await asyncio.sleep(1)

        try:

            command = b"hello\n\r"
            print(f"<<[{command}]")

            ser_write.write(command)  # write a string
            await ser_write.drain()
            print("written")

            # for _ in range(len(command)):
            #    a = await ser_read.read()  # Read the loopback chars and ignore
            # print("read echo")

            # reply = b""
            # while True:
            #     a = await ser_read.read(1)
            #     if a == b"\r":
            #         print(f">>[{reply}]")
            #         reply = b""
            #     else:
            #         reply += a
            #     await asyncio.sleep(0.1)
        except Exception:
            LOG.exception("Exception in serial loop, retrying in 1s")
            await asyncio.sleep(1)


async def open_serial():
    global ser_read, ser_write
    if ser_read:
        try:
            await ser_read.close()
        except Exception:
            LOG.exception("Exception closing serial read")
    if ser_write:
        try:
            await ser_write.close()
        except Exception:
            LOG.exception("Exception closing serial write")
    ports = adafruit_board_toolkit.circuitpython_serial.data_comports()
    if not ports:
        raise Exception("No adafruit board serial data connections found")
    serial_device = ports[0].device
    LOG.info("Connecting to serial device %s" % (serial_device,))
    ser_read, ser_write = await serial_asyncio.open_serial_connection(
        url=serial_device, baudrate=115200, loop=loop,
    )


async def serial_read():
    global ser_read, ser_write

    while True:
        # import ipdb; ipdb.set_trace()
        try:
            await open_serial()

            while not ser_read:
                await asyncio.sleep(1)

            # command = b"hello\n\r"
            # print(f"<<[{command}]")

            # ser_write.write(command)  # write a string
            # await ser_write.drain()
            # print("written")

            # for _ in range(len(command)):
            #    a = await ser_read.read()  # Read the loopback chars and ignore
            # print("read echo")

            reply = b""
            while True:
                a = await ser_read.read(1)
                if a == b"\r":
                    print(f">>[{reply}]")
                    reply = b""
                else:
                    reply += a
                await asyncio.sleep(0.1)
        except Exception:
            LOG.exception("Exception in serial loop, retrying in 1s")
            await asyncio.sleep(1)
        finally:
            try:
                await ser_read.close()
            except Exception:
                LOG.exception("Exception closing serial read")
            try:
                await ser_write.close()
            except Exception:
                LOG.exception("Exception closing serial write")
            ser_read = ser_write = None


async def cursor_watch():
    while not ser_write:
        await asyncio.sleep(1)

    while True:
        try:
            last_pos_x = pyautogui.size()[0] / 2
            zero_start = None
            switched = False
            while True:
                await asyncio.sleep(0.1)
                pos_x, _ = pyautogui.position()
                if pos_x != last_pos_x:
                    print(pos_x)
                diff = abs(last_pos_x - X_THRESHOLD)
                if pos_x == X_THRESHOLD and (zero_start is not None or diff > 0 and diff < EDGE_THRESHOLD):
                    if zero_start is None:
                        print("zero_start")
                        zero_start = datetime.datetime.now()
                    if datetime.datetime.now() - zero_start > zero_time_threshold:
                        if not switched:
                            print("switch")
                            switched = True
                            command = b"switch\n\r"
                            ser_write.write(command)
                            await ser_write.drain()
                            print(f"<<[{command}]")
                else:
                    zero_start = None
                    if switched:
                        print("Switch off")
                        switched = False
                last_pos_x = pos_x
        except serial.serialutil.SerialException:
            await open_serial()
        except Exception:
            LOG.exception("Exception in cursor_watch loop, retrying in 1s")
            await asyncio.sleep(0.1)


# loop.create_task(serial_write())
loop.create_task(serial_read())
loop.create_task(cursor_watch())
loop.run_forever()
loop.close()
