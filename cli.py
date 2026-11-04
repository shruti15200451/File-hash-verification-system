"""Command-line interface for the File Hash Verification System.

Examples:
    python cli.py register report.pdf --owner "Ravi" --note "Final draft"
    python cli.py verify report.pdf
    python cli.py list
    python cli.py validate
    python cli.py tamper 1
"""
import argparse
import datetime
import os
import sys

from blockchain import Blockchain, hash_file

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "chain.json")


def fmt_time(ts: float) -> str:
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def main() -> int:
    parser = argparse.ArgumentParser(description="Blockchain-based file hash verification")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("register", help="register a file's hash on the blockchain")
    p.add_argument("file")
    p.add_argument("--owner", default="")
    p.add_argument("--note", default="")

    p = sub.add_parser("verify", help="verify a file against the blockchain")
    p.add_argument("file")

    sub.add_parser("list", help="list all blocks")
    sub.add_parser("validate", help="validate the whole chain")

    p = sub.add_parser("tamper", help="demo: simulate tampering with block N (on a copy)")
    p.add_argument("index", type=int)

    args = parser.parse_args()
    bc = Blockchain(path=DATA_PATH)

    if args.cmd == "register":
        digest, size = hash_file(args.file)
        block, created = bc.add_file_record(os.path.basename(args.file), digest, size, args.owner, args.note)
        if created:
            print(f"Registered in block #{block.index}")
        else:
            print(f"Already registered earlier in block #{block.index} ({fmt_time(block.timestamp)})")
        print(f"SHA-256: {digest}")

    elif args.cmd == "verify":
        digest, _ = hash_file(args.file)
        res = bc.verify_file(digest, os.path.basename(args.file))
        print(f"SHA-256: {digest}")
        print(f"Result : {res['status']}")
        if res["block"]:
            b = res["block"]
            print(f"Block  : #{b['index']}  registered {fmt_time(b['timestamp'])}  owner={b['data'].get('owner')!r}")
        for e in res["errors"]:
            print("  !", e)
        return 0 if res["status"] == "VERIFIED" else 1

    elif args.cmd == "list":
        for b in bc.chain:
            print(f"#{b.index}  {fmt_time(b.timestamp)}  nonce={b.nonce}")
            print(f"    hash: {b.hash}")
            print(f"    prev: {b.previous_hash}")
            print(f"    data: {b.data}")

    elif args.cmd == "validate":
        ok, errors = bc.is_valid()
        print("Chain is VALID" if ok else "Chain is INVALID")
        for e in errors:
            print("  !", e)
        return 0 if ok else 1

    elif args.cmd == "tamper":
        ok, errors = bc.simulate_tampering(args.index)
        print(f"Tampered copy of block #{args.index} -> {'VALID' if ok else 'INVALID (tampering detected)'}")
        for e in errors:
            print("  !", e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
