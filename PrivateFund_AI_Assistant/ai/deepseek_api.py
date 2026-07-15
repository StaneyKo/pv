"""DeepSeek OpenAI 兼容接口客户端。"""

from __future__ import annotations

import re
from dataclasses import dataclass

import httpx

from ai.prompt_template import build_research_prompt
from config.config import DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, MAX_CONTEXT_CHARS
from models import SourceChunk


MODEL_MAP: dict[str, tuple[str, str | None]] = {
    "DeepSeek-V4-Flash（推荐）": ("deepseek-v4-flash", "disabled"),
    "DeepSeek-V4-Pro（深度研究）": ("deepseek-v4-pro", "enabled"),
    "DeepSeek-V3（兼容模式）": ("deepseek-chat", None),
    "DeepSeek-R1（兼容模式）": ("deepseek-reasoner", None),
}


@dataclass
class GeneratedResearch:
    """LLM 生成的两类研究材料。"""

    brief: str
    detail: str
    raw: str


class DeepSeekClient:
    """封装连接测试和材料生成。"""

    def __init__(self, api_key: str, base_url: str = DEEPSEEK_BASE_URL, model: str = DEEPSEEK_MODEL) -> None:
        """保存连接参数，禁止空密钥。"""
        if not api_key.strip():
            raise ValueError("请先填写 DeepSeek API Key")
        self.api_key = api_key.strip()
        self.base_url = base_url.rstrip("/")
        mapped = MODEL_MAP.get(model)
        self.model = mapped[0] if mapped else model
        self.thinking = mapped[1] if mapped else None

    def _headers(self) -> dict[str, str]:
        """构造鉴权请求头。"""
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def test_connection(self, timeout: float = 20.0) -> tuple[bool, str]:
        """使用最小请求测试接口连接。"""
        try:
            payload = {"model": self.model, "messages": [{"role": "user", "content": "请仅回复：连接成功"}], "max_tokens": 16}
            if self.thinking:
                payload["thinking"] = {"type": self.thinking}
            response = httpx.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
                timeout=timeout,
            )
            response.raise_for_status()
            return True, response.json()["choices"][0]["message"]["content"].strip()
        except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
            return False, f"连接失败：{exc}"

    def generate(self, company: str, strategy: str, chunks: list[SourceChunk], timeout: float = 180.0) -> GeneratedResearch:
        """提交可追溯材料并拆分简版、详版输出。"""
        materials = format_materials(chunks, MAX_CONTEXT_CHARS)
        prompt = build_research_prompt(company, strategy, materials)
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 5000,
        }
        if self.thinking:
            payload["thinking"] = {"type": self.thinking}
        if self.thinking != "enabled":
            payload["temperature"] = 0.1
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers=self._headers(),
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()
        raw = response.json()["choices"][0]["message"]["content"].strip()
        brief = _extract_tag(raw, "BRIEF")
        detail = _extract_tag(raw, "DETAIL")
        if not brief or not detail:
            raise ValueError("模型输出格式不完整，请重新生成")
        return GeneratedResearch(brief, detail, raw)


def format_materials(chunks: list[SourceChunk], max_chars: int = MAX_CONTEXT_CHARS) -> str:
    """将原始片段格式化为带来源的上下文，并限制总长度。"""
    parts: list[str] = []
    used = 0
    for chunk in chunks:
        header = f"\n[来源：{chunk.source_file}；位置：{chunk.source_page or '未标注'}]\n"
        remaining = max_chars - used - len(header)
        if remaining <= 0:
            break
        body = chunk.text[:remaining]
        parts.append(header + body)
        used += len(header) + len(body)
    return "".join(parts)


def _extract_tag(text: str, tag: str) -> str:
    """读取模型输出中的 XML 风格标签。"""
    match = re.search(rf"<{tag}>\s*(.*?)\s*</{tag}>", text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""
