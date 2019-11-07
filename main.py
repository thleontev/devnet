import telnetlib
import time
import re
import textfsm
import yaml
from jinja2 import Environment, FileSystemLoader


# constatns
DEV_COUNT = 3
DELAY_SCR = 1000
TFTP_SERVER = "10.10.11.3"
PASS_AUTH = "cisco"
PASS_ENA = "cisco"
DELAY = 0.5
CONN_TYPE_COM = True
LOGGINING = True

# variables
devices = []     # list of pointers at object CDevice
ipaddress = []   # list of ip address devices
models = dict()  # dictionary of compatible device models and software versions

class CDevice(telnetlib.Telnet):
    ip_add = ""
    pos = 0
    script = "none"
    model = "none"
    software = "none"
    file = "none"
    status = "none"
    update_soft = False
    logginig = False

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
    device.status = "connect_success"
except:
    device.status = "error_connect"

# check connection status !

if LOGGINING:
    flog = open("log_"+device.ip_add+".txt", 'w')

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

# cheat
device.model = 'WS-C3750G-24TS-S1U'

# find script
if device.software != models['WS-C3750G-24TS-S1U']['software']:
    device.software = models['WS-C3750G-24TS-S1U']['software']
    device.script = models['WS-C3750G-24TS-S1U']['script']
    device.file = models['WS-C3750G-24TS-S1U']['file']
    device.update_soft = True

# fill template
file = TFTP_SERVER+"/" + device.file
path = device.software[:re.search('.bin', device.software).start()]+"/"+device.software
dev_temp = {'IP':device.ip_add, 'FILE': file, 'PATH': path}

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template(device.script)
script = template.render(dev_temp).split("\n")

# perform script
device.write(b"\n")
res = device.read_very_eager().decode('ascii')
fwait = False
fconfirm = True
for line in script:
    if line.find("!@") != -1:
        if line.find(":"):
            cmd = line[2:line.find(":")]
            arg = line[line.find(":")+1:]
            if cmd == 'section':
                device.status = cmd+":"+arg
                print(device.status)
            if cmd == 'wait':
                fwait = False
                floop = True
                while floop:
                    time.sleep(DELAY)
                    res = device.read_very_eager().decode('ascii').split("\r\n")
                    for res_line in res:
                        if res_line.find(arg) == -1:
                            continue
                        else:
                            floop = False
                            break

            if cmd == 'send':
                if arg == 'enter':
                    device.write(b"\r\n")

            if cmd == 'confirm':
                if arg == 'disable':
                    fconfirm = False

            if cmd == 'confirm':
                if arg == 'enable':
                    fconfirm = True
                    fwait = False


    else:
        while fwait & fconfirm:
            time.sleep(DELAY)
            res = device.read_very_eager().decode('ascii').split("\r\n")
            for res_line in res:
                if re.search('^[a-zA-Z0-9_.()-]+[#>]', res_line):
                    fwait = False
                    break
        device.write(line.encode('ascii') + b"\n")
        fwait = True
        if LOGGINING:
            flog.write("\r\n=== send command ===\r\n")
            flog.write(line)
            print(line)

# report info
print("######## status report ########")
print("IP address", "Model", "Software", "Status")
print(device.ip_add, device.model, device.status)

flog.close()