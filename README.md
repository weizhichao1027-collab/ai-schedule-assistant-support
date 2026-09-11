# 记一下 JotIt 官方网站

记一下（JotIt）的官方隐私政策与用户支持网站。

- 隐私政策：`/privacy/`
- 用户支持：`/support/`
- 订阅与使用条款：`/terms/`
- 静态站点文件：`dist/`

站点通过 GitHub Actions 自动部署到 GitHub Pages。推送到 `main` 分支后会触发发布。

本地预览：

```bash
python3 -m http.server 4173 --directory dist
```
