# hockey-sensor

MicroPython firmware for a stick-mounted motion sensor that streams real-time hockey shot data over Bluetooth LE. This is the on-device half of a two-part system — the desktop/ML counterpart that consumes this stream lives in [hockey-sensor-client](https://github.com/Alexirlixer/hockey-sensor-client).

## Hardware

- Raspberry Pi Pico W
- Adafruit BNO055 9-DOF IMU (gyroscope + accelerometer), wired over I2C on pins 14 (SDA) and 15 (SCL)
- LiPo battery, monitored via ADC on pin 29/ADC3

## What it does

- `sensor.py` polls the BNO055 at high frequency, reads gyro and linear-acceleration vectors, and filters out near-zero noise before timestamping and packing each sample (`<Qffffff`: timestamp + 3-axis gyro + 3-axis acceleration).
- `service.py` advertises a custom BLE GATT peripheral named `hockey-sensor` (service UUID `0xBEEF`) and notifies connected clients with each measurement as it arrives, plus a separate battery-voltage characteristic (`0xB00F`).
- `main.py` wires the sensor loop, the BLE service, battery monitoring, and an onboard LED status blink (solid when a client is connected, blinking while advertising) together as cooperative `uasyncio` tasks.

## Setup

1. Flash the Pico W with `micropython-firmware-pico-w-130623.uf2` or newer (needs Bluetooth support).
2. Copy [`bno055.py`](https://github.com/micropython-IMU/micropython-bno055/) and its dependencies onto the board.
3. Copy `main.py`, `sensor.py`, `service.py`, `bno055_base.py` onto the board.
4. Power on — the board advertises as `hockey-sensor` over BLE. Connect with [hockey-sensor-client](https://github.com/Alexirlixer/hockey-sensor-client) to collect data or run live shot detection.
