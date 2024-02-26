#!/usr/bin/env python3

import socket
import argparse
import sys

def send_command(sock, command):
    sock.send(command + b'\r\n')
    return sock.recv(1024)

def check_user(sock, username, vrfy_check, expn_check):
    if vrfy_check:
        try_vrfy(sock, username)
    elif expn_check:
        try_expn(sock, username)
    else:
        try_rcpt(sock, username)

def try_vrfy(sock, username):
    vrfy_result = send_command(sock, f'VRFY {username}'.encode())

    if b"not recognized" in vrfy_result:
        print("VRFY command not recognized. Exiting.")
        return False

    if b"252" in vrfy_result:
        print(f"User {username} found using VRFY!")
    else:
        print(f"User {username} not found.")

def try_expn(sock, username):
    expn_result = send_command(sock, f'EXPN {username}'.encode())

    if b"not recognized" in expn_result:
        print("EXPN command not recognized. Skipping.")
        return False
    
    if b"252" in expn_result:
        print(f"User {username} found using EXPN!")
    else:
        print(f"User {username} not found using EXPN.")

# Need to recheck
def try_rcpt(sock, username):
    mail = f"MAIL FROM: <{username}>\r\n".encode()
    mail_from_result = send_command(sock, mail)
    
    if b"250 OK" not in mail_from_result:
        print("Error: MAIL FROM command failed.")
        return False

    rcpt = f'RCPT TO: <{username}>\r\n'.encode()
    rcpt_result = send_command(sock, rcpt)

    if b"250 OK" in rcpt_result:
        print(f"User {username} found using RCPT TO!")
        return True
    elif b"502 5.5.2 Error: command not recognized" in rcpt_result:
        print("RCPT TO command not recognized. Exiting.")
        sys.exit(1)
    else:
        print(f"Unable to determine the existence of user {username} using RCPT TO.")
        return False

def main():
    script_name = sys.argv[0]
    parser = argparse.ArgumentParser(description=f"python3 {script_name} --ip ip_address --file your_wordlist")
    parser.add_argument("--user", help="Username to check", type=str)
    parser.add_argument("--file", help="File with a list of usernames", type=argparse.FileType("r"))
    parser.add_argument("--ip", help="Target server IP address", type=str, required=True)
    parser.add_argument("--port", help="SMTP port (default is 25)", default=25, type=int)
    args = parser.parse_args()
    vrfy_check = True
    expn_check = True

    if not args.user and not args.file:
        print("Please specify --user or --file.")
        sys.exit(1)

    try:
        with socket.create_connection((args.ip, args.port)) as sock:
            banner = sock.recv(1024)
            print(banner)

            if args.user:
                check_user(sock, args.user, vrfy_check, expn_check)
            else:
                for line in args.file:
                    check_user(sock, line.strip(), vrfy_check, expn_check)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
