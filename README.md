dhcp-commit-report
==================

Introduction
------------

Outputs a parseable table of commits from an ISC DHCP-Server. Currently supports [DokuWiki](http://www.dokuwiki.org) markup format. Also comes with a small DokuWiki XMLRPC uploader.

Requirements
------------

  * [IPy](http://pypi.python.org/pypi/IPy)

Installation
------------

Use this commands inside your DHCP configuration file (dhcpd.conf) to enable COMMIT-logging:

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

Copy the distribution files into a directory and call dhcp-commit-report to output the data. Afterwards you can use dokuwiki-put to upload the report into DokuWiki.

Usage
-----

### dhcp-commit-report.py


    Usage: dhcp-commit-report.py [options] LOGFILE

    LOGFILE: Filename of the log file to parse

    Options:
      -h, --help            show this help message and exit
      -s, --sortable        Add a <sortable>-tag around the table.
      -t TITLE, --title=TITLE
                            Title of the page
      -m MODE, --mode=MODE  Output mode. Currently only supports d for DokuWiki
      -c CONF, --conf=CONF  dhcpd-Config file for subnet information (currently
                            doesn't support includes)

### dokuwiki-put.py

    Usage: dokuwiki-put.py [options] TEXTFILE

    TEXTFILE: Filename of the text to upload

    Options:
      -h, --help            show this help message and exit
      -u URL, --url=URL     URL to the Dokuwiki XMLRPC-handler
      -p PAGE, --page=PAGE  Pagename to use

Notes
-----

dhcp-commit-report outputs a special "Subnet Info" column. This is done by parsing a ISC DHCP-configuration file. The script currently doesn't support the "include"-Tag, so you simply have to paste the whole configuration together like this

    cat /etc/dhcpd.conf /etc/dhcpd.d/* > /tmp/dhcp.combined

and use this one.

To add subnet information lines into the dhcp-conf you have to add a line right before the subnet declaration looking like this:

    #$<Subnet Information>

So the result should look like this:

    #$My home subnet
    subnet 192.168.0.1 netmask 255.255.255.0 {