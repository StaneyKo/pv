"""页面四：结果预览与下载。"""

from __future__ import annotations

import streamlit as st

from ui import go_to, render_header


def render() -> None:
    """展示已生成材料，并提供下载或重新生成入口。"""
    if not st.session_state.get("generated"):
        go_to("generate")
        return
    render_header(4)
    generated = st.session_state.generated
    st.success(f"{generated['company']}｜{generated['strategy']} 材料已生成")

    st.subheader("简版介绍材料")
    if generated.get("brief"):
        st.text_area("简版正文", generated["brief"], height=220, label_visibility="collapsed")
        st.caption("可在文本框内全选复制，或下载 TXT。")
        st.download_button(
            "下载 TXT",
            data=generated["txt_data"],
            file_name=generated["txt_name"],
            mime="text/plain; charset=utf-8",
            use_container_width=True,
        )
    else:
        st.info("本次未选择简版材料。返回生成设置可补充生成。")

    st.divider()
    st.subheader("详细研究材料")
    if generated.get("detail"):
        with st.expander("预览详细正文", expanded=True):
            st.markdown(generated["detail"])
        st.download_button(
            "下载 Word",
            data=generated["docx_data"],
            file_name=generated["docx_name"],
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
    else:
        st.info("本次未选择详细研究材料。返回生成设置可补充生成。")

    left, right = st.columns(2)
    with left:
        if st.button("重新生成", use_container_width=True):
            go_to("generate")
    with right:
        if st.button("处理新材料", type="primary", use_container_width=True):
            for key in ("chunks", "company", "strategies", "modules", "generated", "uploaded_names"):
                st.session_state.pop(key, None)
            go_to("upload")

