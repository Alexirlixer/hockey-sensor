import uasyncio as asyncio
import service
import sensor
#
# async def wlan_connect(ssid: str, pwd: str, wifi_on: asyncio.Event):
#     """
#     Connect to Wi-Fi
#     :param ssid: Network SSID
#     :param pwd: Network password
#     :param wifi_on: Event to set when connected
#     :return:
#     """
#     wlan = network.WLAN(network.STA_IF)
#     wlan.active(True)
#     wlan.connect(ssid, pwd)
#     while not wlan.isconnected():
#         print(".")
#         await asyncio.sleep(0.5)
#
#     print(wlan.ifconfig())
#     wifi_on.set()


async def main():
    print("main enter")
    task_server, on_sense, on_battery = service.make_service_task()

    task_sensor = sensor.make_sensor_task(on_sense)
    battery_task = sensor.make_battery_task(on_battery)

    blink_task = asyncio.create_task(service.blink_state())

    v = await asyncio.gather(task_sensor, task_server, blink_task, battery_task, return_exceptions=True)
    print("main exiting", v)


asyncio.run(main())
