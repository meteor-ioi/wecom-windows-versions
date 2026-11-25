import os
import re
import hashlib
import json
import urllib.request
from pathlib import Path

OFFICIAL_REDIRECT_URL = "https://work.weixin.qq.com/wework_admin/commdownload?platform=win&from=wwindex"

class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        return fp

def get_latest_official():
    opener = urllib.request.build_opener(NoRedirectHandler)
    req = urllib.request.Request(
        OFFICIAL_REDIRECT_URL,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    resp = opener.open(req)
    location = resp.headers.get("Location")
    if not location:
        raise RuntimeError("Failed to resolve official download redirect Location header.")

    m = re.search(r"WeCom_([0-9\.]+)\.exe", location)
    if not m:
        raise RuntimeError(f"Unable to extract version from URL: {location}")

    version = m.group(1)

    # HEAD to get Last-Modified and Content-Length
    head_req = urllib.request.Request(location, method="HEAD")
    with urllib.request.urlopen(head_req, timeout=10) as head_resp:
        last_modified = head_resp.headers.get("Last-Modified", "")
        content_length = int(head_resp.headers.get("Content-Length", 0))

    return {
        "version": version,
        "url": location,
        "last_modified": last_modified,
        "size_mb": round(content_length / (1024 * 1024), 2)
    }

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
    with urllib.request.urlopen(req, timeout=180) as resp, open(dest_path, "wb") as f:
        while chunk := resp.read(1024 * 1024):
            hasher.update(chunk)
            f.write(chunk)
    return hasher.hexdigest()


def update_versions_md(version, size_mb, url):
    versions_file = Path("VERSIONS.md")
    if not versions_file.exists():
        return
    content = versions_file.read_text(encoding="utf-8")
    new_row = f"| {version} | {size_mb} MB | [{url}]({url}) |"
    lines = content.splitlines()
    header_idx = -1
    for idx, line in enumerate(lines):
        if line.strip().startswith("| :---"):
            header_idx = idx
            break
    if header_idx != -1:
        lines.insert(header_idx + 1, new_row)
        versions_file.write_text("
".join(lines) + "
", encoding="utf-8")
        print(f"Updated VERSIONS.md with new version {version}")

def main():
    repo = os.getenv("GITHUB_REPOSITORY", "meteor-ioi/wecom-windows-versions")
    info = get_latest_official()
    version = info["version"]
    tag = f"v{version}"
    print(f"Official latest version: {version}")

    exists = check_release_exists(repo, tag)
    updated = not exists

    build_dir = Path("build")
    build_dir.mkdir(exist_ok=True)
    artifact_path = build_dir / f"WeCom_{version}.exe"

    if updated:
        print(f"New version detected! Preparing release for {tag}...")
        sha256 = download_and_hash(info["url"], artifact_path)
        release_note = (
            f"## WeCom Windows Version {version}\n\n"
            f"- **Version**: `{version}`\n"
            f"- **Official Download URL**: [{info['url']}]({info['url']})\n"
            f"- **SHA-256**: `{sha256}`\n"
            f"- **Installer Size**: `{info['size_mb']} MB`\n"
            f"- **Last Modified**: `{info['last_modified']}`\n"
        )
        (build_dir / "releaseNote.md").write_text(release_note, encoding="utf-8")
        update_versions_md(version, info["size_mb"], info["url"])
        print("Release note generated.")
    else:
        print(f"Release {tag} already exists. No update required.")

    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"updated={str(updated).lower()}\n")
            f.write(f"version={version}\n")
            f.write(f"tag={tag}\n")
            f.write(f"artifact={str(artifact_path)}\n")

if __name__ == "__main__":
    main()
