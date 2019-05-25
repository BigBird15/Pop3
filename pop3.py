import socket
import ssl
import argparse
from parse import *


def get_args():
    parser = argparse.ArgumentParser(description="Allows you to get the mail messages, including specified "
                                                 "details (like sender, date, etc) and download attachments. "
                                                 "You may find all of them in working directory.")
    parser.add_argument("--s", type=str, default='yandex', help="server name (supported: google/mail/yandex)")
    parser.add_argument("-l", type=str, help="login")
    parser.add_argument("-p", type=str, help="password")
    parser.add_argument("-n", type=int, help="letter number")
    parser.add_argument("-a", type=str, help="additional specified requirements: 'd' = date, 's' = sender, 't' = theme,"
                                             "'r' = recipient, 'm' = message, 'a' = attachments", default='adstrm')

    return parser.parse_args()


def main(login, password, number, server, additionals):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        ssl_sock = ssl.wrap_socket(sock)
        ssl_sock.settimeout(10)

        if server == 'yandex':
            ssl_sock.connect(('pop.yandex.ru', 995))
        if server == 'gmail':
            ssl_sock.connect(('pop.gmail.com', 995))
        if server == 'mail':
            ssl_sock.connect(('pop.mail.ru', 995))

        data = ssl_sock.recv(4096).decode()

        if data[:3] != "+OK":
            sys.exit("Connection failed")

        try:
            ssl_sock.send(("USER " + login + "\r\n").encode())
            data = ssl_sock.recv(4096).decode()
            if data[:3] != "+OK":
                sys.exit("Login problems encountered")

            ssl_sock.send(("PASS " + password + "\r\n").encode())
            data = ssl_sock.recv(4096).decode()
            if data[:3] != "+OK":
                sys.exit("Password problems encountered")
        except socket.timeout:
            sys.exit("Socket timeout")

        try:
            ssl_sock.send("STAT\r\n".encode())
            data = ssl_sock.recv(4096).decode()
            if data[:3] != "+OK":
                sys.exit("STAT problems encountered")
        except socket.timeout:
            sys.exit("STAT timeout")

        try:
            ssl_sock.send("RETR {}\r\n".format(number).encode())
            data = ssl_sock.recv(1024).decode(errors="ignore")
            message = ""
            while data:
                try:
                    if data.split()[0] != '+OK':
                        message += data
                    data = ssl_sock.recv(4096).decode(errors="ignore")
                except socket.timeout:
                    break
            # print(message)
            parse(message, additionals)
        except socket.timeout:
            sys.exit("Getting letter timeout encountered")
        ssl_sock.send("QUIT\r\n".encode())


if __name__ == '__main__':
    args = get_args()
    if (args.l is None) or (args.n is None) or (args.p is None):
        print("Some arguments are missing. \nMake sure you've entered a user name, password and letter number.")
    else:
        main(args.l, args.p, args.n, args.s, args.a)