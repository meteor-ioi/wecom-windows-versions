# 企业微信 Windows 历史版本归档库 (WeCom for Windows Archive)

自动化追踪、下载并发布企业微信 (WeCom) Windows 桌面端历史版本的 GitHub 归档仓库。

[English](README.md) | [简体中文](README.zh-CN.md)

[![Release Latest WeCom](https://github.com/meteor-ioi/wecom-windows-versions/actions/workflows/release.yml/badge.svg)](https://github.com/meteor-ioi/wecom-windows-versions/actions/workflows/release.yml)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/meteor-ioi/wecom-windows-versions/total)
![GitHub Downloads (all assets, latest release)](https://img.shields.io/github/downloads/meteor-ioi/wecom-windows-versions/latest/total)

本项目通过 `GitHub Actions` **每小时**自动检测腾讯企业微信官方分发服务器的更新，拉取最新安装包、校验 SHA-256 哈希并同步发布至本仓库的 [Releases](https://github.com/meteor-ioi/wecom-windows-versions/releases) 页面。

同时支持从 4.0.0 起按时间正序全量回溯归档所有历史版本。

## 相关项目 (Related Projects)

- [WeChat Windows Version Archive](https://github.com/cscnk52/wechat-windows-versions) (by @cscnk52)
- [WeChat Windows 64-bit 3.0 Archive](https://github.com/tom-snow/wechat-windows-versions) (by @tom-snow)

## 架构说明

- **`.github/workflows/release.yml`**：每小时整点定时巡检或手动触发。解析官方 `commdownload` 重定向端点嗅探最新客户端，若发现新版本则下载、计算 SHA-256 并发版（标记为 Latest）。
- **`.github/workflows/backfill.yml`**：历史版本批量回溯流。严格按**从旧到新（时间正序）**依次下载与发版，确保 Releases 列表中最老版本在底部、最新版本置顶。
- **`versions.json`**：收录并校验过的 4.0 ~ 5.0 全量历史版本及官方 CDN 下载源。

## 开源协议

本项目采用 [MIT 许可证](./LICENSE)。企业微信安装程序版权归腾讯公司所有，本项目仅供历史归档与研发兼容性测试之用。
