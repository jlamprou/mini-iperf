#!/usr/bin/env python


import argparse
import socket
import struct
import sys
import time


def ServerUDP(PORT, SNDB, BSIZE, HOST=0):
    serv = HOST  # IP address which server expect the connection will come from
    port = PORT  # port = PORT  # Arbitrary non-privileged port
    sndbuff = SNDB  # Size of Socket RCVBUFFOR
    buffsize = BSIZE  # size of data in udp datagram
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    except socket.error as serror:
        print('Unable to create a socket ! Error: ', serror)
    except Exception as msg:
        print('Error not related to socket occured ! Error: ', msg)

    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, sndbuff)

    except socket.error as setsckerror:
        print('Unable to set socket options ! Error: ', setsckerror, '\n')
    except Exception as msg:
        print('Error not related to socket occured ! Error: ', msg)

    print('----------------------SERVER----------------------')
    print('Socket created \n')
    print('Server SNDBuff', s.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF))
    print('Server RCVBuff', s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF), '\n')

    try:
        if serv != '0.0.0.0':
            s.bind((host, port))
        elif serv == '0.0.0.0':
            s.bind(('', port))
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()
    except Exception as msg:
        print('Error not related to socket occured ! Error: ', msg)
        sys.exit()

    print('Socket binding complete succesfully')

    while 1:
        print('\n Waiting for connection request !')
        try:
            time_delivered = False

            while time_delivered == False:
                rcv, cliaddr = s.recvfrom(10)
                foo = int(rcv.decode())
                ack = 'ack'.encode()
                s.sendto(ack, cliaddr)
                if rcv is not None:
                    time_delivered = True

        except socket.error as msg:
            if socket.errno.EINTR in msg.args:
                print('A signal was interrupted before any data was available')
                continue
            elif socket.errno.EFAULT in msg.args:
                print('Datagram that is sended is to big, cannot receive it ! ')
                break
            else:
                print('Error occured ! Error : ', msg)
        except Exception as msg:
            print('Error not related to socket occured ! Error: ', msg)

        data = ('z' * buffsize).encode()

        print('user with address:  ', cliaddr[0], ' asked for packets ')
        print('user connected on port: ', cliaddr[1], '\n')

        i = 0
        count = 0  # Nr of datagrams received
        size = 0  # Size od data received
        start_time = time.time()
        while 1:
            try:
                i += 1
                s.sendto(data, cliaddr)
                count = count + 1
                size += len(data)
                if (time.time() - start_time) > foo:
                    s.sendto('Last datagram'.encode(), cliaddr)
                    print('Sended %d segments \n' % i)
                    stop_time = time.time()
                    duration = (stop_time - start_time)
                    trafic = ((size * 8.0) / 1000000) / duration
                    print('Reading from socket in: (%f) s, : in (%d) segments (%d)((%f) mbit/s)\n' % (
                    duration, count, size, trafic))
                    break

            except socket.error as e:
                if socket.errno.ECONNRESET in e.args:
                    print('Connection reseted by host side:', e)
                    break
                else:
                    print('Error occured ! Error:', e)
            except Exception as msg:
                print('Error not related to socket occured ! Error: ', msg)

    s.close()


