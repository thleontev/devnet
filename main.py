import telnetlib
import time
import re
import textfsm

DEV_COUNT = 3
DELAY_SCR = 1000
TFTP_SERVER = "10.10.11.3"
PASS_AUTH = "cisco"
PASS_ENA = "cisco"
DELAY = 0.5
dev_ip = ["172.31.1.150", "172.31.1.151", "172.31.1.152",
          "10.10.11.103", "10.10.11.104", "10.10.11.105",
          "10.10.11.106", "10.10.11.107", "10.10.11.108",
          "10.10.11.109"]

dev_soft = {'3750G-48PS-S':'c3750-ipbasek9-mz.122-55.SE12.bin',
            '3750G-24TS-1U':'c3750-ipservicesk9-mz.150-2.SE11.bin',
            'C3745-2FE':'c3750-ipservicesk9-mz.150-2.SE11.bin',
            'CISCO7206VXR': 'c3750-ipservicesk9-mz.150-2.SE11.bin',
            '3640 chassis': 'c3750-ipservicesk9-mz.150-2.SE11.bin'}

dev_script = {'3750G-48PS-S':'dn3750',
            '3750G-24TS-1U':'dn3750',
            'C3745-2FE':'dn3750',
            'CISCO7206VXR':'dn3750',
            '3640 chassis':'dn3750'}

devices = []

class cdevice(telnetlib.Telnet):
    ip_add = ""
    pos = 0
    link = "none"
    model = "none"
    software = "none"
    status = "none"
    update_ios = False

    def __init__(self, ip_add):
        self.ip_add = ip_add
        telnetlib.Telnet.__init__(self)

    def __del__(self):
        super().__del__()

    def open(self):
        super().open(self.ip_add, 23, 5)


i =0
devices.append(cdevice(dev_ip[i]))

# connect to device
try:
    devices[i].open()
except:
    pass

#check init config
time.sleep(DELAY)
res = devices[i].read_very_eager().decode('utf-8')
if re.search('initial configuration', res):
    devices[i].write(b"no\n")
    time.sleep(DELAY)
    res = devices[i].read_very_eager().decode('utf-8')
    if re.search('.+[>]', res) is None:
        devices[i].status = "error_auth_vty"

#check auth to vty
devices[i].write(b"\n")
time.sleep(DELAY)
res = devices[i].read_very_eager().decode('utf-8')
if re.search('Password:', res):
    devices[i].write(PASS_AUTH.encode('ascii')+b"\n")
    time.sleep(DELAY)
    res = devices[i].read_very_eager().decode('utf-8')
    if re.search('.+[>]', res) is None:
        devices[i].status = "error_auth_vty"


# check auth to enable
devices[i].write(b"en\n")
time.sleep(DELAY)
res = devices[i].read_very_eager().decode('utf-8')
if re.search('Password:', res):
    devices[i].write(PASS_ENA.encode('ascii') + b"\n")
    time.sleep(DELAY)
    res = devices[i].read_very_eager().decode('utf-8')
    if re.search('.+[#]', res) is None:
        devices[i].status = "error_auth_enable"
    else:
        devices[i].status = "auth_success"

# find device mode
devices[i].write(b"sh inv \n")
time.sleep(DELAY)
res = devices[i].read_very_eager().decode('utf-8')
template = open('cisco_ios_show_inventory.template')
fsm = textfsm.TextFSM(template)
result = fsm.ParseText(res)
devices[i].model = result[0][1]

# find software version
devices[i].write(b"sh ver \n")
time.sleep(DELAY)
res = devices[i].read_very_eager().decode('utf-8')
template = open('cisco_ios_show_version.template')
fsm = textfsm.TextFSM(template)
result = fsm.ParseText(res)
devices[i].software = result[0][6]

# debug
print("######## status report ########")
print("IP address", "Model", "Software", "Status")
print(devices[i].ip_add, devices[i].model, devices[i].status)

