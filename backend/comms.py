import serial
import os
import time
import serial.tools.list_ports

class serialDevice():

    def __init__(self,baud=115200,name="LPGantry"):
        self.baud = baud
        self.name = name
        self.ser_con = self.searchAndConnect()

    def searchAndConnect(self):
        ports = serial.tools.list_ports.comports()

        for port in ports:
            try:
                ser = serial.Serial(port.device, self.baud, timeout=1)
                time.sleep(2)  # allow reset (important on GIGA and arduino)

                ser.write(b'I\n')
                time.sleep(0.5)

                response = ser.read_all().decode()

                if self.name in response:
                    print(f"[COMMS] Connected to {port.device}, resp: {response}")
                    return ser
                else:
                    ser.close()

            except Exception as e:
                print(f"[COMMS][ERROR]Failed on {port.device}: {e}")
                return None

        return None

    def sendAndReceive(self,msg,dwell = 0.1):
        cmd= msg + '\n'
        try:
            self.ser_con.write(cmd.encode())
            time.sleep(dwell)
            response = self.ser_con.read_all().decode()
            return response
        except Exception as e:
            print(f"[COMMS][ERROR] Send Failure: {e} ")
            return False
        
if __name__ == "__main__":
    dev = serialDevice()
    resp = dev.sendAndReceive("S10")
    print(resp)
    print(dev.sendAndReceive("H"))