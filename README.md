# File Hash Verification System (Blockchain)

A final-year project that proves a file has **not been modified** by storing its SHA-256 fingerprint on a custom blockchain with Proof-of-Work.

- Pure-Python blockchain (no external blockchain library, so every part is explainable in a viva)
- Flask web interface + command-line interface
- Tamper detection with a safe, non-destructive demo
- 12 unit tests

## How it works

1. **Register**: the file is hashed with SHA-256 (streamed, never stored). The hash, file name, size, owner and timestamp go into a new block. The block is *mined* (Proof-of-Work) and linked to the previous block's hash.
2. **Verify**: hash the file again and look it up on the chain.
   - `VERIFIED`: hash is on the chain, file is unchanged
   - `MODIFIED`: a file with this name was registered, but the hash differs
   - `NOT_FOUND`: never registered
   - `CHAIN_INVALID`: hash found but the chain itself fails validation
3. **Validate**: re-compute every block hash, check every `previous_hash` link and every proof-of-work.

## Setup

Requires Python 3.10+.

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS
pip install -r requirements.txt
```

## Run the web app

```bash
python app.py
```

Open http://127.0.0.1:5000

| Page | Purpose |
|---|---|
| `/` | Dashboard: files registered, chain status |
| `/register` | Upload a file and add it to the chain |
| `/verify` | Upload a file (or paste a hash) to verify |
| `/chain` | Visual view of all blocks |
| `/demo/tamper/1` | Shows tampering detection (works on a copy) |
| `/api/chain` | Full chain as JSON |

## Run the CLI

```bash
python cli.py register myfile.pdf --owner "Your Name" --note "Final version"
python cli.py verify myfile.pdf
python cli.py list
python cli.py validate
python cli.py tamper 1
```

## Run the tests

```bash
python -m unittest discover -s tests -t .
```

## Project structure

```
file_hash_blockchain/
├── app.py                  Flask web app
├── cli.py                  Command-line tool
├── blockchain/
│   ├── block.py            Block, SHA-256 block hash, mining (PoW)
│   ├── chain.py            Chain, register/verify, validation, JSON storage
│   └── hasher.py           Streaming file hashing
├── templates/              HTML pages (Jinja2)
├── static/style.css
├── tests/test_blockchain.py
├── docs/PROJECT_REPORT.md  Report text for your submission
└── data/chain.json         Created on first run (the ledger)
```

## Configuration

- Mining difficulty: `Blockchain(difficulty=3)` (number of leading zeros). Higher = slower mining.
- Upload limit: `MAX_UPLOAD_MB` in `app.py` (default 50 MB).
- Set a real `SECRET_KEY` environment variable if you ever deploy it.

## Limitations (mention these in your viva)

- Single-node chain: it detects tampering but a single owner of the server could rebuild the whole chain. A real deployment needs multiple nodes and consensus.
- Hashing proves a file is identical; it cannot say *who* created it (no digital signatures yet).
- JSON file storage is for demonstration; use a database for scale.
