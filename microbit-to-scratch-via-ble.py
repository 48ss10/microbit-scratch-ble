#!/usr/bin/env python
# coding: utf-8

import sys
from bluepy import btle  # https://github.com/IanHarvey/bluepy
import scratch  # https://www.wyre-it.co.uk/py-scratch/
from struct import pack, unpack
from threading import Thread
from consts import *

#dev_addr = 'FA:3C:D2:1C:55:8D'
dev_addr = sys.argv[1]  # device address (XX:XX:XX:XX:XX:XX)

# If you change below value, the gesture detection will not work correctly
acc_period = 160  # 1, 2, 5, 10, 20, 80, 160 and 640 msec (default: 160)

def enable_notification(ch):
    CCCD_UUID = 0x2902 # Client Characteristic Configuration Descriptor
    ch_cccd = ch.getDescriptors(forUUID=CCCD_UUID)[0]
    ch_cccd.write(pack('h', 1), False)

def subscribe_microbit_event(ch, evt, val):
    ch.write(pack('hh', evt, val), False)

class MyDelegate(btle.DefaultDelegate):
    def __init__(self, p, scr):
        #try:
            #svc = p.getServiceByUUID(BUTTON_SERVICE_UUID)
            #ch_btn_a = svc.getCharacteristics(BUTTON_A_STATE_UUID)[0]
            #enable_notification(ch_btn_a)
            #ch_btn_b = svc.getCharacteristics(BUTTON_B_STATE_UUID)[0]
            #enable_notification(ch_btn_b)
            #self.chh_btn_a = ch_btn_a.getHandle()
            #self.chh_btn_b = ch_btn_b.getHandle()
            #print('button service found')
        #except btle.BTLEException:
            #print('button service not found')
            #self.chh_btn_a = None
            #self.chh_btn_b = None

        try:
            svc = p.getServiceByUUID(ACCELEROMETER_SERVICE_UUID)
            ch_acc = svc.getCharacteristics(ACCELEROMETER_DATA_UUID)[0]
            enable_notification(ch_acc)
            ch_acp = svc.getCharacteristics(ACCELEROMETER_PERIOD_UUID)[0]
            ch_acp.write(pack('h', acc_period))
            self.chh_acc = ch_acc.getHandle()
            print('accelerometer service found')
        except btle.BTLEException:
            print('accelerometer service not found')
            self.ch_acc = None

        try:
            svc = p.getServiceByUUID(TEMPERATURE_SERVICE_UUID)
            ch_tem = svc.getCharacteristics(TEMPERATURE_UUID)[0]
            enable_notification(ch_tem)
            self.chh_tem = ch_tem.getHandle()
            print('temperature service found')
        except btle.BTLEException:
            print('temperature service not found')
            self.ch_tem = None

        try:
            svc = p.getServiceByUUID(EVENT_SERVICE_UUID)
            ch_evt = svc.getCharacteristics(MICROBIT_EVENT_UUID)[0]
            self.chh_evt = ch_evt.getHandle()
            ch_cr = svc.getCharacteristics(CLIENT_REQUIREMENTS_UUID)[0]
            subscribe_microbit_event(ch_cr, ID_BUTTON_A, 0)
            subscribe_microbit_event(ch_cr, ID_BUTTON_B, 0)
            subscribe_microbit_event(ch_cr, ID_BUTTON_AB, 0)
            subscribe_microbit_event(ch_cr, ID_GESTURE, 0)  # mutually exclusive with accelerometer service
            #subscribe_microbit_event(ch_cr, ID_IO_P0, 0)
            #subscribe_microbit_event(ch_cr, ID_IO_P1, 0)
            #subscribe_microbit_event(ch_cr, ID_IO_P2, 0)
            subscribe_microbit_event(ch_cr, 9010, 0) # light level
            enable_notification(ch_evt)
            print('event service found')
        except btle.BTLEException:
            print('event service not found')
            self.chh_evt = None

        btle.DefaultDelegate.__init__(self)
        self.scr = scr

    def handleNotification(self, cHandle, data):
        if cHandle == self.chh_evt:
            id, value = unpack('hh', data)
            if id == ID_GESTURE:
                if value == GESTURE_TILT_UP:
                    self.scr.broadcast('tilt-up')
                elif value == GESTURE_TILT_DOWN: 
                    self.scr.broadcast('tilt-down')
                elif value == GESTURE_TILT_LEFT: 
                    self.scr.broadcast('tilt-left')
                elif value == GESTURE_TILT_RIGHT: 
                    self.scr.broadcast('tilt-right')
                elif value == GESTURE_FACE_UP: 
                    self.scr.broadcast('face-up')
                elif value == GESTURE_FACE_DOWN: 
                    self.scr.broadcast('face-down')
                elif value == GESTURE_FREEFALL: 
                    self.scr.broadcast('freefall')
                elif value == GESTURE_3G: 
                    self.scr.broadcast('3G')
                elif value == GESTURE_6G: 
                    self.scr.broadcast('6G')
                elif value == GESTURE_8G: 
                    self.scr.broadcast('8G')
                elif value == GESTURE_SHAKE: 
                    self.scr.broadcast('shake')
            elif id == 9010: # light level (custom event)
                self.scr.sensorupdate({'light-level': value})
            elif id == ID_BUTTON_A:
                if value == BUTTON_DOWN:
                    self.scr.broadcast('button-A-pressed')
                self.scr.sensorupdate({'button-A': value})
            elif id == ID_BUTTON_B:
                if value == BUTTON_DOWN:
                    self.scr.broadcast('button-B-pressed')
                self.scr.sensorupdate({'button-B': value})
            elif id == ID_BUTTON_AB:
                if value == BUTTON_DOWN:
                    self.scr.broadcast('button-AB-pressed')
                self.scr.sensorupdate({'button-AB': value})
        #elif cHandle == self.chh_btn_a:
            #print('button-A', ord(data))
        #elif cHandle == self.chh_btn_b:
            #print('button-B', ord(data))
        elif cHandle == self.chh_acc:
            x, y, z = unpack('hhh', data)
            self.scr.sensorupdate({'accelerometer-X': x, 'accelerometer-Y': y, 'accelerometer-Z': z})
        elif cHandle == self.chh_tem:
            self.scr.sensorupdate({'temperature': ord(data)})
        #else:
            #print('unknown')

