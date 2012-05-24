'''
DHCP-COMMIT-REPORT

Outputs a parseable table of commits from an ISC DHCP-Server

Use this commands inside your configuration file to enable COMMIT-logging:

on commit {
    if (static) {
        set isst = "static";
    } else {
        set isst = "dynamic";
    }

    log (info, concat (
        "COMMIT IP,", binary-to-ascii (10,8,".",leased-address),
        ",MAC,", suffix (concat ("0", substring(binary-to-ascii (16, 8, ":", hardware), 2, 17)),17),
        ",hostname,", option host-name,
        ",host-decl-name,", pick-first-value(host-decl-name, "(none)"),
        ",dhcp-client-identifier,", pick-first-value(binary-to-ascii(16,8,"",option dhcp-client-identifier), "(none)"),
        ",vendor-class-identifier,", pick-first-value(option vendor-class-identifier, "(none)"),
        ",agent.remote,", pick-first-value(option agent.remote-id, "(none)"),
        ",agent.circuit,", pick-first-value(option agent.circuit-id, "(none)"),
        ",leasetime,", binary-to-ascii (10,32,"",encode-int (lease-time,32)),
        ",asstype,", isst
        )
    );
}

@author: Dennis Ploeger <develop@dieploegers.de>
'''

from optparse import OptionParser
import re
from datetime import datetime, timedelta
from IPy import IP
import sys

regexp_logline = "^([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*) dhcpd: COMMIT " + \
                 "IP,([^,]*)," + \
                 "MAC,([^,]*)," + \
                 "hostname,([^,]*)," + \
                 "host-decl-name,([^,]*)," + \
                 "dhcp-client-identifier,([^,]*)," + \
                 "vendor-class-identifier,([^,]*)," + \
                 "agent.remote,([^,]*)," + \
                 "agent.circuit,([^,]*)," + \
                 "leasetime,([^,]*)," + \
                 "asstype,(.*)$"

months = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12
}

def create_dokuwiki(data_blob, blob_keys, sortable, title):

    print "====== %s ======" % (title)

    if sortable:
        print "<sortable>"

    print "^ Subnet ^ IP ^ MAC ^ Hostname ^ Start ^ Leasetime ^ End " + \
          "^ Lease-Type ^ Host-Decl-Name ^ DHCP-Client ^ Vendor-Class " + \
          "^ Remote-Agent ^ Circuit ^"

    for ipint in blob_keys:

        current = data_blob[ipint]

        print \
        "| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" \
        % (

            current["subnet_info"],
            current["ip"],
            current["mac"],
            current["hostname"],
            current["logdatetime"],
            current["leasetime"],
            current["logdatetime"] + timedelta(0, int(current["leasetime"])),
            current["asstype"],
            current["host_decl_name"],
            current["dhcp_client_identifier"],
            current["vendor_class_identifier"],
            current["agent_remote"],
            current["agent_circuit"]

        )

    if sortable:
        print "</sortable>"

    return

if __name__ == '__main__':

    parser = OptionParser(
        usage="Usage: %prog [options] LOGFILE",
        description="LOGFILE: Filename of the log file to parse"
    )

    parser.add_option(
        "-s",
        "--sortable",
        action="store_true",
        dest="sortable",
        help="Add a <sortable>-tag around the table."
    )

    parser.add_option(
        "-t",
        "--title",
        action="store",
        dest="title",
        help="Title of the page"
    )

    parser.add_option(
        "-m",
        "--mode",
        type="choice",
        choices=["d"],
        dest="mode",
        help="Output mode. Currently only supports d for DokuWiki"
    )

    parser.add_option(
        "-c",
        "--conf",
        action="store",
        dest="conf",
        help="dhcpd-Config file for subnet information " + \
            "(currently doesn't support includes)"
    )

    (options, args) = parser.parse_args()

    if len(args) == 0:
        parser.print_help()
        sys.exit(1)

    filename = args[0]

    logfile = open(filename, "rb")

    data_blob = {}

    dhcpd_conf = ""

    subnet_infos = {}

    if options.conf != None:
        conffile = open(options.conf, "rb")
        dhcpd_conf = conffile.readlines()

        last_line = ""

        for conf_line in dhcpd_conf:

            subnet_match = re.match(
                ".*subnet ([^ ]*).*netmask ([^ ]*).*",
                conf_line
            )

            if subnet_match:
                (net_ip, netmask) = subnet_match.groups()

                subnet_ip = IP("%s/%s" % (net_ip, netmask))

                subnet_infos[subnet_ip] = last_line

            last_line = conf_line


    # Parse logfile into data blob

    for line in logfile:

        line_info = re.match(regexp_logline, line)

        if line_info:

            (month, day, time, host, ip, mac, hostname, host_decl_name,
                dhcp_client_identifier, vendor_class_identifier,
                agent_remote, agent_circuit, leasetime, asstype
            ) = line_info.groups()

            (hour, minute, second) = time.split(":")

            logdatetime = datetime(
                datetime.now().year,
                months[month],
                int(day),
                int(hour),
                int(minute),
                int(second)
            )

            ipint = IP(ip).int()

            if data_blob.has_key(ipint):
                if data_blob[ipint]["logdatetime"] < logdatetime:
                    continue

            # Find subnet

            subnet_info = "unknown"

            for key in subnet_infos.keys():

                if IP(ip) in key:
                    subnet_info = subnet_infos[key]

            subnet_info = re.sub(" *", "", subnet_info)
            subnet_info = re.sub("\n", "", subnet_info)
            subnet_info = re.sub("#\$", "", subnet_info)

            data_blob[ipint] = {
                "ip": ip,
                "logdatetime": logdatetime,
                "mac": mac,
                "host": host,
                "hostname": hostname,
                "host_decl_name": host_decl_name,
                "dhcp_client_identifier": dhcp_client_identifier,
                "vendor_class_identifier": vendor_class_identifier,
                "agent_remote": agent_remote,
                "agent_circuit": agent_circuit,
                "leasetime": leasetime,
                "asstype": asstype,
                "subnet_info": subnet_info
            }

    # Sort IPs

    blob_keys = data_blob.keys()
    blob_keys.sort()

    # Create output

    if options.mode == "d":
        create_dokuwiki(data_blob, blob_keys, options.sortable, options.title)

