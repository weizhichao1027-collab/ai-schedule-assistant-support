# Design QA — 官网左上角品牌图标

- Source visual truth: `/var/folders/n1/klg21cln6qq4gd8fj10ww_km0000gn/T/codex-clipboard-405cea3a-0362-4c04-826c-0a8421fd442a.png`
- Implementation: `http://127.0.0.1:4173/`
- Implementation screenshot: Codex 内置浏览器的本轮内联截图（该浏览器未提供本地文件路径）
- Viewport/state: 首页，735 × 803 CSS px，浅色主题，无交互弹层
- Source pixels: 1464 × 1464 px
- Implementation pixels: 735 × 803 px
- Density normalization: 原图按 2× 截图理解为 732 × 732 CSS px；与 735 px 宽的实现截图按宽度对齐，对比顶部与首屏内容。

## Full-view comparison evidence

原图和调整后首页已在同一次浏览器 QA 输入中并置展示。首屏结构、标题换行、卡片比例、颜色和文案保持一致；左上角占位色块已替换为正式莲花 App 图标。

## Focused region comparison evidence

聚焦区域为页头左上角的图标与品牌名称。正式图标以 42 × 42 CSS px 显示，保持正方形比例，无拉伸、无裁切、无透明边缘，与文字基线对齐，间距为 12 px。

## Required fidelity surfaces

- Fonts and typography: 保持现有系统字体、字重、行高和换行；无新的可操作差异。
- Spacing and layout rhythm: 图标及文字间距与参考图一致；更大的页头和首屏节奏未改变。
- Colors and visual tokens: 保持原页面品牌紫、背景、边框和阴影体系。
- Image quality and asset fidelity: 使用 iOS 项目的 1024 px 正式 App Icon 生成 192 px 网页资产，清晰且无伪造图形。
- Copy/content: 未修改用户可见文案。

## Comparison history

1. Earlier finding — P2: 左上角使用紫色渐变占位块，与 App 的莲花品牌标识不一致。
2. Fix: 使用项目内正式 App Icon，生成网页尺寸图标与 favicon，同步更新首页、隐私政策页和用户支持页。
3. Post-fix evidence: 首页与用户支持页已在内置浏览器重新捕获；正式图标清晰显示，三个页面的品牌标记一致，导航链接正常。

## Findings

无可操作的 P0/P1/P2 差异。

## Interaction checks

- 首页 → 隐私政策：通过
- 首页 → 用户支持：通过
- 子页 → 首页品牌链接：通过

## Follow-up polish

无必要的 P3 项。

final result: passed

## 2026-09-09 精修图标同步

- 三个页面的页头、favicon 和 apple-touch-icon 已统一使用精修版紫色五瓣花图标。
- 192 px 和 48 px 资源均由 App 当前使用的 1024 px 图标缩放生成。
- 所有 9 处图标引用已核对文件存在，并添加版本参数刷新浏览器缓存。
- 本轮验证为资源尺寸、来源和引用检查；未重复进行页面截图审计。
