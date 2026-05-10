import pexpect
import sys
import re
import xml.etree.ElementTree as ET
import getpass
from panos.firewall import Firewall

USERNAME = input("Username: ")
PASSWORD = getpass.getpass("Password: ")

PROMPT = r"\S+@\S+>"

with open("firewalls.txt") as f:
    FW_LIST = [line.strip() for line in f if line.strip()]

for FW_IP in FW_LIST:
    print(f"\n===== SSH CHECK: {FW_IP} =====\n")

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

    child.sendline("set cli op-command-xml-output on")
    child.expect(PROMPT)

    child.sendline("show system info")

    child.expect("show system info")
    child.expect(PROMPT)

    output = child.before

    print("\n========== FULL OUTPUT ==========\n")
    print(output)
    print("\n=================================\n")

    child.sendline("exit")
    child.expect(pexpect.EOF)

    print("\nSession closed")

    print(f"\n===== SDK CHECK: {FW_IP} =====\n")

    fw = Firewall(
        hostname=FW_IP,
        api_username=USERNAME,
        api_password=PASSWORD,
    )

    result = fw.op("show system info")

    sw_version = result.find(".//sw-version").text
    hostname = result.find(".//hostname").text
    logdb_version = result.find(".//logdb-version").text

    print("hostname:", hostname)
    print("sw-version:", sw_version)
    print("logdb-version:", logdb_version)
