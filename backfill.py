import argparse
import hashlib
import json
import os
import subprocess
import time
import urllib.request
from pathlib import Path

def check_release_exists(repo, tag):
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    api_url = f"https://api.github.com/repos/{repo}/releases/tags/{tag}"
    req = urllib.request.Request(api_url)
    req.add_header("User-Agent", "WeCom-Version-Archiver")
    if token:
        req.add_header("Authorization", f"token {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise

def download_and_hash(url, dest_path):
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    hasher = hashlib.sha256()
    print(f"Downloading from {url} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=300) as resp, open(dest_path, "wb") as f:
        while chunk := resp.read(1024 * 1024):
            hasher.update(chunk)
            f.write(chunk)
    return hasher.hexdigest()

def main():
    parser = argparse.ArgumentParser(description="Backfill historical WeCom releases from oldest to newest.")
    parser.add_argument("--start", type=int, default=0, help="Start index (0-based)")
    parser.add_argument("--limit", type=int, default=0, help="Max versions to process (0 = all)")
    parser.add_argument("--versions-file", type=str, default="versions.json", help="Path to versions JSON file")
    args = parser.parse_args()

    repo = os.getenv("GITHUB_REPOSITORY", "meteor-ioi/wecom-windows-versions")
    with open(args.versions_file, "r", encoding="utf-8") as f:
        items = json.load(f)

    # Ensure strictly sorted from oldest to newest
    def ver_key(item):
        return [int(x) for x in item["version"].split(".")]

    items.sort(key=ver_key)

    total = len(items)
    selected = items[args.start:]
    if args.limit > 0:
        selected = selected[:args.limit]

    print(f"Total available: {total}. Processing {len(selected)} versions starting from index {args.start}...")

    build_dir = Path("build")
    build_dir.mkdir(exist_ok=True)

    for idx, item in enumerate(selected, start=args.start + 1):
        ver = item["version"]
        tag = f"v{ver}"
        url = item["url"]
        size_mb = item.get("size_mb", 0)

        print(f"\n[{idx}/{total}] Checking {tag} ...")
        if check_release_exists(repo, tag):
            print(f"Tag {tag} already exists. Skipping.")
            continue

        installer_path = build_dir / f"WeCom_{ver}.exe"
        try:
            sha256 = download_and_hash(url, installer_path)
            note_content = (
                f"## WeCom Windows Version {ver}\n\n"
                f"- **Version**: `{ver}`\n"
                f"- **Official Download URL**: [{url}]({url})\n"
                f"- **SHA-256**: `{sha256}`\n"
                f"- **Installer Size**: `{size_mb} MB`\n"
                f"- **Archive Date**: `{time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}`\n"
            )
            note_file = build_dir / "releaseNote.md"
            note_file.write_text(note_content, encoding="utf-8")

            print(f"Publishing release for {tag}...")
            cmd = [
                "gh", "release", "create", tag, str(installer_path),
                "--repo", repo,
                "--title", f"WeCom Windows Version {ver}",
                "--notes-file", str(note_file)
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0:
                print(f"Error publishing {tag}: {res.stderr}")
            else:
                print(f"Successfully published release {tag}: {res.stdout.strip()}")

        except Exception as e:
            print(f"Failed processing {ver}: {e}")
        finally:
            if installer_path.exists():
                installer_path.unlink()

        time.sleep(2)

    print("\nBackfill process completed.")

if __name__ == "__main__":
    main()
