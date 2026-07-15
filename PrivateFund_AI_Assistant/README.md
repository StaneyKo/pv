# 私募材料智能整理工具

面向券商研究所内部使用的 Streamlit 应用。研究员上传私募公司的 Word、PPT、Excel、PDF、TXT 或 ZIP 材料后，系统自动识别公司与策略，按来源整理十一类研究信息，并调用 DeepSeek 生成简版 TXT 和详细 Word 材料。

> 本工具不会绕过研究员审核。AI 输出仅来自上传材料，仍应逐项核对原文与数字口径。

## 主要功能

- 多文件拖拽上传，支持 `.docx`、`.pptx`、`.xlsx`、`.xlsm`、`.pdf`、`.txt`、`.zip`
- 自动保存、解析、识别公司名称和投资策略
- 十一个信息模块：公司、策略、团队、策略逻辑、收益来源、风控、业绩、产品规模、投资流程、模型框架、风险提示
- 每个模块保留 AI/规则整理内容、原始文件、页码或等效位置、原始文本
- DeepSeek-V4-Flash、V4-Pro 可切换，同时保留 V3 与 R1 兼容选项，接口地址可配置
- 输出 200–300 字 TXT、两页以内的研究风格 DOCX，或同时生成两种版本
- SQLite 保存识别信息；ZIP 包含路径穿越防护；单文件解析失败不阻断其他材料
- 兼容 Windows、macOS 与 Linux

## 项目目录

```text
PrivateFund_AI_Assistant/
├── app.py
├── pages/
│   ├── upload.py
│   ├── analysis.py
│   ├── generate.py
│   └── export.py
├── file_parser/
│   ├── word_parser.py
│   ├── ppt_parser.py
│   ├── excel_parser.py
│   ├── pdf_parser.py
│   ├── txt_parser.py
│   ├── zip_parser.py
│   └── parser_factory.py
├── ai/
│   ├── deepseek_api.py
│   ├── prompt_template.py
│   ├── company_extract.py
│   ├── strategy_extract.py
│   └── module_extract.py
├── document/
│   ├── txt_generator.py
│   └── word_generator.py
├── database/
│   └── database.py
├── config/
│   └── config.py
├── examples/
│   ├── 涵德投资_示例说明.txt
│   └── create_sample_files.py
├── tests/
│   └── test_core.py
├── uploads/
├── outputs/
├── requirements.txt
├── .env.example
└── README.md
```

## 本地运行

建议使用 Python 3.10 或更高版本。

### Windows PowerShell

```powershell
cd PrivateFund_AI_Assistant
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DEEPSEEK_API_KEY="sk-你的密钥"
streamlit run app.py
```

### macOS / Linux

```bash
cd PrivateFund_AI_Assistant
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DEEPSEEK_API_KEY="sk-你的密钥"
streamlit run app.py
```

浏览器通常会自动打开 `http://localhost:8501`。

API Key 也可在第三页临时输入。页面输入只保存在当前 Streamlit 会话，不写入 SQLite 或源码。不要把真实密钥提交到版本库。

## 配置项

配置集中在 `config/config.py`，均可用环境变量覆盖：

| 环境变量 | 默认值 | 说明 |
|---|---|---|
| `LLM_PROVIDER` | `deepseek` | 预留的模型供应商标识 |
| `DEEPSEEK_API_KEY` | 空 | DeepSeek API Key |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` | OpenAI 兼容接口根地址 |
| `DEEPSEEK_MODEL` | `deepseek-v4-flash` | 默认模型 |
| `MAX_UPLOAD_MB` | `100` | 单文件大小限制 |
| `MAX_CONTEXT_CHARS` | `100000` | 单次请求最多提交的材料字符数 |

当前默认使用 DeepSeek-V4-Flash 非思考模式，V4-Pro 使用思考模式。页面仍保留 V3（`deepseek-chat`）和 R1（`deepseek-reasoner`）兼容选项，但 DeepSeek 官方已公告这两个旧模型名将在 2026-07-24 停用；新部署应优先选择 V4。详见 [DeepSeek API 官方快速开始](https://api-docs.deepseek.com/) 与 [思考模式说明](https://api-docs.deepseek.com/zh-cn/guides/thinking_mode)。如使用兼容代理，可在页面修改接口地址。

## 使用流程

1. 上传同一家私募的多份材料，点击“保存并自动解析”。
2. 在识别页核对公司、策略及十一类信息；展开卡片查看来源和原文。
3. 填写或读取 DeepSeek API Key，测试连接，选择关注策略与输出版本。
4. 生成后预览正文，下载 TXT 或 Word；需要调整时返回重新生成。

## 示例材料

`examples/涵德投资_示例说明.txt` 可直接上传。运行以下命令还会生成 Word、PPT、Excel、PDF 和含多种文件的 ZIP 测试包：

```bash
python examples/create_sample_files.py
```

示例中的机构、策略与内容仅用于软件测试，不应作为真实研究结论。

## 测试

```bash
pytest -q
```

测试覆盖：TXT 解析、公司/策略识别、模块来源追溯、ZIP 路径安全、SQLite 入库、TXT/DOCX 导出。

## 已知边界

- 扫描版 PDF 没有文本层时无法直接解析，请先用 OCR 软件生成可搜索 PDF。
- DOCX 文件本身不存储稳定页码，界面使用“段落 N / 表格 N”定位；PPT 和 PDF 会保留真实页码，Excel 使用工作表和行号。
- `.doc`、`.ppt`、`.xls` 旧格式不在本版本支持范围，请先另存为新版 Office 格式。
- 很长的材料会按上传及解析顺序截断到 `MAX_CONTEXT_CHARS`，界面审核仍保留完整解析结果。
- DeepSeek 输出可能存在格式或内容误差，使用前必须对照原文复核。

## 扩展其他模型

当前 DeepSeek 调用被封装在 `ai/deepseek_api.py`。后续可新增同样返回 `GeneratedResearch` 的 Provider 客户端，并根据 `LLM_PROVIDER` 在生成页选择客户端，无需改动文件解析和文档导出模块。
