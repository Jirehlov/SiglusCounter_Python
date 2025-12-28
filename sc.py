import argparse
from pathlib import Path

KEY = bytes.fromhex("8be55dc3a1e030440085c074095f5e33c05b8be55dc38b450c85c075148b55ec83c220526a00e8f528010083c40889450c8b45e46a006a005053ff1534b143008b451085c074058b4dec89088a45f084c07578a1e03044008b7de88b750c85c075448b1dd0b0430085ff763781ff000004006a0076438b45f88d55fc5268000004005650ff152cb143006a05ffd3a1e030440081ef0000040081c60000040085c074c58b5df853e8f4fbffff8b450c83c4045f5e5b8be55dc38b55f88d4dfc51575652ff152cb14300ebd88b45e883c020506a00e8472801008b7de88945f48bf0a1e030440083c40885c075568b1dd0b0430085ff764981ff000004006a0076")

def lzss(s, n):
    c = s[0] + 256; i = 1; o = bytearray()
    while len(o) < n:
        if c == 1: c = s[i] + 256; i += 1
        if c & 1: o.append(s[i]); i += 1
        else:
            t = s[i] | (s[i + 1] << 8); i += 2; off = t >> 4; ln = (t & 15) + 2; st = len(o) - off
            for j in range(ln): o.append(o[st + j])
        c >>= 1
    return o[:n]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input"); ap.add_argument("-o", "--output"); ap.add_argument("--raw")
    a = ap.parse_args()
    ip = Path(a.input); op = Path(a.output) if a.output else ip.with_suffix(".txt")
    d = bytearray(ip.read_bytes())
    x = int.from_bytes(d[8:12], "little"); m = int.from_bytes(d[12:16], "little")
    for i in range(x): d[16 + i] ^= KEY[i & 255]
    b = lzss(d[24:], int.from_bytes(d[20:24], "little"))
    if a.raw:
        with open(a.raw, "wb") as rf:
            rf.write(b)
    q = 0; tr = tc = 0
    with op.open("w", encoding="utf-8-sig", newline="") as f:
        for _ in range(m):
            L = int.from_bytes(b[q:q+4], "little"); q += 4
            name = b[q:q+2*L].decode("utf-16le", "replace"); q += 2 * L
            cnt = int.from_bytes(b[q:q+4], "little"); q += 4
            flags = b[q:q+cnt]; q += cnt
            r = sum(flags) if cnt else 0; tr += r; tc += cnt
            pct = (r * 1000) // cnt if cnt else 0
            f.write(f"{r:6d}/{cnt:6d}   {pct//10:3d}.{pct%10:d}%   {name}\r\n")
        f.write("----------------------------------------\r\n")
        pct = (tr * 10000) // tc if tc else 0
        f.write(f"{tr:6d}/{tc:6d}   {pct//100:3d}.{pct%100:02d}%  (ALL)\r\n")
if __name__ == "__main__":
    main()
