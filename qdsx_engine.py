#!/usr/bin/env python3
# QDSX Engine — single-file, Android-safe compressor

import os, sys, json, struct, time, hashlib, random
import zlib, bz2, lzma
from pathlib import Path

LOG_DIR = Path("./QDSX_logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

MAGIC   = b"QDSX"
VERSION = 2

def sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()

def log(msg: str) -> None:
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_DIR / "qdsx.log", "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")

# ----------------- transforms -----------------

def tf_none(data: bytes) -> bytes:  return data
def itf_none(data: bytes) -> bytes: return data

def tf_delta(data: bytes) -> bytes:
    out  = bytearray()
    prev = 0
    for b in data:
        out.append((b - prev) & 0xFF)
        prev = b
    return bytes(out)

def itf_delta(data: bytes) -> bytes:
    out  = bytearray()
    prev = 0
    for b in data:
        val = (b + prev) & 0xFF
        out.append(val)
        prev = val
    return bytes(out)

def tf_rle(data: bytes) -> bytes:
    out = bytearray()
    i   = 0
    n   = len(data)
    while i < n:
        b   = data[i]
        run = 1
        i  += 1
        while i < n and data[i] == b and run < 255:
            run += 1
            i   += 1
        out.append(b)
        out.append(run)
    return bytes(out)

def itf_rle(data: bytes) -> bytes:
    out = bytearray()
    it  = iter(data)
    for b, run in zip(it, it):
        out.extend([b] * run)
    return bytes(out)

# ------------- BWT + MTF + RLE ----------------

def bwt_transform(data: bytes):
    n = len(data)
    if n == 0:
        return b"", 0
    rotations = range(n)
    def rot_key(i):
        return data[i:] + data[:i]
    order   = sorted(rotations, key=rot_key)
    primary = order.index(0)
    last_col = bytearray(n)
    for r, i in enumerate(order):
        last_col[r] = data[i - 1] if i != 0 else data[-1]
    return bytes(last_col), primary

def bwt_inverse(last_col: bytes, primary: int) -> bytes:
    n = len(last_col)
    if n == 0:
        return b""
    last  = list(last_col)
    first = sorted([(b, i) for i, b in enumerate(last)])

    count_map = {}
    occ_last  = []
    for b in last:
        c = count_map.get(b, 0) + 1
        count_map[b] = c
        occ_last.append(c)

    count_map.clear()
    occ_first = []
    for b, _ in first:
        c = count_map.get(b, 0) + 1
        count_map[b] = c
        occ_first.append(c)

    pos_first = {}
    for idx, ((b, _), k) in enumerate(zip(first, occ_first)):
        pos_first[(b, k)] = idx

    LF = [pos_first[(last[r], occ_last[r])] for r in range(n)]

    res = bytearray(n)
    r   = primary
    for i in range(n - 1, -1, -1):
        res[i] = last[r]
        r      = LF[r]
    return bytes(res)

def mtf_encode(data: bytes) -> bytes:
    alphabet = list(range(256))
    out      = []
    for b in data:
        idx = alphabet.index(b)
        out.append(idx)
        alphabet.pop(idx)
        alphabet.insert(0, b)
    return bytes(out)

def mtf_decode(data: bytes) -> bytes:
    alphabet = list(range(256))
    out      = []
    for idx in data:
        b = alphabet[idx]
        out.append(b)
        alphabet.pop(idx)
        alphabet.insert(0, b)
    return bytes(out)

def tf_bwt_mtf_rle(data: bytes) -> bytes:
    bwt, primary = bwt_transform(data)
    mtf          = mtf_encode(bwt)
    return struct.pack(">I", primary) + tf_rle(mtf)

def itf_bwt_mtf_rle(payload: bytes) -> bytes:
    if len(payload) < 4:
        return b""
    primary = struct.unpack(">I", payload[:4])[0]
    mtf_rle = payload[4:]
    mtf     = itf_rle(mtf_rle)
    bwt_last = mtf_decode(mtf)
    return bwt_inverse(bwt_last, primary)

TRANSFORMS = {
    "none":        (tf_none,        itf_none),
    "delta":       (tf_delta,       itf_delta),
    "rle":         (tf_rle,         itf_rle),
    "bwt_mtf_rle": (tf_bwt_mtf_rle, itf_bwt_mtf_rle),
}

# ----------------- codecs ---------------------

CODECS = {
    "zlib": (lambda b: zlib.compress(b, 9),
             lambda b: zlib.decompress(b)),
    "bz2":  (lambda b: bz2.compress(b, 9),
             lambda b: bz2.decompress(b)),
    "lzma": (lambda b: lzma.compress(b, preset=9 | lzma.PRESET_EXTREME),
             lambda b: lzma.decompress(b)),
}

# -------------- header helpers ----------------

def encode_header(header: dict) -> bytes:
    hdr = json.dumps(header, sort_keys=True).encode("utf-8")
    return MAGIC + struct.pack(">I", VERSION) + struct.pack(">I", len(hdr)) + hdr

