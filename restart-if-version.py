#!/usr/bin/env python3

import pexpect
import sys
import getpass
from panos.firewall import Firewall

#
# Usage:
# python3 script.py web-server
#

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <process-name>")
    sys.exit(1)

PROCESS_NAME = sys.argv[1]

USERNAME = input("Username: ")
PASSWORD = getpass.getpass("Password: ")

PROMPT = r"\S+@\S+>"

with open("firewalls.txt") as f:
    FW_LIST = [line.strip() for line in f if line.strip()]

for FW_IP in FW_LIST:

    print(f"\n===== API CHECK: {FW_IP} =====\n")

    try:

        #
        # REST API / SDK check first
        #
        fw = Firewall(
            hostname=FW_IP,
            api_username=USERNAME,
            api_password=PASSWORD,
        )

        result = fw.op("show system info")

        hostname = result.find(".//hostname").text
        sw_version = result.find(".//sw-version").text
        logdb_version = result.find(".//logdb-version").text

        print("hostname:", hostname)
        print("sw-version:", sw_version)
        print("logdb-version:", logdb_version)

        #
        # Restart only on specific PAN-OS version
        #
        if sw_version != "10.1.4":

            print(f"\nSkipping {FW_IP} because version is not 10.1.4\n")
            continue

        #
        # Continue with SSH restart
        #
        print(f"\n===== SSH RESTART: {FW_IP} =====\n")

        child = pexpect.spawn(
            f"ssh -tt -o StrictHostKeyChecking=no {USERNAME}@{FW_IP}",
            encoding="utf-8",
            timeout=120
        )

        child.logfile = sys.stdout

        #
        # Login
        #
        child.expect("Password:")
        child.sendline(PASSWORD)

        child.expect(PROMPT)

        #
        # CLI settings
        #
        child.sendline("set cli scripting-mode on")
        child.expect(PROMPT)

        child.sendline("set cli pager off")
        child.expect(PROMPT)

        child.sendline("set cli terminal width 500")
        child.expect(PROMPT)

        #
        # Restart process
        #
        COMMAND = f"debug software restart process {PROCESS_NAME}"

        print(f"\nRunning command: {COMMAND}\n")

        child.sendline(COMMAND)

        child.expect(COMMAND)
        child.expect(PROMPT)

        output = child.before

        print("\n========== COMMAND OUTPUT ==========\n")
        print(output)
        print("\n====================================\n")

        #
        # Exit SSH
        #
        child.sendline("exit")
        child.expect(pexpect.EOF)

        print(f"\nSession closed for {FW_IP}\n")

    except Exception as e:

        print(f"\nERROR on {FW_IP}")
        print(e)
