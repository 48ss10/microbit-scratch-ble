# microbit-scratch-ble
Bridging between micro:bit and Scratch 1.4 via BLE (Bluetooth Low Energy) using [Remote Sensors Protocol](https://en.scratch-wiki.info/wiki/Remote_Sensors_Protocol).

Based on the work of Alessio Ciregia (https://github.com/alcir/microbit-ble).

## Python program to bridge between micro:bit and Scratch via BLE
$ python [microbit-to-scratch-via-ble.py](/microbit-to-scratch-via-ble.py) XX:XX:XX:XX:XX:XX

(XX:XX:XX:XX:XX:XX is the device address of your micro:bit.)

## Scratch program
Note that the variable `LED-text` needs to be __global__.

![Scratch program](/scratch.gif)

## MakeCode blocks on micro:bit
Currently the io pin service and the temperature service are not supported by the above python program.

![Makecode blocks](/makecode.png)

## Tested on the Raspberry Pi
- Raspberry Pi 1 Model B
- Bluetooth dongle [BT-Micro4](https://www.planex.co.jp/products/bt-micro4/)
- Raspbian Stretch

## Other references
- [bluepy](https://github.com/IanHarvey/bluepy)
- [scratchpy](https://github.com/pilliq/scratchpy)
- [micro:bit Bluetooth profile specification](https://lancaster-university.github.io/microbit-docs/resources/bluetooth/bluetooth_profile.html)
