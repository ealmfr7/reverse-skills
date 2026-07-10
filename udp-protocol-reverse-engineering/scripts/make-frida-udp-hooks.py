#!/usr/bin/env python3
import argparse
from pathlib import Path


SENDTO_RECVFROM = r'''// Native UDP hooks for authorized runtime analysis.
function sockaddrPort(addr) {
    if (addr.isNull()) return "null";
    const family = addr.readU16();
    if (family === 2) {
        const port = ((addr.add(2).readU8() << 8) | addr.add(3).readU8());
        const ip = [
            addr.add(4).readU8(),
            addr.add(5).readU8(),
            addr.add(6).readU8(),
            addr.add(7).readU8()
        ].join(".");
        return ip + ":" + port;
    }
    return "family=" + family;
}

function dumpBuffer(ptrValue, lenValue) {
    const len = Math.min(Number(lenValue), 256);
    if (ptrValue.isNull() || len <= 0) return;
    console.log(hexdump(ptrValue, { length: len, ansi: false }));
}

const sendtoPtr = Module.findGlobalExportByName("sendto");
if (sendtoPtr) {
    Interceptor.attach(sendtoPtr, {
        onEnter(args) {
            this.len = args[2].toInt32();
            console.log("[sendto] fd=" + args[0].toInt32() + " len=" + this.len + " dst=" + sockaddrPort(args[4]));
            dumpBuffer(args[1], this.len);
        }
    });
}

const recvfromPtr = Module.findGlobalExportByName("recvfrom");
if (recvfromPtr) {
    Interceptor.attach(recvfromPtr, {
        onEnter(args) {
            this.buf = args[1];
        },
        onLeave(retval) {
            const len = retval.toInt32();
            if (len > 0) {
                console.log("[recvfrom] len=" + len);
                dumpBuffer(this.buf, len);
            }
        }
    });
}

const sendmsgPtr = Module.findGlobalExportByName("sendmsg");
if (sendmsgPtr) {
    Interceptor.attach(sendmsgPtr, {
        onEnter(args) {
            console.log("[sendmsg] fd=" + args[0].toInt32() + " msghdr=" + args[1] + " flags=" + args[2].toInt32());
        }
    });
}

const recvmsgPtr = Module.findGlobalExportByName("recvmsg");
if (recvmsgPtr) {
    Interceptor.attach(recvmsgPtr, {
        onEnter(args) {
            this.msg = args[1];
        },
        onLeave(retval) {
            const len = retval.toInt32();
            if (len > 0) {
                console.log("[recvmsg] len=" + len + " msghdr=" + this.msg);
            }
        }
    });
}
'''


DATAGRAM_SOCKET = r'''// Java DatagramSocket hooks for authorized runtime analysis.
if (Java.available) {
    Java.perform(function () {
        const DatagramSocket = Java.use("java.net.DatagramSocket");
        DatagramSocket.send.implementation = function (packet) {
            console.log("[DatagramSocket.send] " + packet.getAddress() + ":" + packet.getPort() + " len=" + packet.getLength());
            return this.send(packet);
        };
        DatagramSocket.receive.implementation = function (packet) {
            const ret = this.receive(packet);
            console.log("[DatagramSocket.receive] " + packet.getAddress() + ":" + packet.getPort() + " len=" + packet.getLength());
            return ret;
        };
    });
}
'''


def main():
    parser = argparse.ArgumentParser(description="Generate Frida UDP hook templates.")
    parser.add_argument("--mode", choices=["native", "java", "both"], default="both")
    parser.add_argument("--out")
    args = parser.parse_args()

    parts = []
    if args.mode in {"native", "both"}:
        parts.append(SENDTO_RECVFROM)
    if args.mode in {"java", "both"}:
        parts.append(DATAGRAM_SOCKET)
    js = "\n\n".join(parts)
    if args.out:
        Path(args.out).write_text(js, encoding="utf-8")
    else:
        print(js)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
