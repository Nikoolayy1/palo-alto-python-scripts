#!/usr/bin/env python3

import pexpect
import sys
import getpass

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

    print(f"\n===== CONNECTING TO {FW_IP} =====\n")

    child = pexpect.spawn(
        f"ssh -tt -o StrictHostKeyChecking=no {USERNAME}@{FW_IP}",
        encoding="utf-8",
        timeout=120
    )

    child.logfile = sys.stdout

    child.expect("Password:")
    child.sendline(PASSWORD)

    child.expect(PROMPT)

    child.sendline("set cli scripting-mode on")
    child.expect(PROMPT)

    child.sendline("set cli pager off")
    child.expect(PROMPT)

    child.sendline("set cli terminal width 500")
    child.expect(PROMPT)

    COMMAND = f"debug software restart process {PROCESS_NAME}"

    print(f"\nRunning command: {COMMAND}\n")

    child.sendline(COMMAND)

    child.expect(COMMAND)
    child.expect(PROMPT)

    output = child.before

    print("\n========== COMMAND OUTPUT ==========\n")
    print(output)
    print("\n====================================\n")

    child.sendline("exit")
    child.expect(pexpect.EOF)

    print(f"\nSession closed for {FW_IP}\n")
