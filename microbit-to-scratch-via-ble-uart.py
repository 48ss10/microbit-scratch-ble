import sys
import time
from threading import Thread
from bluepy import btle
import scratch

"""
 This code is based on SensorTagCollectorThread with auto-reconnect mechanism by Venkat2811
 https://github.com/Venkat2811/bluepy/blob/master/bluepy/sensortag_collector.py
"""

device_mac = sys.argv[1]  # device address (XX:XX:XX:XX:XX:XX)


class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        self.scr = scratch.Scratch()

    def handleNotification(self, cHandle, data):
        #print("A notification was received: {} ".format(data))
        datalist = data.split()
        if datalist[0] == 's' and len(datalist) >= 3:
            self.scr.sensorupdate({datalist[1]: datalist[2]})
        if datalist[0] == 'b' and len(datalist) >= 2:
            self.scr.broadcast(datalist[1])

class microbitCollector(Thread):
    def __init__(self, device_name, device_mac, sampling_interval_sec=1, retry_interval_sec=5):
        Thread.__init__(self)
        self.daemon = True
        self.conn = None
        self.device_name = device_name
        self.device_mac = device_mac
        self._sampling_interval_sec = sampling_interval_sec
        self._retry_interval_sec = retry_interval_sec
        # Connects with re-try mechanism
        self._re_connect()
        self.start()

    def _connect(self):
        print "Connecting..."
        self.conn = btle.Peripheral(self.device_mac, btle.ADDR_TYPE_RANDOM)
        #self.conn.setSecurityLevel("medium")
        print "Connected..."
        self._enable()

    def _enable(self):
        self.svc = self.conn.getServiceByUUID("6e400001-b5a3-f393-e0a9-e50e24dcca9e")
        self.ch = self.svc.getCharacteristics("6e400002-b5a3-f393-e0a9-e50e24dcca9e")[0]
        self.chwrite = self.svc.getCharacteristics("6e400003-b5a3-f393-e0a9-e50e24dcca9e")[0]

        # Write 0200 to CCCD UUID
        self.ch_cccd = self.ch.getDescriptors("00002902-0000-1000-8000-00805f9b34fb")[0]
        self.ch_cccd.write(b"\x02\x00", True)

        self.conn.setDelegate( MyDelegate() )
        time.sleep(1)
        print "UART notification enabled..."

    def run(self):
        while True:
            count=0
            while True:
                try:
                    if self.conn.waitForNotifications(1.0):
                        count = 0
                        continue

                    print("Waiting...")
                    count=count+1
                    # After 3 waiting cycles, send the "reset." string to the micro:bit
                    if(count > 3):
                        print("No data for a while: reset")
                        self.chwrite.write("reset.")
                except Exception as e:
                    print str(e)
                    self.conn.disconnect()
                    break

            time.sleep(self._retry_interval_sec)
            self._re_connect()

    def _re_connect(self):
        while True:
            try:
                self._connect()
                break
            except Exception as e:
                print str(e)
                time.sleep(self._retry_interval_sec)

if __name__ == '__main__':

    microbitCollector(device_name="BBC micro:bit", device_mac=device_mac, sampling_interval_sec=1)

    while True:
        time.sleep(1000)
        pass
