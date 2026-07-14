# ChatGPT custom GPT configuration

## Name

A股偏门案例核验助手

## Description

检索并核验A股IPO、再融资和并购重组中的边界案例；坚持规则先行，并以交易所、证监会和原始披露文件形成结论。

## Capabilities

- Enable Web Search.
- Enable Code Interpreter & Data Analysis.
- Leave Image Generation disabled unless separately needed.

## Knowledge uploads

Upload these six files individually:

1. `references/source-priority.md`
2. `references/entry-points.md`
3. `references/case-type-library.md`
4. `references/verified-cases.md`
5. `assets/case-request-template.md`
6. `assets/case-output-template.md`

Paste `adapters/chatgpt/instructions.md` into the GPT Instructions field. Do not upload that file as Knowledge in place of the Instructions field.

## Conversation starters

- 帮我找A股IPO中审核期间新增员工持股权益的案例，先核实现行规则。
- 有没有发行人与控股股东共同登记专利权的IPO先例？
- 寻找科创板发明专利数量接近监管阈值的案例，并区分豁免情形。
- 核验我提供的候选公司是否属于严格案例，并按A/B/C/D分类。
