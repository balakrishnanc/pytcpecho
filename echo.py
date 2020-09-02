#!/usr/bin/env python
# -*- mode: python; coding: utf-8; fill-column: 80; -*-
"""A simple TCP echo server and client.
"""

import argparse
import socket


def mk_socket():
    """Make TCP socket."""
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def run_client():
    pass


def run_server(port):
    """Run TCP echo server."""
    srv = mk_socket()
    # TODO: Pass interface.
    srv.bind(('', port))


def main(args):
    if args.target:
        # Run client.
        pass
    else:
        # Run server.
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Run TCP echo server or client")
    parser.add_argument('--port', dest='port',
                        type=int,
                        default=9988,
                        help='Port number')
    parser.add_argument('--target', dest='target', metavar='target-IP',
                        type=str,
                        default='localhost',
                        help=('Target IP address for a client to connect'))
    main(parser.parse_args())
