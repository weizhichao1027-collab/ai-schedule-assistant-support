# 祁杉 Qishan Labs 公司官网

上海祁杉文化传播有限公司的公司与产品网站，公开域名 `qishanlabs.com`。

## 页面

| 用途 | 中文 | 英文 |
| --- | --- | --- |
| 公司首页 | `/` | `/en/` |
| 记一下 JotIt 产品页 | `/products/jotit/` | `/en/products/jotit/` |
| 用户支持 | `/support/` | `/en/support/` |
| 隐私政策 | `/privacy/` | `/en/privacy/` |
| 订阅与使用条款 | `/terms/` | `/en/terms/` |

保留原有支持和政策路径，供已提交的 App 元数据及 App 内链接继续使用。以后新增 App 时，在 `products/` 下添加独立产品页，并为该产品提供自己的支持和政策页面。

记一下 App Store 页面：`https://apps.apple.com/cn/app/id6764322744`（英文页使用不带地区的 `https://apps.apple.com/app/id6764322744`，由 Apple 按用户所在商店跳转）。工作邮箱 `weizhichao@qishanlabs.com`。

## SEO 与 GEO

- 每页有 canonical、`zh-Hans`/`en`/`x-default` 三向 hreflang、Open Graph 与 Twitter 大图卡。
- 结构化数据：产品页 `MobileApplication`（含 offers、screenshot、featureList、softwareVersion），支持页 `FAQPage` + `ContactPage`，政策页 `WebPage`，首页 `Organization` + `WebSite`，全部页面带 `BreadcrumbList`。
- `robots.txt` 显式放行主流搜索引擎与 AI 答案引擎爬虫；`sitemap.xml` 含 10 个页面、`lastmod` 与 `xhtml:link` 语言互链。
- `llms.txt` 面向 AI 助手汇总可引用事实，并列出不应声称的内容。产品页与支持页的「事实速查」`dl` 与 `llms.txt` 保持一致。

版本、价格、语言数、上架地区等事实来自 App Store；更新前用 `https://itunes.apple.com/lookup?id=6764322744&country=cn` 核对，不要凭记忆改数字。

## 本地开发

静态文件位于 `dist/`，没有构建步骤，直接编辑 HTML。

```sh
python3 -m http.server 4173 --directory dist   # 本地预览
python3 tools/check_site.py                    # 链接、资源、JSON-LD、hreflang、sitemap 校验
python3 tools/check_site.py --external         # 另外探测站外链接可达性
python3 tools/build_assets.py                  # 从商店截图源重建 dist/assets 的截图与 OG 图
```

`tools/build_assets.py` 读取同级目录 `../多语言商店截图_2026-09-11/raw/<locale>/`，需要 `cwebp` 与 Pillow。`dist/assets/app-store-badge.svg` 是 Apple 官方徽章原件，不要改色或改形。

推送 GitHub `main` 分支会通过 Actions 部署至 GitHub Pages。Sites 项目身份保留在 `.openai/hosting.json`。发布后建议再跑一次 `tools/check_site.py --external` 并回读线上页面。