def parse_header(blob: bytes):
    if len(blob) < 12:
        raise RuntimeError("Blob too small for QDSX header")
    if blob[:4] != MAGIC:
        raise RuntimeError("Bad QDSX magic")
    off     = 4
    version = struct.unpack(">I", blob[off:off+4])[0]; off += 4
    hlen    = struct.unpack(">I", blob[off:off+4])[0]; off += 4
    if off + hlen > len(blob):
        raise RuntimeError("Corrupt QDSX header length")
    hdr_json = blob[off:off+hlen]
    off     += hlen
    header   = json.loads(hdr_json.decode("utf-8"))
    cdata    = blob[off:]
    return version, header, cdata

# ---------------- pack / unpack ---------------

def qdsx_pack(path: str) -> str:
    with open(path, "rb") as f:
        raw = f.read()

    if not raw:
        header = {
            "version":      VERSION,
            "orig_name":    os.path.basename(path),
            "orig_size":    0,
            "orig_sha256":  sha256_bytes(b""),
            "transform":    "none",
            "codec":        "none",
            "timestamp":    time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        blob    = encode_header(header)
        outpath = path + ".qdsx"
        with open(outpath, "wb") as f:
            f.write(blob)
        log(f"PACK {path} (empty) -> {outpath}")
        return outpath

    orig_sha  = sha256_bytes(raw)
    best_size = None
    best_key  = None

    for tname, (tf, _) in TRANSFORMS.items():
        try:
            tdata = tf(raw)
        except Exception as e:
            log(f"TRANSFORM FAIL {tname} on {path}: {e}")
            continue
        for cname, (enc, _) in CODECS.items():
            try:
                cdata = enc(tdata)
            except Exception as e:
                log(f"CODEC FAIL {cname} on {path} ({tname} stage): {e}")
                continue
            size = len(cdata)
            if best_size is None or size < best_size:
                best_size = size
                best_key  = (tname, cname, cdata)

    if best_key is None:
        raise RuntimeError("No working transform/codec combo for file")

    tname, cname, cdata = best_key

    header = {
        "version":      VERSION,
        "orig_name":    os.path.basename(path),
        "orig_size":    len(raw),
        "orig_sha256":  orig_sha,
        "transform":    tname,
        "codec":        cname,
        "timestamp":    time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    blob    = encode_header(header) + cdata
    outpath = path + ".qdsx"

    with open(outpath, "wb") as f:
        f.write(blob)

    # self-check
    restored = qdsx_unpack(outpath, return_bytes=True)
    if restored != raw:
        raise RuntimeError("QDSX integrity fail on self-check")

    ratio = best_size / max(1, len(raw))
    log(f"PACK {path} -> {outpath} using {tname}+{cname}, ratio={ratio:.3f}")
    return outpath

def qdsx_unpack(qpath: str, return_bytes: bool = False):
    with open(qpath, "rb") as f:
        blob = f.read()

    _, header, cdata = parse_header(blob)
    tname = header.get("transform", "none")
    cname = header.get("codec", "none")

    if header.get("orig_size", 0) == 0 and cname == "none":
        raw = b""
    else:
        _, dec = CODECS[cname]
        _, itf = TRANSFORMS[tname]
        raw = itf(dec(cdata))

    if sha256_bytes(raw) != header["orig_sha256"]:
        raise RuntimeError("Checksum mismatch while unpacking")

    if return_bytes:
        return raw

    out = str(Path(qpath).with_suffix(""))
    with open(out, "wb") as f:
        f.write(raw)
    log(f"UNPACK {qpath} -> {out}")
    return out

# ---------------- benchmark stuff -------------

def make_synth() -> bytes:
    rng  = random.Random(1234)
    txt  = ("\n".join(
        ["QDS variance law σ(H)/H=A R^{-p} with p≈0.35"] * 200
    )).encode("utf-8")
    ramp  = bytes([i % 256 for i in range(65536)])
    js    = ("\n".join(
        json.dumps({"k": i % 7, "v": "abcde" * 3}) for i in range(2000)
    )).encode("utf-8")
    noise = bytes(rng.getrandbits(8) for _ in range(65536))
    return b"".join([txt, ramp, js, noise])

def summarize(path, outpath, tname, cname, raw, cmpd):
    ratio = cmpd / max(1, raw)
    print(f"{os.path.basename(path):25s} Raw:{raw:8d} → "
          f"{os.path.basename(outpath):20s} {ratio:6.3f} [{tname}+{cname}]")

def bench(paths):
    print("QDSX BENCHMARK")
    print("-" * 60)
    for p in paths:
        try:
            out = qdsx_pack(p)
            with open(out, "rb") as f:
                blob = f.read()
            _, hdr, cdata = parse_header(blob)
            summarize(p, out, hdr["transform"], hdr["codec"],
                      hdr["orig_size"], len(cdata))
        except Exception as e:
            print(f"ERROR: {p} {e}")

# ------------------- CLI ----------------------

def main():
    if len(sys.argv) == 1:
        synth = "./synthetic_payload.bin"
        with open(synth, "wb") as f:
            f.write(make_synth())
        bench([synth])
        return

    if sys.argv[1] in ("-d", "--decompress"):
        if len(sys.argv) < 3:
            print("Usage: qdsx_engine.py -d file.qdsx [more.qdsx...]")
            return
        for qp in sys.argv[2:]:
            try:
                out = qdsx_unpack(qp)
                print(f"Unpacked {qp} -> {out}")
            except Exception as e:
                print(f"ERROR unpacking {qp}: {e}")
        return

    bench(sys.argv[1:])

if __name__ == "__main__":
    main()