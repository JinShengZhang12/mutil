# 三智能体协同学生科学推理 Web 应用

这个仓库已经改造成**可直接在 GitHub 上拉起交互式网页**（推荐使用 GitHub Codespaces）。

## 你现在可以怎么用

### 方式 A（推荐）：GitHub Codespaces 一键运行
1. 在 GitHub 仓库页面点击 **Code → Codespaces → Create codespace on main**。
2. Codespace 启动后会自动安装依赖（由 `.devcontainer/devcontainer.json` 配置）。
3. 在终端执行：
   ```bash
   cp .env.example .env
   # 编辑 .env，把 OPENAI_API_KEY 改成你的真实 key
   python main.py
   ```
4. Codespaces 会自动转发 `7860` 端口，打开后即是交互网页。

### 方式 B：本地运行
```bash
python -m venv .venv
source .venv/bin/activate  # Windows 用 .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

## API Key 变量（已保留，待你填写）
应用会按如下优先级读取：
1. `OPENAI_API_KEY`
2. `DEEPSEEK_API_KEY`
3. `HF_TOKEN`

你只需要在 `.env` 中填一个即可。

## 关键运行参数
- `PORT`（默认 `7860`）
- `GRADIO_SERVER_NAME`（默认 `0.0.0.0`）
- `OPENAI_BASE_URL`（默认 `https://api.deepseek.com`）
- `OPENAI_MODEL`（默认 `deepseek-chat`）

## GitHub CI
仓库新增了 `.github/workflows/smoke-test.yml`：
- 安装依赖
- 对核心脚本执行语法检查（`py_compile`）

这能保证你推到 GitHub 后基础运行链路不会因为语法错误中断。
