# microbit-scratch-ble
Bridging between micro:bit and Scratch 1.4 via BLE (Bluetooth Low Energy) using [Remote Sensors Protocol](https://en.scratch-wiki.info/wiki/Remote_Sensors_Protocol).

Based on the work of Alessio Ciregia (https://github.com/alcir/microbit-ble).

# Tested on the Raspberry Pi and Lubuntu 18.04
## Raspberry PI
- Raspberry Pi 1 Model B with 
- Bluetooth dongle [BT-Micro4](https://www.planex.co.jp/products/bt-micro4/)
- Raspbian Stretch
## Lubuntu 18.04
- ThinkPad X40
- Bluetooth dongle [BT-Micro4](https://www.planex.co.jp/products/bt-micro4/)
- Lubuntu 18.04

# Access Bluetooth services on micro:bit
## MakeCode blocks on micro:bit

Note that the accelerometer value notification and the gesture notification are mutually exclusive.
To get the accelerometer values, you must add the bluetooth accelerometer service block.
To get the gestures, you must remove the bluetooth accelerometer service block.

<img alt="Makecode blocks" src="/makecode.png" width=500px>

## Scratch program (sample)

Note that the variable `light-level-period` needs to be __global__ ("For all sprites").

![Scratch program](/scratch.gif)

## Python program
Run after enabling remote sensors on Scratch.

$ python [microbit-to-scratch-via-ble.py](/microbit-to-scratch-via-ble.py) XX:XX:XX:XX:XX:XX  
(XX:XX:XX:XX:XX:XX is the device address of your micro:bit.)

# Other references
- [bluepy](https://github.com/IanHarvey/bluepy)
- [Scratch Python Module](https://www.wyre-it.co.uk/py-scratch/)
- [micro:bit Bluetooth profile specification](https://lancaster-university.github.io/microbit-docs/resources/bluetooth/bluetooth_profile.html)

# License
- These derivative works are placed in the public domain.
- There's no warranty.
