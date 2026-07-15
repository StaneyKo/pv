"""TXT 文件生成器。"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from config.config import OUTPUT_DIR


def generate_txt(company: str, strategy: str, content: str, output_dir: Path = OUTPUT_DIR) -> tuple[bytes, Path]:
    """生成 UTF-8 with BOM 的简版材料，便于 Windows 正确显示中文。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_company = _safe_filename(company)
    path = output_dir / f"{safe_company}_{_safe_filename(strategy)}_简版_{timestamp}.txt"
    full_content = f"{company}\n{strategy}\n\n{content.strip()}\n"
    data = full_content.encode("utf-8-sig")
    path.write_bytes(data)
    return data, path


def _safe_filename(value: str) -> str:
    """替换 Windows 不允许的文件名字符。"""
    return "".join("_" if char in '<>:"/\\|?*' else char for char in value).strip() or "未命名"