def ClientUDP(HOST, PORT, RECVB, BSIZE, TIME):
    serv = HOST  # IP addr of server to which we want to connect
    port = PORT  # port = PORT  # Arbitrary non-privileged port
    rcvbuff = RECVB  # Size of Socket RCVBUFFOR
    buff = BSIZE  # size of data in udp datagram
    tim = TIME

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    except socket.error as serror:
        print('Unable to create a socket ! Error: ', serror)
    except Exception as msg:
        print('Error not related to socket occured ! Error: ', msg)

    print('----------------------CLIENT----------------------')
    print('Socket created \n')

    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, rcvbuff)
        s.settimeout(2)
    except socket.error as sckerror:
        print('Setting socket option failed ! Error: ', sckerror, '\n')
    except Exception as elol:
        print('Error not related to socket occured ! Error ', elol)

    print('Client RCVBuff:', s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF))
    print('Client SNDBuff:', s.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF))

    ack_delivered = False
    while ack_delivered == False:
        intro = str(tim).encode()
        try:
            s.sendto(intro, (serv, port))
            ack, servaddr = s.recvfrom(10)
            ack = ack.decode()
            if ack == 'ack':
                ack_delivered = True

        except socket.error as elol:
            print('Unable to send initialization packet to server, Error :', elol)
        except Exception as msg:
            print('Error not related to socket occured ! Error: ', msg)

    count = 0  # Nr of datagrams received
    size = 0  # Size od data received
    start_time = time.time()  # Countdown starts here !

    while 1:
        try:
            data, servaddr = s.recvfrom(buff)

        except socket.error as elol:
            if elol.args[0] in (socket.errno.EAGAIN, socket.errno.EWOULDBLOCK):
                print('Socket descriptor marked nonblocking and no data is waiting to be received')
                break
            elif s.timeout:
                print('2 seconds lasted from last datagram sended by the server ! ')
                break
            elif socket.errno.ECONNRESET in elol.args:
                print('Connection reseted by server side:', elol)
                break
            else:
                print('Unable to receive any data, Error:', elol)
                break
        except Exception as msg:
            print('Error not related to socket occured ! Error: ', msg)

        count = count + 1
        size += len(data)

    stop_time = time.time()
    duration = (stop_time - start_time) - 2
    trafic = ((size * 8.0) / 1000000) / duration
    print('Reading from socket in: (%f) s, : in (%d) segments (%d)((%f) mbit/s)\n' % (duration, count, size, trafic))
    s.close()


def ServerTCP(PORT, SNDB, BSIZE, HOST=0):
    host = HOST  # IP address which server expect the connection will come from
    port = PORT  # PORT nr. on which server will be open for clients
    sndbuff = SNDB  # size of socket SEND buffor
    buffsize = BSIZE  # size od data in tcp segment

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    except socket.error as serror:
        print('Unable to create a socket ! Error: ', serror)

    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, sndbuff)
        l_onoff = 1
        l_linger = 0
        s.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', l_onoff, l_linger))
    except socket.error as setsckerror:
        print('Unable to set socket options ! Error: ', setsckerror, '\n')

    print('----------------------SERVER----------------------')
    print('Socket created \n')
    print('Server SNDBuff', s.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF))
    print('Server RCVBuff', s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF), '\n')

    try:
        if HOST != '0.0.0.0':
            s.bind((host, port))
        else:
            s.bind(('', port))
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    print('Socket binding complete succesfully')

    s.listen(10)
    print('Socket is now listening \n')

    while 1:
        # wait to accept a connection - blocking call
        conn, addr = s.accept()

        rcv = conn.recv(10)
        foo = int(rcv.decode())
        data = ('z' * buffsize).encode()
        print('Connected with ' + addr[0] + ':' + str(addr[1]))

        i = 1
        count = 0  # Nr of segments received
        size = 0  # Size od data received
        start_time = time.time()
        while 1:
            try:
                i += 1
                count = count + 1
                size += len(data.decode())
                conn.send(data)
                if (time.time() - start_time) > foo:
                    stop_time = time.time()
                    duration = stop_time - start_time
                    trafic = ((size * 8.0) / 1000000) / duration
                    print('Reading from socket in: (%f) s, : in (%d) segments (%d)((%f) mbit/s)\n' % (
                    duration, count, size, trafic))
                    conn.close()
                    break

            except socket.error as msg:
                print('send error:', msg)
                break

    print('Sended %d segments \n' % i)
    s.close()


