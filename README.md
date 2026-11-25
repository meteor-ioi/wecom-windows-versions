# WeCom for Windows Version Archive

Automated archive tracking and release repository for Tencent WeCom (Enterprise WeChat) Windows clients, inspired by [cscnk52/wechat-windows-versions](https://github.com/cscnk52/wechat-windows-versions).

## Features

- **Automated Update Detection**: Periodically polls the official WeCom client endpoint (`work.weixin.qq.com/wework_admin/commdownload`).
- **Release Automation**: When a new version is detected, GitHub Actions downloads the package, computes SHA-256 integrity checksums, and publishes a new GitHub Release.
- **Historical Backfill**: Includes `backfill.py` and a dedicated workflow to sequentially publish historical versions from oldest (`4.0.0.6024`) to newest.

## Workflow Structure

- `.github/workflows/release.yml`: Runs on a cron schedule (`0 * * * *`) and `workflow_dispatch` to detect and publish the latest version.
- `.github/workflows/backfill.yml`: Runs on manual trigger to backfill historical versions defined in `versions.json`.
- `main.py`: Detects current latest release, checks GitHub release status, and prepares assets.
- `backfill.py`: Handles chronological publication of historical versions.

## Usage

1. Initialize git in this directory and push to your GitHub repository.
2. Ensure repository Settings -> Actions -> General -> Workflow permissions is set to **Read and write permissions**.
3. Trigger the **Backfill Historical Releases** workflow via GitHub Actions UI to populate historical releases from oldest to newest.
