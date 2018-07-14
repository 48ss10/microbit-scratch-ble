import sys
from bluepy import btle  # https://github.com/IanHarvey/bluepy
import scratch  # https://www.wyre-it.co.uk/py-scratch/
import struct
from threading import Thread


dev_addr = sys.argv[1]  # device address (XX:XX:XX:XX:XX:XX)
acc_period = 160  # 1, 2, 5, 10, 20, 80, 160 and 640 msec


class Listener(Thread):
    def __init__(self, scr, ch_led):
        self.scr = scr
        self.ch_led = ch_led
        Thread.__init__(self)
        self.daemon = True
        self.start()

    def _listen(self):
        while True:
            try:
                yield scr.receive()
            except scratch.ScratchError:
                raise StopIteration

    def run(self):
        for msg in self._listen():
            #if 'broadcast' in msg and len(msg['broadcast']) > 0:
                #print "BROADCAST: {}".format(msg['broadcast'])
            if 'sensor-update' in msg:
                su = msg['sensor-update']
                #print "SENSOR-UPDATE: {}".format(su)
                if 'LED-text' in su and len(su['LED-text']) > 0:
                    self.ch_led.write(su['LED-text'])


class MyDelegate(btle.DefaultDelegate):
    def __init__(self, scr, ch_btn_a, ch_btn_b, ch_acc, ch_tem):
        btle.DefaultDelegate.__init__(self)
        self.scr = scr
        self.chh_btn_a = ch_btn_a.getHandle()
        self.chh_btn_b = ch_btn_b.getHandle()
        self.chh_acc = ch_acc.getHandle()
        self.chh_tem = ch_tem.getHandle()

    def handleNotification(self, cHandle, data):
        if cHandle == self.chh_btn_a:
            self.scr.sensorupdate({'button-A': ord(data)})
            if ord(data) == 1:
                self.scr.broadcast('button-A-pressed')
        elif cHandle == self.chh_btn_b:
            self.scr.sensorupdate({'button-B': ord(data)})
            if ord(data) == 1:
                self.scr.broadcast('button-B-pressed')
        elif cHandle == self.chh_acc:
            x, y, z = struct.unpack('hhh', data)
            self.scr.sensorupdate({'acceleration-X': x, 'acceleration-Y': y, 'acceleration-Z': z})
        elif cHandle == self.chh_tem:
            self.scr.sensorupdate({'temperature': ord(data)})


p = btle.Peripheral(dev_addr, btle.ADDR_TYPE_RANDOM)

# Without this, the reading of the characteristic fails 
p.setSecurityLevel("medium")

# Setup to turn notifications on, e.g.
# https://lancaster-university.github.io/microbit-docs/resources/bluetooth/bluetooth_profile.html
# Button Service
svc = p.getServiceByUUID("E95D9882251D470AA062FA1922DFA9A8")
# Button A State
ch_btn_a = svc.getCharacteristics("E95DDA90251D470AA062FA1922DFA9A8")[0]
# Button B State
ch_btn_b = svc.getCharacteristics("E95DDA91251D470AA062FA1922DFA9A8")[0]

# ACCELEROMETER SERVICE
svc = p.getServiceByUUID("E95D0753251D470AA062FA1922DFA9A8")
# Accelerometer Data
ch_acc = svc.getCharacteristics("E95DCA4B251D470AA062FA1922DFA9A8")[0]
# Accelerometer Period
ch_acp = svc.getCharacteristics("E95DFB24251D470AA062FA1922DFA9A8")[0]
ch_acp.write(struct.pack('h', acc_period))

# TEMPERATURE SERVICE
svc = p.getServiceByUUID("E95D6100251D470AA062FA1922DFA9A8")
# Temperature
ch_tem = svc.getCharacteristics("E95D9250251D470AA062FA1922DFA9A8")[0]

# LED SERVICE
svc = p.getServiceByUUID("E95DD91D251D470AA062FA1922DFA9A8")
# LED Text
ch_led = svc.getCharacteristics("E95D93EE251D470AA062FA1922DFA9A8")[0]

CCCD_UUID = 0x2902 # Client Characteristic Configuration Descriptor
ch_cccd=ch_btn_a.getDescriptors(forUUID=CCCD_UUID)[0]
ch_cccd.write(b'\x01\x00', False)
ch_cccd=ch_btn_b.getDescriptors(forUUID=CCCD_UUID)[0]
ch_cccd.write(b'\x01\x00', False)
ch_cccd=ch_acc.getDescriptors(forUUID=CCCD_UUID)[0]
ch_cccd.write(b'\x01\x00', False)
ch_cccd=ch_tem.getDescriptors(forUUID=CCCD_UUID)[0]
ch_cccd.write(b'\x01\x00', False)

scr = scratch.Scratch()
p.setDelegate(MyDelegate(scr, ch_btn_a, ch_btn_b, ch_acc, ch_tem))

Listener(scr, ch_led)

while True:
    if p.waitForNotifications(1.0):
       # handleNotification() was called
       continue

    print 'Waiting...'