def ClientTCP(HOST, PORT, RECVB, BSIZE, TIME):
    port = PORT  # port = PORT  # Arbitrary non-privileged port
    rcvbuff = RECVB  # Size of Socket RCVBUFFOR
    buff = BSIZE  # size of data in tcp seg
    host = HOST  # IP addr of server to which we want to connect
    tim = TIME
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as serror:
        print('Unable to create a socket ! Error: ', serror)

    print('----------------------CLIENT----------------------')
    print('Socket created \n')

    # Bind socket to local host and port
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, rcvbuff)
    except socket.error as sckerror:
        print('Setting socket option failed ! Error: ', sckerror, '\n')

    try:
        s.connect((host, port))
    except socket.error as msg:
        if socket.errno.ECONNRESET in msg.args:
            print('Connection reseted by peer side:', msg)
        elif socket.errno.EINTR in msg.args:
            print('A signal was interrupted before any data was available')
        else:
            print('Cannot connect to the server ! ', msg, '\n')
            sys.exit()

    print('Client RCVBuff:', s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF))
    print('Client SNDBuff:', s.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF))
    print('Client MSS:', s.getsockopt(socket.SOL_TCP, socket.TCP_MAXSEG), '\n')
    print('Socket connect succesfully')

    intro = str(tim).encode()

    count = 0  # Nr of segments received
    size = 0  # Size od data received
    start_time = time.time()  # Countdown starts here !

    while 1:
        try:
            s.send(intro)
            x = s.recv(buff).decode()
        except socket.error as elol:
            print('Connection closed')
            break

        if not x:
            break
        data = len(x)
        count = count + 1
        size += data

    stop_time = time.time()
    duration = stop_time - start_time
    trafic = ((size * 8.0) / 1000000) / duration
    print('Reading from socket in: (%f) s, : in (%d) segments (%d)((%f) mbit/s)\n' % (duration, count, size, trafic))
    s.close()


def Main():
    parser = argparse.ArgumentParser(
        description='IPERF like script, IP address of socket on/to which you want to connect is REQUIRED, also option if you want to run SERVER or CLIENT')
    parser.add_argument('-s', '--server', help='If you want to run server', action='store_true', default=False)
    parser.add_argument('-c', '--client', help='If you want to run client', action='store_true', default=False)
    parser.add_argument('-i', '--ip',
                        help='host/serv ip address, if you write ip address on server, server will expect connection only from this particular IP, if multicast is enabled and we '
                             ' pass something here, server will bind with mcastgrp addr ! ', nargs='?', type=str,
                        default='0.0.0.0')
    parser.add_argument('-p', '--port', help='Port number, default port nr. is 8888', type=int, default=8888, nargs='?')
    parser.add_argument('-l', '--len', help='Lenght of buffers to read and write, default = 128000', nargs='?',
                        default=128000, type=int)
    parser.add_argument('-bs', '--buffsize',
                        help='Option which controls amound of data that is transmitted every datagram, default = 8000',
                        nargs='?', default=8000, type=int)
    parser.add_argument('-t', '--time', help='ONLY client option -> how much time measurment lasts, default = 10s',
                        default=10, nargs='?', type=int)
    parser.add_argument('-T', '--TCP', help='If you want to use TCP ', action='store_true', default=False)
    parser.add_argument('-U', '--UDP', help='If you want to use UDP', action='store_true', default=False)

    args = parser.parse_args()

    if args.server and args.TCP and not args.client and not args.UDP:
        ServerTCP(args.port, args.len, args.buffsize, args.ip)
    elif args.server and args.UDP and not args.client and not args.TCP:
        ServerUDP(args.port, args.len, args.buffsize, args.ip)
    elif args.client and args.UDP and not args.server and not args.TCP:
        ClientUDP(args.ip, args.port, args.len, args.buffsize, args.time)
    elif args.client and args.TCP and not args.server and not args.UDP:
        ClientTCP(args.ip, args.port, args.len, args.buffsize, args.time)
    elif args.TCP and args.UDP:
        print('You should chose either TCP or UDP ! ')
    elif args.server and args.client:
        print('You need to select either CLIENT or SERVER ! ')
    else:
        print('Something went wrong ! ')


if __name__ == '__main__':
    Main()