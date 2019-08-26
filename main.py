import getpass
import telnetlib, time

DEV_COUNT = 1
DELAY_SCR = 1000
TFTP_SERVER = "10.10.11.3"
dev_ip = ["10.10.11.100", "10.10.11.101", "10.10.11.102",
          "10.10.11.103", "10.10.11.104", "10.10.11.105",
          "10.10.11.106", "10.10.11.107", "10.10.11.108",
          "10.10.11.109"]

dev_soft = {'3750G-48PS-S':'c3750-ipbasek9-mz.122-55.SE12.bin',
            '3750G-24TS-1U':'c3750-ipservicesk9-mz.150-2.SE11.bin'}

dev_script = {'3750G-48PS-S':'script3750',
            '3750G-24TS-1U':'script3750'}

devices = []

class cdevice(telnetlib.Telnet):
    ip_add = ""
    line = 0
    link = "none"
    model = "none"
    status = "none"
    update_ios = False
    def __init__(self, ip_add):
        self.ip_add = ip_add
        telnetlib.Telnet.__init__(self)
        pass

# initiation loop
for i in range(DEV_COUNT):
    devices.append(cdevice(dev_ip[i]))
    devices[i].open()

    # find model
    devices[i].write("sh inv")
    time.sleep(0.5)
    res = devices[i].read_very_eager()

    # check software
    devices[i].write("sh ver")
    time.sleep(0.5)
    res = devices[i].read_very_eager()
    devices[i].update_ios = True

    print(devices[i].ip_add, devices[i].model, devices[i].status)
    devices[i].close()

'''
# main loop
fl_end = False
src_count = 0
while not fl_end:
    # command loop
    for i in range(DEV_COUNT):
        fl_end = False


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