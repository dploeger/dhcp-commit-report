'''
Simple Dokuwiki page uploader using XMLRPC

Specify the URL (-u) to the Dokuwiki XMLRPC-Service and the page name (-p)
to overwrite

@author: Dennis Ploeger <develop@dieploegers.de>
'''

import xmlrpclib
from optparse import OptionParser

if __name__ == '__main__':
    parser = OptionParser(
        usage="Usage: %prog [options] TEXTFILE",
        description="TEXTFILE: Filename of the text to upload"
    )

    parser.add_option(
        "-u",
        "--url",
        action="store",
        dest="url",
        help="URL to the Dokuwiki XMLRPC-handler"
    )

    parser.add_option(
        "-p",
        "--page",
        action="store",
        dest="page",
        help="Pagename to use"
    )

    (options, args) = parser.parse_args()

    if len(args) == 0 or options.url == None or options.page == None:
        parser.print_help()
        sys.exit(1)

    filename = args[0]

    file_contents = "".join(open(filename, "rb").readlines())

    server = xmlrpclib.Server(options.url)
    server.wiki.putPage(options.page, file_contents, {})
