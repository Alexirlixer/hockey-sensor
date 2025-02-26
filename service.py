import uasyncio as asyncio
import aioble
import bluetooth
from micropython import const
import machine
import time

# # location and navigation service
# _SENSE_UUID = bluetooth.UUID(0x1819)
# # location and speed
# _SENSE_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A67)

# custom
_SENSE_UUID = bluetooth.UUID(0xBEEF)
_SENSE_CHARACTERISTIC_UUID = bluetooth.UUID(0xBEEF)
_BATTERY_CHARACTERISTIC_UUID = bluetooth.UUID(0xB00F)
# speed sensor
_ADV_APPEARANCE = const(0x0482)

# How frequently to send advertising beacons.
_ADV_INTERVAL_MS = 250_000

# Register GATT server.
sensor_service = aioble.Service(_SENSE_UUID)
sensor_characteristic = aioble.Characteristic(
    sensor_service, _SENSE_CHARACTERISTIC_UUID, read=True, notify=True
)
battery_characteristic = aioble.Characteristic(
    sensor_service, _BATTERY_CHARACTERISTIC_UUID, read=True, notify=True
)
aioble.register_services(sensor_service)


led = machine.Pin("LED", machine.Pin.OUT)
connected = asyncio.Event()


async def blink_state():
    while True:
        if connected.is_set():
            led.on()
        else:
            led.on()
            time.sleep(0.5)
            led.off()
        await asyncio.sleep(1)


def _publish_measurement(data: bytes):
    # print("server publish notify")
    if connected.is_set():
        sensor_characteristic.write(data, send_update=True)


def _publish_battery(data: bytes):
    if connected.is_set():
        print("battery publish notify")
        battery_characteristic.write(data, send_update=True)


async def peripheral_task():
    """
    Serially wait for connections. Don't advertise while a central is connected.
    :return:
    """
    while True:
        async with await aioble.advertise(
                _ADV_INTERVAL_MS,
                name="hockey-sensor",
                services=[_SENSE_UUID],
                appearance=_ADV_APPEARANCE,

        ) as connection:
            print("Connection from", connection.device)
            connected.set()

            await connection.disconnected()
            connected.clear()


def make_service_task():
    return asyncio.create_task(peripheral_task()), _publish_measurement, _publish_battery
