# 祁杉 Qishan Labs 公司官网

上海祁杉文化传播有限公司的公司与产品网站，公开域名 `qishanlabs.com`。

## 页面

五类页面各有 13 种语言，与 App 界面语言一致。简体中文无前缀，其余用 `/zh-Hant/`、`/en/`、`/ja/`、`/ko/`、`/de/`、`/fr/`、`/es/`、`/pt/`（pt-BR）、`/ru/`、`/ar/`、`/hi/`、`/id/`。

| 用途 | 简体中文 | 其他语言示例 |
| --- | --- | --- |
| 公司首页 | `/` | `/en/`、`/ja/`、`/ar/` |
| 记一下 JotIt 产品页 | `/products/jotit/` | `/en/products/jotit/` |
| 用户支持 | `/support/` | `/ja/support/` |
| 隐私政策 | `/privacy/` | `/ko/privacy/` |
| 订阅与使用条款 | `/terms/` | `/de/terms/` |

简体中文和英文页面手工维护。其余 11 种语言由 `tools/build_i18n.py` 从 `tools/i18n_strings.py` 生成；改文案后重跑生成器，不要直接改 `dist/ja/` 等生成目录。隐私政策与条款的非中英译文带有“以中文和英文为准”的声明，避免未经审校的译文单独构成约束文本。

保留原有支持和政策路径，供已提交的 App 元数据及 App 内链接继续使用。以后新增 App 时，在 `products/` 下添加独立产品页，并为该产品提供自己的支持和政策页面。

记一下 App Store 页面：`https://apps.apple.com/cn/app/id6764322744`（英文页使用不带地区的 `https://apps.apple.com/app/id6764322744`，由 Apple 按用户所在商店跳转）。工作邮箱 `weizhichao@qishanlabs.com`。

## SEO 与 GEO

- 每页有 canonical、13 种语言 + `x-default`（指向简体中文）hreflang、Open Graph 与 Twitter 大图卡。导航里有语言切换器。
- 结构化数据：产品页 `MobileApplication`，支持页 `FAQPage`，政策页 `WebPage`，首页 `WebSite`，全部带 `Organization` 与 `BreadcrumbList`。
- `robots.txt` 显式放行主流搜索引擎与 AI 答案引擎爬虫；`sitemap.xml` 含 65 个可索引地址、`lastmod` 与 `xhtml:link` 语言互链。
- `llms.txt` 面向 AI 助手汇总可引用事实，并列出不应声称的内容。产品页与支持页的「事实速查」`dl` 与 `llms.txt` 保持一致。
- IndexNow 密钥文件为站点根路径下的 `3b98754f544a3bccd9366bd26665f6da.txt`。密钥上线后执行 `python3 tools/submit_indexnow.py`，向 `api.indexnow.org` 与 Bing 提交 sitemap 中的 65 个地址。这不是访问统计，不改隐私政策。
- 搜索引擎所有权文件：`BingSiteAuth.xml`（Bing Webmaster）、`baidu_verify_codeva-wiLhuyw0HV.html`（百度搜索资源平台）。验证通过后不要删除。

版本、价格、语言数、上架地区等事实来自 App Store；更新前用 `https://itunes.apple.com/lookup?id=6764322744&country=cn` 核对，不要凭记忆改数字。

## 本地开发

静态文件位于 `dist/`。简体中文和英文页直接编辑 HTML；其余语言改 `tools/i18n_strings.py` 后运行生成器。

```sh
python3 -m http.server 4173 --directory dist   # 本地预览
python3 tools/check_site.py                    # 链接、资源、JSON-LD、hreflang、sitemap 校验
python3 tools/check_site.py --external         # 另外探测站外链接可达性
python3 tools/build_assets.py                  # 从商店截图源重建中英文截图与 OG 图
python3 tools/build_i18n.py                    # 生成 11 种语言页面、补全 hreflang/切换器、重写 sitemap
```

`tools/build_assets.py` 与 `tools/build_i18n.py` 读取同级目录 `../多语言商店截图_2026-09-11/raw/<locale>/`，需要 `cwebp` 与 Pillow。改 `style.css` 时同步升高各页 `?v=` 查询参数。`dist/assets/app-store-badge.svg` 是 Apple 官方徽章原件，不要改色或改形。

推送 GitHub `main` 分支会通过 Actions 部署至 GitHub Pages。Sites 项目身份保留在 `.openai/hosting.json`。发布后建议再跑一次 `tools/check_site.py --external` 并回读线上页面。
