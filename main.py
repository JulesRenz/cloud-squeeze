# idea collection:
# send file: squeeze.py --transmit=/path/to/file --server=192.168.1.100 --max-cloud-storage=1GB --
# receive file: squeeze.py --receive --server=192.168.1.100
# list available files squeeze.py --list --server 192.168.1.100

# create work dir
# select file to receive
# check avaiable space for work
# setable chunk size (zip)
# checksum


# file structure
# file.ext.squeezepart_1;1-11:*hash*

import os
import optparse
import hashlib
import sys
import paramiko


class SqueezePart:
    def __init__(self):
        self.localfilepath = ""
        self.parentfile = ""
        self.size = ""
        self.sha256hash = ""
        self.partnum = ""
        self.filename = ""


class SqueezeFileTransfer:
    def __init__(self):
        self.mainfile = ""
        self.localfilepath = ""
        self.sha256hash = ""
        self.parts = []

    def toInitialSqueezeTransferFile(self):

        with open(self.mainfile + '.squeezetransfer', 'w', newline='') as file:
            file.write(self.sha256hash + '\n')
            for part in self.parts:
                file.write("#PENDING;" + part.filename + ";" + part.sha256hash + '\n')


def sha256hash(file):
    # BUF_SIZE is totally arbitrary, change for your app!
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!

    sha256 = hashlib.sha256();

    with open(file, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha256.update(data)

    return "{0}".format(sha256.hexdigest())

def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client

#ssh = createSSHClient(server, port, user, password)
#scp = SCPClient(ssh.get_transport())


d = os.path.dirname(__file__)  # directory of script
WORKDIR = r'{}/work'.format(d)  # path to be created
CHUNK_SIZE = 100 * 1024 * 1024

parser = optparse.OptionParser()

parser.add_option('-s', '--server',
                  action="store", dest="server",
                  help="The server to interact with")

parser.add_option('-t', '--transmit',
                  action="store", dest="transmit",
                  help="The file you want to transmit")

parser.add_option('-r', '--receive',
                  action="store", dest="receive",
                  help="The file you want to receive")

options, args = parser.parse_args()

if options.receive and options.transmit:
    print("Cannot set both receive and transmit options")
    exit(-1)

if not options.server:
    print("Need server!")
    exit(-1)

# make workdir if neccessary
directory = os.path.dirname(WORKDIR)
if not os.path.exists(directory):
    print("generating directory " + WORKDIR)
    os.makedirs(directory)

if options.transmit:
    filename = options.transmit

    transfer = SqueezeFileTransfer()
    transfer.mainfile = os.path.basename(filename)
    transfer.localfilepath = filename

    print("transmitting file " + options.transmit + " to server " + options.server)


    print("hashing ...")
    transfer.sha256hash = sha256hash(filename)
    print(filename + ":" + transfer.sha256hash)



    with open(filename, "rb") as f:
        file_number = 0
        chunk = 0
        while chunk or file_number == 0:
            file_number += 1
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break;
            chunkname = filename + ".squeezepart_" + str(file_number)
            with open(chunkname, 'wb') as chunk_file:
                chunk_file.write(chunk)

            part = SqueezePart()
            part.filename = os.path.basename(chunkname)
            part.localfilepath = chunkname
            part.parentfile = transfer.mainfile
            part.partnum = file_number
            part.size = CHUNK_SIZE
            part.sha256hash = sha256hash(chunkname)
            transfer.parts.append(part)

            print("Part " + (str)(file_number) + " of file " + filename + " has hash " + part.sha256hash)

    transfer.toInitialSqueezeTransferFile()
    #upload Squeezetransfer File to server
    print("done")

