"""跨模块共享的数据结构。"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class SourceChunk:
    """表示一段带来源定位的原始文本。"""

    text: str
    source_file: str
    source_page: str | None = None
    file_type: str = ""

    def to_dict(self) -> dict[str, Any]:
        """转换为可序列化字典。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SourceChunk":
        """从字典恢复对象。"""
        return cls(**data)


@dataclass
class ModuleInfo:
    """表示一个可审核的信息模块。"""

    title: str
    summary: str
    sources: list[SourceChunk]

    def to_dict(self) -> dict[str, Any]:
        """转换为可序列化字典。"""
        return {"title": self.title, "summary": self.summary, "sources": [item.to_dict() for item in self.sources]}

