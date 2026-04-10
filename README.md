# 杠杆平衡与多物体力矩叠加：GitHub Pages 交互版

这个仓库原本是 Gradio + Python 版本。为了让你**在 GitHub 上直接运行交互式网页**，新增了一个纯前端版本（`web/`），可直接部署到 GitHub Pages。

## 你会得到什么

- 学生答题区（两题、每题最多两次作答）
- 自动评分 + 引导（优先调用 OpenAI 兼容接口）
- 教师日志区（浏览器本地保存）
- 可直接由 GitHub Actions 自动发布到 GitHub Pages

## 目录说明

- `web/index.html`：页面结构
- `web/style.css`：样式
- `web/app.js`：核心交互逻辑（状态机、评分、引导、日志）
- `web/config.example.js`：API 配置模板（保留 API Key 变量）
- `.github/workflows/deploy-pages.yml`：自动部署 Pages

## 快速使用（GitHub 直接运行）

1. 在仓库根目录创建 `web/config.js`，内容可参考 `web/config.example.js`。
2. 把 `API_KEY` 填成你的 key（现在可以先留空，后续再填）。
3. 打开仓库 Settings → Pages，Source 选 `GitHub Actions`。
4. 推送代码后，等待 `Deploy to GitHub Pages` 工作流完成。
5. 在 Pages 链接访问交互网页。

## API 配置模板

```js
window.APP_CONFIG = {
  BASE_URL: "https://api.deepseek.com",
  MODEL: "deepseek-chat",
  API_KEY: "", // 先留空，后续填写
};
```

> 注意：前端直连 API 会暴露密钥，不适合生产场景。课堂/演示可先用，正式环境建议加后端代理。

## 本地预览

你也可以本地打开 `web/index.html`（或用任意静态服务器）进行预览。

