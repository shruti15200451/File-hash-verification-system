"""Flask web interface for the File Hash Verification System."""
import datetime
import os

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

from blockchain import Blockchain
from blockchain.hasher import hash_stream

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "chain.json")
MAX_UPLOAD_MB = 50


def create_app(chain_path: str = DATA_PATH, difficulty: int = 3) -> Flask:
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024
    bc = Blockchain(difficulty=difficulty, path=chain_path)

    @app.template_filter("dt")
    def fmt_dt(ts):
        return datetime.datetime.fromtimestamp(ts).strftime("%d %b %Y, %H:%M:%S")

    @app.route("/")
    def index():
        ok, errors = bc.is_valid()
        return render_template(
            "index.html",
            total_blocks=len(bc.chain),
            files=len(bc.chain) - 1,
            valid=ok,
            recent=list(reversed(bc.chain[1:]))[:5],
        )

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            f = request.files.get("file")
            if not f or not f.filename:
                flash("Please choose a file.", "error")
                return redirect(url_for("register"))
            digest, size = hash_stream(f.stream)
            block, created = bc.add_file_record(
                f.filename, digest, size,
                request.form.get("owner", "").strip(),
                request.form.get("note", "").strip(),
            )
            return render_template("result.html", mode="register", created=created,
                                   block=block.to_dict(), digest=digest)
        return render_template("register.html")

    @app.route("/verify", methods=["GET", "POST"])
    def verify():
        if request.method == "POST":
            f = request.files.get("file")
            pasted = request.form.get("hash", "").strip().lower()
            if f and f.filename:
                digest, _ = hash_stream(f.stream)
                filename = f.filename
            elif pasted:
                digest, filename = pasted, None
            else:
                flash("Upload a file or paste a SHA-256 hash.", "error")
                return redirect(url_for("verify"))
            res = bc.verify_file(digest, filename)
            return render_template("result.html", mode="verify", res=res, digest=digest,
                                   filename=filename)
        return render_template("verify.html")

    @app.route("/chain")
    def chain_view():
        ok, errors = bc.is_valid()
        return render_template("chain.html", blocks=bc.chain, valid=ok, errors=errors)

    @app.route("/demo/tamper/<int:index>")
    def tamper_demo(index):
        ok, errors = bc.simulate_tampering(index)
        return render_template("tamper.html", index=index, ok=ok, errors=errors,
                               total=len(bc.chain))

    @app.route("/api/chain")
    def api_chain():
        ok, errors = bc.is_valid()
        return jsonify({"valid": ok, "errors": errors, "length": len(bc.chain), "chain": bc.to_list()})

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
