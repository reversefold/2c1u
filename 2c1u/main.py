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

zero_time_threshold = datetime.timedelta(seconds=0.2)
ser_write = None

loop = asyncio.new_event_loop()


class Operator(object):
    @staticmethod
    def apply(a, b):
        raise Unimplemented()


class GreaterThan(Operator):
    @staticmethod
    def apply(a, b):
        return a > b


class LessThan(Operator):
    @staticmethod
    def apply(a, b):
        return a < b


EDGE_THRESHOLD = 5
MAX_DIFF = 300
if sys.platform.startswith("win"):
    X_EDGE = 0 + EDGE_THRESHOLD
    OPERATOR = LessThan
else:
    X_EDGE = 2559 - EDGE_THRESHOLD
    OPERATOR = GreaterThan


ser_read = ser_write = None


async def serial_write():
    global ser_read, ser_write

    while True:
        while not ser_write:
            LOG.info("Waiting for serial write connection")
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
            LOG.exception("Exception in serial_write loop, retrying in 1s")
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
        url=serial_device,
        baudrate=115200,
        loop=loop,
    )


async def serial_read():
    global ser_read, ser_write

    while True:
        # import ipdb; ipdb.set_trace()
        try:
            await open_serial()

            while not ser_read:
                LOG.info("Waiting for serial read connection")
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
            LOG.exception("Exception in serial_read loop, retrying in 1s")
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
            edge_start = None
            switched = False
            while True:
                await asyncio.sleep(0.1)
                pos_x, _ = pyautogui.position()
                if pos_x == last_pos_x and edge_start is None:
                    continue
                if pos_x != last_pos_x:
                    print(pos_x)
                diff = abs(last_pos_x - X_EDGE)
                if OPERATOR.apply(pos_x, X_EDGE) and (
                    edge_start is not None or diff < MAX_DIFF
                ):
                    if edge_start is None:
                        print(diff)
                        print("edge_start")
                        edge_start = datetime.datetime.now()
                    if datetime.datetime.now() - edge_start > zero_time_threshold:
                        if not switched:
                            print("switch")
                            switched = True
                            command = b"switch\n\r"
                            ser_write.write(command)
                            await ser_write.drain()
                            print(f"<<[{command}]")
                else:
                    edge_start = None
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
