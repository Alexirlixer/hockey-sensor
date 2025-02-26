import uasyncio as asyncio
import bno055
import machine
import struct
from machine import Pin, ADC
import time

meas_pin = machine.Pin(29, machine.Pin.IN)
vsys = machine.ADC(3)
noise = {
    'gx': (-2.502723322906186, 2.5436267639633625),
    'gy': (-0.49575641770802303, 0.5065996729742798),
    'gz': (-0.33516017607772947, 0.3083873120191138),
    'ax': (-0.09868671432857441, -0.02056226918855668),
    'ay': (0.05140231812338187, 0.12810310529571275),
    'az': (-0.0677758433171089, 0.05252005407252612)
}


async def battery_level(on_battery):
    while True:
        voltage_factor = 3.23 * 3 / 65535
        voltage = vsys.read_u16() * voltage_factor

        on_battery(struct.pack("<f", voltage))
        await asyncio.sleep(1)


def _measure_pack(imu):
    # gyro is in degrees
    g = imu.gyro()
    a = imu.lin_acc()

    gx, gy, gz = g
    ax, ay, az = a

    # if (gx < noise['gx'][0] or gx > noise['gx'][1] or
    #     gy < noise['gy'][0] or gy > noise['gy'][1] or
    #     gz < noise['gz'][0] or gz > noise['gz'][1] or
    if (ax < noise['ax'][0] or ax > noise['ax'][1] or
        ay < noise['ay'][0] or ay > noise['ay'][1] or
        az < noise['az'][0] or az > noise['az'][1]):
        # not a noise measurement
        m = (time.ticks_us(),) + g + a
        return struct.pack("<Qffffff", *m)
    else:
        # noise
        return None

async def monitor(imu: bno055.BNO055, delay: float, on_measure):
    """
    Monitor sensor for changes
    :param imu: Sensor
    :param delay: Polling delay
    :param on_measure:
    :return:
    """
    calibrated = False
    while True:
        if not calibrated:
            calibrated = imu.calibrated()
            if calibrated:
                print('calibrated')
        m = _measure_pack(imu)
        if m:
            on_measure(m)
        # print('Mag       x {:5.0f}    y {:5.0f}     z {:5.0f}'.format(*imu.mag()))
        # print('Gyro      x {:5.0f}    y {:5.0f}     z {:5.0f}'.format(*imu.gyro()))
        # print('Accel     x {:5.1f}    y {:5.1f}     z {:5.1f}'.format(*imu.accel()))
        # print('Lin acc.  x {:5.1f}    y {:5.1f}     z {:5.1f}'.format(*imu.lin_acc()))
        # print('Gravity   x {:5.1f}    y {:5.1f}     z {:5.1f}'.format(*imu.gravity()))
        # print('Heading     {:4.0f} roll {:4.0f} pitch {:4.0f}'.format(*imu.euler()))
        await asyncio.sleep(delay)


def make_sensor_task(on_measure) -> asyncio.Task:
    i2c = machine.I2C(1, sda=machine.Pin(14), scl=machine.Pin(15))
    imu = bno055.BNO055(i2c)
    return asyncio.create_task(monitor(imu, 0.001, on_measure))


def make_battery_task(on_battery) -> asyncio.Task:
    return asyncio.create_task(battery_level(on_battery))
