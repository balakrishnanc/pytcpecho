#!/usr/bin/env python
# -*- mode: python; coding: utf-8; fill-column: 80; -*-
"""A simple TCP echo server and client.
"""

import argparse
import socket
import sys


# Default port.
DEF_PORT = 9988

# Number of packets.
DEF_NUM_PKTS = 10

# Connection backlog size.
BACKLOG = 5

# Buffer size.
BUF_SZ = 4096


def __err(msg, exit_code=1):
    """Write an error message to STDERR."""
    sys.stderr.write("Error: %s\n" % (msg))
    sys.exit(exit_code)


def mk_socket():
    """Make TCP socket."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
    return s


def run_client(target, port, num_pkts, verbose):
    """Run TCP echo client."""
    cli = mk_socket()

    # TODO: Pass IP address rather than hard-code the default.
    cli.connect((target, port))

    data = ('*' * 512).encode('utf-8')

    with cli:
        for _ in range(num_pkts):
            n = cli.send(data)

            if n != len(data):
                __err("Failed to write all bytes!")

        # TODO: Move to a separate thread.
        for _ in range(num_pkts):
            n = cli.recv(BUF_SZ)


def handle_cli(sock, addr, num_pkts, verbose):
    """Handle connection from client."""
    for _ in range(num_pkts):
        data = sock.recv(BUF_SZ)
        n = sock.send(data)

        # Check if we echoed all the bytes back.
        if n != len(data):
            __err("Failed to echo all bytes!")


def run_server(port, num_pkts, verbose=False):
    """Run TCP echo server."""
    srv = mk_socket()

    # TODO: Pass interface rather than hard-code the default.
    srv.bind(('', port))
    srv.listen(BACKLOG)

    try:
        with srv:
            while True:
                cli, addr = srv.accept()

                if verbose:
                    print("> received connection from %s:%d" % (addr))

                # TODO: Spawn a thread to handle the client.
                with cli:
                    handle_cli(cli, addr, num_pkts, verbose)
    except KeyboardInterrupt:
        # Killed from terminal via CTRL-C
        if verbose:
            print("> quit.")


def main(args):
    other_opts = (args.count, args.verbose)

    if args.target:
        # Run client.
        run_client(args.target, args.port, *other_opts)
    else:
        # Run server.
        run_server(args.port, *other_opts)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Run TCP echo server or client")
    parser.add_argument('--verbose', '-v',
                        action='store_true',
                        help='Enable verbose output')
    parser.add_argument('--port', dest='port',
                        type=int,
                        default=DEF_PORT,
                        help='Port number')
    parser.add_argument('--target', dest='target', metavar='target-IP',
                        type=str,
                        help=('Target IP address for a client to connect'))
    parser.add_argument('--count', '-c',
                        type=int,
                        default=DEF_NUM_PKTS,
                        help='Number of packets (pings) to send')
    main(parser.parse_args())