class ScratchListener(Thread):
    def __init__(self, p, scr):
        Thread.__init__(self)
        self.scr = scr

        try:
            svc = p.getServiceByUUID(LED_SERVICE_UUID)
            self.ch_led = svc.getCharacteristics(LED_TEXT_UUID)[0]
            print('LED service found')
        except btle.BTLEException:
            print('LED service not found')
            self.ch_led = None

        try:
            svc = p.getServiceByUUID(EVENT_SERVICE_UUID)
            self.ch_ce = svc.getCharacteristics(CLIENT_EVENT_UUID)[0]
        except btle.BTLEException:
            self.ch_ce = None

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
                if 'LED-text' in su and len(su['LED-text']) > 0 and self.ch_led != None:
                    self.ch_led.write(su['LED-text'], True)
                if 'light-level-period' in su and self.ch_ce != None:
                    self.ch_ce.write(pack('hh', 9011, int(su['light-level-period'])), True)


p = btle.Peripheral(dev_addr, btle.ADDR_TYPE_RANDOM)

# Without this, the reading of the characteristic fails 
#p.setSecurityLevel("medium")

scr = scratch.Scratch()
p.setDelegate(MyDelegate(p, scr))
ScratchListener(p, scr)

while True:
    try:
        if p.waitForNotifications(1.0):
           # handleNotification() was called
           continue
    except btle.BTLEException as e:
        print(format(e))
        break
    except Exception as e:
        print(format(e))
