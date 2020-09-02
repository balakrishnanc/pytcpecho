#!/usr/bin/env python
# -*- mode: python; coding: utf-8; fill-column: 80; -*-
"""A simple TCP echo server and client.
"""

import argparse
import socket
import sys
import threading
import time


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


def mk_socket(server=False):
    """Make TCP socket."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    if server:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return s


def mk_msg(sz):
    """Make a message of given size and include a timestamp."""
    return bytes("%.6f" % (time.time()), 'utf-8').zfill(sz)


def proc_echo(recv_ts, data):
    """Compute the elapsed time (in ms) from the timestamp in the packet."""
    return (recv_ts - float(data.lstrip(b'0').decode())) * 1000


def recv_echoes(sock, num_pkts, sz, verbose):
    """Receive echoes and process the timestamps in them."""
    for i in range(num_pkts):
        data = sock.recv(sz)
        recv_ts = time.time()
        n = len(data)

        if n != sz:
            __err("Failed to receive all bytes!")

        if verbose:
            sys.stdout.write("« %.2f\n" % (proc_echo(recv_ts, data)))


def run_client(target, port, num_pkts, verbose):
    """Run TCP echo client."""
    cli = mk_socket()

    # TODO: Pass IP address rather than hard-code the default.
    cli.connect((target, port))

    if verbose:
        sys.stdout.write("»\n")

    # Create a separate thread to handle receives.
    recv_opts = (cli, num_pkts, BUF_SZ, verbose)
    recv = threading.Thread(target=recv_echoes, args=recv_opts)

    with cli:
        recv.start()

        for i in range(num_pkts):
            data = mk_msg(BUF_SZ)
            n = cli.send(data)

            if n != len(data):
                __err("Failed to write all bytes!")

            if verbose:
                sys.stdout.write("»\n")

        # Wait until all echoes are received.
        recv.join()


def cli_handler(sock, addr, num_pkts, verbose):
    """Echo client data."""
    with sock:
        for i in range(num_pkts):
            data = sock.recv(BUF_SZ)

            if verbose:
                sys.stdout.write("« [%d]\n" % (len(data)))

            n = sock.send(data)

            # Check if we echoed all the bytes back.
            if n != len(data):
                __err("Failed to echo all bytes!")

            if verbose:
                sys.stdout.write("»\n")


def run_server(port, num_pkts, verbose=False):
    """Run TCP echo server."""
    srv = mk_socket(True)

    # TODO: Pass interface rather than hard-code the default.
    srv.bind(('127.0.0.1', port))
    srv.listen(BACKLOG)

    handlers = []

    try:
        with srv:
            while True:
                cli, addr = srv.accept()

                if verbose:
                    print("• received connection from %s:%d" % (addr))

                handler = threading.Thread(target=cli_handler,
                                           args=(cli, addr, num_pkts, verbose))
                handlers.append(handler)

                handler.start()
    except KeyboardInterrupt:
        # Killed from terminal via CTRL-C
        for t in handlers:
            t.join()

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
    parser.add_argument('--target', '-t',
                        metavar='target-IP',
                        type=str,
                        help=('Target IP address for a client to connect'))
    parser.add_argument('--count', '-c',
                        type=int,
                        default=DEF_NUM_PKTS,
                        help='Number of packets (pings) to send')
    main(parser.parse_args())
