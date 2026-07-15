"""核心解析、识别、数据库和文档导出测试。"""

from __future__ import annotations

import sqlite3
import zipfile
from pathlib import Path

import pytest

from ai.company_extract import extract_company
from ai.module_extract import build_modules
from ai.strategy_extract import extract_strategies
from database.database import init_database, save_modules
from document.txt_generator import generate_txt
from document.word_generator import generate_word
from file_parser import parse_file
from file_parser.zip_parser import decode_zip_member_name
from models import SourceChunk


def test_txt_parse_and_identification(tmp_path: Path) -> None:
    """验证文本解析及公司、策略自动识别。"""
    path = tmp_path / "涵德投资路演.txt"
    path.write_text("涵德投资专注量化投资。中证500指数增强采用多因子选股与风险控制。", encoding="utf-8")
    chunks = parse_file(path)
    company = extract_company(chunks)
    assert "涵德投资" in company.name
    assert "中证500指数增强" in extract_strategies(chunks)


def test_legal_company_name_and_confidence_are_preserved() -> None:
    """验证法定全称不被截断，且大量通用投资词不会稀释可信度。"""
    chunks = [
        SourceChunk("*资料来源：北京涵德投资管理有限公司\n公司采用量化投资与组合投资方法。", "涵德策略.pdf", "第 5 页", "PDF"),
        SourceChunk("北京涵德投资管理有限公司投研团队介绍。证券投资、基金投资与风险管理。", "涵德介绍.docx", "段落 2", "Word"),
    ]
    result = extract_company(chunks)
    assert result.name == "北京涵德投资管理有限公司"
    assert result.confidence >= 90


def test_modules_keep_sources() -> None:
    """验证模块整理保留文件名、页码和原文。"""
    chunks = [SourceChunk("策略采用多因子选股，并设置行业偏离约束。", "路演.pptx", "第 15 页", "PPT")]
    modules = build_modules(chunks)
    strategy_module = next(item for item in modules if item.title == "策略逻辑")
    assert strategy_module.sources[0].source_page == "第 15 页"
    assert "多因子" in strategy_module.sources[0].text


def test_zip_path_traversal_is_blocked(tmp_path: Path) -> None:
    """验证 ZIP 路径穿越攻击被拒绝。"""
    path = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("../escape.txt", "unsafe")
    with pytest.raises(ValueError, match="不安全路径"):
        parse_file(path)


def test_gbk_zip_filename_is_repaired() -> None:
    """验证 Windows ZIP 中的 GBK 中文路径可自动恢复。"""
    expected = "【20260618】涵德/【股票版】涵德量化策略全景解析20260603.pdf"
    mojibake = expected.encode("gbk").decode("cp437")
    assert decode_zip_member_name(mojibake) == expected


def test_database_and_exports(tmp_path: Path) -> None:
    """验证 SQLite 保存及 TXT、DOCX 生成。"""
    db_path = tmp_path / "test.db"
    init_database(db_path)
    modules = build_modules([SourceChunk("公司采用风险控制流程。", "介绍.docx", "段落 2", "Word")])
    count = save_modules("测试投资", ["市场中性"], modules, db_path)
    with sqlite3.connect(db_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM company_info").fetchone()[0] == count
    txt_data, txt_path = generate_txt("测试投资", "市场中性", "公司介绍\n资料未披露", tmp_path)
    docx_data, docx_path = generate_word("测试投资", "市场中性", "## 一、公司基本情况\n资料未披露", tmp_path)
    assert txt_data.startswith(b"\xef\xbb\xbf") and txt_path.exists()
    assert docx_data.startswith(b"PK") and docx_path.exists()
