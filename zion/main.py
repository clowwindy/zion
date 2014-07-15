#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import struct
import fcntl
import select
import socket
import logging
import argparse


BUF_SIZE = 2048


def open_tun(name='tunnel'):
    tun_fd = os.open('/dev/net/tun', os.O_RDWR)
    print tun_fd
    data = struct.pack('@16sh22s', name, 2, '')
    with open('test2', 'wb') as f2:
        f2.write(data)
    print (ord('T') << 8) | 202
    # if this doesn't work, compile and run main.c and update the number
    fcntl.ioctl(tun_fd, 1074025674, data)
    return tun_fd


def open_udp(bind_address):
    if not bind_address:
        bind_address = ('0.0.0.0', 53)
    addrs = socket.getaddrinfo(bind_address[0], bind_address[1], 0,
                               socket.SOCK_DGRAM, socket.SOL_UDP)
    if len(addrs) == 0:
        raise Exception("can't get addrinfo for %s:%d" % bind_address)
    af, socktype, proto, canonname, sa = addrs[0]
    sock = socket.socket(af, socktype, proto)
    sock.bind(bind_address)
    sock.setblocking(False)
    return sock


def main():
    assert 'linux' in sys.platform
    # other os not supported now

    config = parse_args()
    logging.info("starting zion")
    remote_addr = (config['server'], int(config['server_port']))
    bind_addr = (config['local'], int(config['local_port']))
    tun = open_tun(config['device'])
    udp = open_udp(bind_addr)
    # currently only raw supported
    assert config['proto'] == 'raw'
    while True:
        rlist, wlist, xlist = select.select([tun, udp], [], [])
        # TODO raw proto implemented, move on to implement DNS proto
        if tun in rlist:
            data = os.read(tun, BUF_SIZE)
            udp.sendto(data, remote_addr)
        if udp in rlist:
            data, remote_addr = udp.recvfrom(BUF_SIZE)
            os.write(tun, data)


def parse_args():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', filemode='a+')

    parser = argparse.ArgumentParser(description='Forward DNS requests.')
    parser.add_argument('-d', '--device', metavar='DEVICE_NAME', type=str)
    parser.add_argument('-b', '--local', metavar='BIND_ADDRESS', type=str)
    parser.add_argument('-l', '--local_port', metavar='BIND_PORT', type=int)
    parser.add_argument('-s', '--server', metavar='SERVER', type=str)
    parser.add_argument('-p', '--server-port', metavar='SERVER_PORT', type=int)
    parser.add_argument('-t', '--proto', metavar='protocol', type=str,
                        default='raw')

    config = vars(parser.parse_args())
    return config

if __name__ == '__main__':
    main()
