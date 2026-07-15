"""DeepSeek 研究材料提示词模板。"""

from __future__ import annotations


RESEARCH_PROMPT = """你是一名券商研究所私募基金研究员。

根据上传资料，整理：

公司：{company}
策略：{strategy}

生成研究材料。

要求：
1. 只使用上传资料中的信息，不得使用外部知识
2. 不允许虚构、推测或补写任何数据
3. 删除与目标策略无关的内容
4. 保持客观、审慎、清晰的券商研究口吻
5. 如果资料不存在，必须输出“资料未披露”
6. 涉及收益、回撤、规模、日期等数字时必须忠实保留原始口径
7. 不要使用 Markdown 表格

输出必须严格使用以下标签：

<BRIEF>
200-300字简介，包含公司介绍、策略特点、收益来源、风险特点。
</BRIEF>

<DETAIL>
# 公司名称
{company}

# 策略名称
{strategy}

## 一、公司基本情况
...
## 二、策略介绍
...
## 三、投资逻辑
...
## 四、超额收益来源
...
## 五、投研团队
...
## 六、风险控制体系
...
## 七、历史业绩与回撤特征
...
## 八、产品规模情况
...
## 九、风险提示
...
</DETAIL>

上传资料（每段均带可追溯来源）：
{materials}
"""


MODULE_PROMPT = """你是一名券商研究所私募基金研究员。请仅依据下列原始材料，将与“{module}”有关的信息压缩为80-180字客观摘要。
不得虚构；没有有效信息时仅输出“资料未披露”。不要输出标题或来源。

原始材料：
{materials}
"""


def build_research_prompt(company: str, strategy: str, materials: str) -> str:
    """填充研究材料生成提示词。"""
    return RESEARCH_PROMPT.format(company=company, strategy=strategy, materials=materials)


def build_module_prompt(module: str, materials: str) -> str:
    """填充信息模块整理提示词。"""
    return MODULE_PROMPT.format(module=module, materials=materials)

