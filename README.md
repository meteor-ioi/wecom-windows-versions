# WeCom for Windows Version Archive

Automated archive tracking and release repository for Tencent WeCom (Enterprise WeChat / 企业微信) Windows desktop clients.

[English](README.md) | [简体中文](README.zh-CN.md)

[![Release Latest WeCom](https://github.com/meteor-ioi/wecom-windows-versions/actions/workflows/release.yml/badge.svg)](https://github.com/meteor-ioi/wecom-windows-versions/actions/workflows/release.yml)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/meteor-ioi/wecom-windows-versions/total)
![GitHub Downloads (all assets, latest release)](https://img.shields.io/github/downloads/meteor-ioi/wecom-windows-versions/latest/total)

This project uses `GitHub Actions` to automatically check for updates **every hour**, download the latest official installer, compute SHA-256 integrity checksums, and publish it to the [Releases](https://github.com/meteor-ioi/wecom-windows-versions/releases) section of this repository.

It also supports chronologically backfilling historical releases starting from version 4.0.0.

## Related Projects

- [WeChat Windows Version Archive](https://github.com/cscnk52/wechat-windows-versions) (by @cscnk52)
- [WeChat Windows 64-bit 3.0 Archive](https://github.com/tom-snow/wechat-windows-versions) (by @tom-snow)

## How It Works

- **`.github/workflows/release.yml`**: Runs on a cron schedule (`0 * * * *`) and `workflow_dispatch`. Resolves the official download redirection URL, detects new versions, hashes the installer, and publishes a new GitHub Release.
- **`.github/workflows/backfill.yml`**: Sequentially publishes historical versions from oldest (`4.0.0.6024`) to newest, ensuring the release timeline remains clean and chronologically ordered.
- **`versions.json`**: Curated list of verified historical versions and their official CDN URLs.

## License

This project is licensed under the [MIT License](./LICENSE). The installers belong to Tencent. This project is for archival and development reproduction purposes only.
