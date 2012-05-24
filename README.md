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
