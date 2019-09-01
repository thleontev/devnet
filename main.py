import telnetlib
import time
import re
import textfsm
import yaml


# constatns
DEV_COUNT = 3
DELAY_SCR = 1000
TFTP_SERVER = "10.10.11.3"
PASS_AUTH = "cisco"
PASS_ENA = "cisco"
DELAY = 0.5

# variables
devices = []     # list of pointers at object CDevice
ipaddress = []   # list of ip address devices
models = dict()   # dictionary of compatible device models and software versions

class CDevice(telnetlib.Telnet):
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

# load yaml data from files
with open('ipaddress.yaml') as f:
    docs = yaml.load_all(f, Loader=yaml.FullLoader)
    for doc in docs:
        ipaddress = doc['ipaddress']

# load yaml data from files
with open('software.yaml') as f:
    docs = yaml.load_all(f, Loader=yaml.FullLoader)
    for doc in docs:
        models = doc



device = CDevice(ipaddress[0])
devices.append(device)

# connect to device
try:
    device.open()
except:
    device.status = "error_connect"

# check connection status !

#check init config (for com)
time.sleep(DELAY)
res = device.read_very_eager().decode('utf-8')
if re.search('initial configuration', res):
    device.write(b"no\n")
    time.sleep(DELAY)
    res = device.read_very_eager().decode('utf-8')
    if re.search('.+[>]', res) is None:
        device.status = "error_auth_vty"

#check auth to vty
device.write(b"\n")
time.sleep(DELAY)
res = device.read_very_eager().decode('utf-8')
if re.search('Password:', res):
    device.write(PASS_AUTH.encode('ascii')+b"\n")
    time.sleep(DELAY)
    res = device.read_very_eager().decode('utf-8')
    if re.search('.+[>]', res) is None:
        device.status = "error_auth_vty"

# check auth to enable
device.write(b"en\n")
time.sleep(DELAY)
res = device.read_very_eager().decode('utf-8')
if re.search('Password:', res):
    device.write(PASS_ENA.encode('ascii') + b"\n")
    time.sleep(DELAY)
    res = device.read_very_eager().decode('utf-8')
    if re.search('.+[#]', res) is None:
        device.status = "error_auth_enable"
    else:
        device.status = "auth_success"

# find device mode
device.write(b"sh inv \n")
time.sleep(DELAY)
res = device.read_very_eager().decode('utf-8')
template = open('cisco_ios_show_inventory.template')
fsm = textfsm.TextFSM(template)
result = fsm.ParseText(res)
device.model = result[0][1]

# find software version
device.write(b"sh ver \n")
time.sleep(DELAY)
res = device.read_very_eager().decode('utf-8')
template = open('cisco_ios_show_version.template')
fsm = textfsm.TextFSM(template)
result = fsm.ParseText(res)
device.software = result[0][6]

# report info
print("######## status report ########")
print("IP address", "Model", "Software", "Status")
print(device.ip_add, device.model, device.status)

