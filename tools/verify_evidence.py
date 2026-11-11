"""Verify archived bytes only; does not import or execute project code."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def checked_path(relative):
    path = ROOT / relative
    if path.is_symlink() or not path.resolve().is_relative_to(ROOT):
        raise ValueError(f"Invalid archive path: {relative}")
    return path


def main():
    manifest = json.loads((ROOT / "REPOSITORY_MANIFEST.json").read_text())
    expected = {item["path"] for item in manifest["files"]}
    actual = {
        f.relative_to(ROOT).as_posix()
        for f in ROOT.rglob("*")
        if f.is_file() and ".git" not in f.relative_to(ROOT).parts
        and f.relative_to(ROOT).as_posix() != "REPOSITORY_MANIFEST.json"
    }
    if expected != actual:
        raise ValueError(f"File set differs: missing={expected-actual}, extra={actual-expected}")
    for item in manifest["files"]:
        data = checked_path(item["path"]).read_bytes()
        if len(data) != item["bytes"] or hashlib.sha256(data).hexdigest() != item["sha256"]:
            raise ValueError(f"Manifest mismatch: {item['path']}")
    receipt = json.loads((ROOT / "publication/SOURCE_COPY_RECEIPT.json").read_text())
    for item in receipt["copied"]:
        data = checked_path(item["repository_path"]).read_bytes()
        if len(data) != item["bytes"] or hashlib.sha256(data).hexdigest() != item["sha256"]:
            raise ValueError(f"Source copy mismatch: {item['repository_path']}")
    for item in receipt["omitted"]:
        if (ROOT / "evidence" / item["source_package_path"]).exists():
            raise ValueError(f"Excluded file present: {item['source_package_path']}")
    print(json.dumps({"status": "PASS", "manifest_files": len(expected),
                      "source_copies": len(receipt["copied"]),
                      "documented_omissions": len(receipt["omitted"]),
                      "archived_code_executed": False}, indent=2))


if __name__ == "__main__":
    main()
