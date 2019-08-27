import getpass
import telnetlib, time

DEV_COUNT = 3
DELAY_SCR = 1000
TFTP_SERVER = "10.10.11.3"
PASS_STD = "cisco"

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


# initiation loop
for i in range(DEV_COUNT):
    devices.append(cdevice(dev_ip[i]))

    # connect to device
    try:
        devices[i].open()
    except:
        continue

    #check auth
    devices[i].write(b"\n")
    time.sleep(DELAY)
    res = str(devices[i].read_very_eager())
    if res.find("Password:") != -1:
        devices[i].write(PASS_STD.encode('ascii')+b"\n")
        time.sleep(DELAY)
        res = str(devices[i].read_very_eager())
        if res.find(">") | res.find("=") == -1:
            #error auth
            pass

    # find model and software version
    devices[i].write(b"sh inv \n")
    time.sleep(DELAY)
    res = str(devices[i].read_very_eager())
    for key in dev_soft:
        if res.find(key) != -1:
            devices[i].software = dev_soft[key]
            devices[i].model = key
            try:
                devices[i].link = open(dev_script[key], 'r', encoding="utf-8")
            except:
                continue

    # check software version
    devices[i].write(b"sh ver \n")
    time.sleep(DELAY)
    res = str(devices[i].read_very_eager())
    if res.find(devices[i].software) == -1:
        devices[i].update_ios = True
        devices[i].status = "configure header"
# debug
print("######## status report ########")
print("IP address", "Model", "Software")
for i in range(DEV_COUNT):
    print(devices[i].ip_add, devices[i].model, devices[i].status)

'''
# main loop
fl_end = False
src_count = 0
while not fl_end:
    # command loop
    for i in range(DEV_COUNT):
        pass


    # print report
    src_count = src_count + 1
    if src_count > DELAY_SCR:
        print("######## status report ########")
        src_count = 0
        for i in range(DEV_COUNT):
            print(devices[i].ip_add, devices[i].model, devices[i].status)

for i in range(DEV_COUNT):
    devices[i].close()

#tn = telnetlib.Telnet(HOST)

#tn.read_until(b"Username: ")
#tn.write(user.encode('ascii') + b"\n")

#tn.write(b"sh ver\n")
#time.sleep(0.5)
#print(tn.read_very_eager())
#while True:
#    line = tn.read_some()  # Read one line
#    print(line)

#tn.write(b"exit\n")
#tprint(tn.read_all().decode('ascii'))
#tn.close()
'''