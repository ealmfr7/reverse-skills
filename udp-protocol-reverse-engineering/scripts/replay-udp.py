#!/usr/bin/env python3
import argparse
import socket
from pathlib import Path


def parse_payload(value, from_file=False):
    if from_file:
        return Path(value).read_bytes()
    return bytes.fromhex(value.replace(":", "").replace(" ", ""))


def main():
    parser = argparse.ArgumentParser(description="Replay a single UDP payload to an authorized lab endpoint.")
    parser.add_argument("host")
    parser.add_argument("port", type=int)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--hex", dest="hex_payload")
    group.add_argument("--file")
    parser.add_argument("--timeout", type=float, default=2.0)
    args = parser.parse_args()

    payload = parse_payload(args.file, True) if args.file else parse_payload(args.hex_payload)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(args.timeout)
        sock.sendto(payload, (args.host, args.port))
        print(f"SENT:{len(payload)} bytes to {args.host}:{args.port}")
        try:
            data, addr = sock.recvfrom(65535)
            print(f"RECV:{len(data)} bytes from {addr[0]}:{addr[1]} {data.hex()}")
        except socket.timeout:
            print("RECV_TIMEOUT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
