"""页面三：API、策略和版本设置。"""

from __future__ import annotations

import os

import streamlit as st

from ai.deepseek_api import DeepSeekClient, MODEL_MAP
from config.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
from document.txt_generator import generate_txt
from document.word_generator import generate_word
from models import SourceChunk
from ui import go_to, render_header


def render() -> None:
    """渲染生成参数并调用 DeepSeek。"""
    if not st.session_state.get("chunks"):
        go_to("upload")
        return
    render_header(3)
    st.subheader("AI 模型与接口")
    model_label = st.radio("AI 模型", list(MODEL_MAP), horizontal=True)
    if "兼容模式" in model_label:
        st.warning("该旧模型名将于 2026-07-24 停用，建议选择 DeepSeek-V4。")
    api_key = st.text_input(
        "API Key",
        value=st.session_state.get("api_key", DEEPSEEK_API_KEY),
        type="password",
        placeholder="sk-...",
        help="仅用于当前会话请求，不写入代码或数据库。建议通过 DEEPSEEK_API_KEY 环境变量配置。",
    )
    base_url = st.text_input("接口地址", value=st.session_state.get("base_url", DEEPSEEK_BASE_URL))
    st.session_state.api_key = api_key
    st.session_state.base_url = base_url
    if st.button("测试连接"):
        _test_connection(api_key, base_url, model_label)

    st.divider()
    st.subheader("关注策略")
    strategies = st.session_state.strategies
    selected_strategy = st.radio("请选择本次研究聚焦的策略", strategies, label_visibility="collapsed")

    st.divider()
    st.subheader("生成文件版本")
    output_version = st.radio(
        "输出版本",
        ["简版介绍材料｜200-300字｜TXT", "详细研究材料｜2页以内｜Word", "同时生成简版和详细版"],
        label_visibility="collapsed",
    )
    st.caption("完整尽调报告：后续扩展")
    back, generate = st.columns([1, 2])
    with back:
        if st.button("返回审核", use_container_width=True):
            go_to("analysis")
    with generate:
        if st.button("开始生成", type="primary", use_container_width=True):
            _generate(api_key, base_url, model_label, selected_strategy, output_version)


def _test_connection(api_key: str, base_url: str, model_label: str) -> None:
    """测试当前 DeepSeek 配置。"""
    try:
        client = DeepSeekClient(api_key, base_url, model_label)
        with st.spinner("正在测试连接…"):
            success, message = client.test_connection()
        (st.success if success else st.error)(message)
    except ValueError as exc:
        st.error(str(exc))


def _generate(api_key: str, base_url: str, model_label: str, strategy: str, version: str) -> None:
    """调用模型，并按用户选择生成 TXT 或 DOCX。"""
    try:
        chunks = [SourceChunk.from_dict(item) for item in st.session_state.chunks]
        company = st.session_state.company["name"]
        client = DeepSeekClient(api_key, base_url, model_label)
        with st.spinner("DeepSeek 正在整理研究材料，请稍候…"):
            research = client.generate(company, strategy, chunks)
            generated: dict[str, object] = {"company": company, "strategy": strategy}
            if version.startswith("简版") or version.startswith("同时"):
                txt_data, txt_path = generate_txt(company, strategy, research.brief)
                generated.update({"brief": research.brief, "txt_data": txt_data, "txt_name": txt_path.name})
            if version.startswith("详细") or version.startswith("同时"):
                docx_data, docx_path = generate_word(company, strategy, research.detail)
                generated.update({"detail": research.detail, "docx_data": docx_data, "docx_name": docx_path.name})
            st.session_state.generated = generated
        go_to("export")
    except Exception as exc:
        st.error(f"生成失败：{exc}")
        st.info("上传和识别结果已保留。请检查 API Key、接口地址、网络或账户余额后重试。")
