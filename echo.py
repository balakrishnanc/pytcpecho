#!/usr/bin/env python
# -*- mode: python; coding: utf-8; fill-column: 80; -*-
"""A simple TCP echo server and client.
"""

import argparse
import socket


# Default port.
DEF_PORT = 9988

# Connection backlog size.
BACKLOG = 5

# Buffer size.
BUF_SZ = 4096


def mk_socket():
    """Make TCP socket."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
    return s


def run_client(target, port, num_pkts=10):
    """Run TCP echo client."""
    cli = mk_socket()

    # TODO: Pass IP address rather than hard-code the default.
    cli.connect((target, port))

    data = ('*' * 512).encode('utf-8')

    with cli:
        for _ in range(num_pkts):
            cli.send(data)


def handle_cli(sock, addr, verbose):
    """Handle connection from client."""
    data = sock.recv(BUF_SZ)
    n = sock.send(data)

    # Check if we echoed all the bytes back.
    if n != len(data):
        raise ValueError("Failed to echo all bytes!")


def run_server(port, verbose=False):
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
                    print(f"> received connection from {addr}")

                # TODO: Spawn a thread to handle the client.
                handle_cli(cli, addr, verbose)
    except KeyboardInterrupt:
        # Killed from terminal via CTRL-C
        if verbose:
            print("> quit.")


def main(args):
    if args.target:
        # Run client.
        run_client(args.target, args.port, args.verbose)
    else:
        # Run server.
        run_server(args.port, args.verbose)


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
    main(parser.parse_args())
