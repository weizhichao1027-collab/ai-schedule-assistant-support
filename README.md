# 祁杉 Qishan Labs 公司官网

上海祁杉文化传播有限公司的公司与产品网站。

- 公司首页：`/`
- 记一下 JotIt 产品页：`/products/jotit/`
- 记一下隐私政策：`/privacy/`
- 记一下用户支持：`/support/`
- 记一下订阅与使用条款：`/terms/`
- 工作邮箱：`weizhichao@qishanlabs.com`
- 公司域名：`qishanlabs.com`

保留原有支持和政策路径，供已提交的 App 元数据及 App 内链接继续使用。以后新增 App 时，在 `products/` 下添加独立产品页，并为该产品提供自己的支持和政策页面。

静态文件位于 `dist/`，推送 GitHub `main` 分支会通过 Actions 部署至 GitHub Pages。Sites 项目身份保留在 `.openai/hosting.json`。

本地预览：`python3 -m http.server 4173 --directory dist`
