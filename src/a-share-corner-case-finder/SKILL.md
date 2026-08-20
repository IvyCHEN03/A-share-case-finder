---
name: a-share-corner-case-finder
description: 检索并核验A股IPO、再融资及并购重组的监管边界案例。用于“找案例”“有没有先例”“审核口径”“某种安排能否上市”等需要拆解条件、检索问询回复并回到一手文件的任务。不用于实时行情、常规财务数据查询、个股投资建议、纯文字润色或只摘要用户已提供的文件。结论必须以现行规则和交易所、证监会或原始披露文件为依据。
---

# A股边界案例检索

## 交付目标

输出可复核的项目组 Memo：结论、口径、监管规则、案例分层、一手出处和检索盲区。不替代律师法律意见、保荐机构内核或监管沟通。

## 三条硬规则

1. **先规则，后案例。** 先核实现行文件、条款和生效状态。
2. **一手文件才能下结论。** 二手资料只找线索；严格案例必须读到原始条款和页码/章节。
3. **只能写“暂未发现”。** 未完成足够覆盖时，不得写“没有案例”“不存在”或“监管禁止”。

## 默认快速模式

除非用户要求完整底稿、候选很多或口径反复变化，否则只做四步：

1. 用一句话复述问题，把“必须”与“最好”分开；
2. 找 3—5 个候选，只深读最可能命中的 1—2 个；
3. 用一手文件核对主体、事项、时点和结果；
4. 交付“结论｜严格案例｜近似/排除｜来源与限制”。

快速模式内部仍遵守下述规则，但默认不向新手展示 S 版本、JSON 或完整评级矩阵。只有用户要求完整 Memo、候选超过 5 个、存在阻塞歧义或口径发生变化时，切换专业模式。

## 专业模式管线

### 1. 接管任务

- 首次更新告知用户：“已启用 A股边界案例检索 Skill”。
- 判断是“继续旧任务”还是“新任务”。新任务重建 `S1`，不继承旧题硬条件。
- 将条件标为 `hard / preferred / fallback / unresolved`。“最好、优先”只影响排序。
- 只在歧义会改变严格结论且无法并行覆盖时，追问一个问题。详见 `references/clarification-policy.md`。

### 2. 定义口径

用不超过8行写明：研究问题、hard条件、preferred/fallback条件、板块和时间、项目状态、关键时点、排除项、交付形式。复杂任务使用 `references/case-request-template.md`。

涉及一致行动或表决权时，固定记录：

```text
主体A → 法律关系/表决权方向 → 主体B
签约人｜直接持股人｜分歧解决｜协议期限｜发生时点
```

### 3. 核实规则

- 核实文件名、条款、版本、生效状态。
- 判断规则属于：允许但需解释／原则允许但有例外／明确禁止。
- 将规则事实、案例事实和研究推断分开。

### 4. 发现候选

- 按“对象词 + 事项词 + 时点词”搜索，补同义词和反向排除词。
- 优先扫描招股书/问询回复的标准披露字段，再用二手资料扩充公司名。
- 结果若集中于单一来源，继续反查知名项目和匿名线索，不得停在1—2轮搜索。
- 按 `references/source-priority.yaml` 选择信源，入口见 `references/entry-points.md`。

### 5. 获取和读取一手文件

优先直接读取主机提供的PDF。遇到超时、错误响应或备用镜像时，运行：

```bash
python3 scripts/case_pipeline.py fetch \
  --url "<交易所PDF>" --url "<巨潮镜像>" \
  --output /tmp/case.pdf
python3 scripts/case_pipeline.py inspect /tmp/case.pdf
```

若文字层稀少或提取失败，渲染相关页并OCR；数字、日期和主体名必须与页面图像核对。完整降级路径见 `references/troubleshooting.md`。

严格区分：

- 已定位文件：只能标 E2；
- 已读到条款并记录页码/章节：才能标 E1。

### 6. 自动评级（复杂任务）

将条件和一手证据录入JSON，交给脚本机械分类：

```bash
python3 scripts/case_pipeline.py schema > /tmp/cases.json
python3 scripts/case_pipeline.py classify /tmp/cases.json --output /tmp/ratings.json
```

| 匹配 | 含义 |
|---|---|
| A | 全部hard条件满足 |
| B | 只缺用户已允许放宽的条件 |
| C | 已确认违反不可放宽的hard条件 |
| D | 至少一项hard条件信息不足 |

| 证据 | 含义 |
|---|---|
| E1 | 已读一手条款，有文件和页码/章节 |
| E2 | 只定位一手文件 |
| E3 | 只有二手资料或搜索摘要 |
| E4 | 无可用证据 |

只有 `A-E1` 进入严格结论。preferred只在同等级内排序。用户改变口径时新建 S 版本并全量重评候选。

### 7. 交付

按以下顺序输出：

1. 结论：是否找到 `A-E1`、检索截止日和最大限制；
2. 必要条件矩阵和分层案例；
3. 每个主张对应的文件名、披露日期、问题编号、页码和链接；
4. 监管逻辑和可直接粘贴的 Memo 段落；
5. 未覆盖范围、D类线索和人工复核项。

简短问题使用快速模式；完整报告使用 `references/case-output-template.md`。新手端到端示例见 `references/quick-example.md`。

## 必做检查

- 核对现行规则版本、项目状态和检索截止日。
- 检索截止日不得晚于实际当前日期；案例事件不得晚于检索截止日。假设场景必须显式标注，不得混入真实案例结论。
- 对前1—2名候选完成条款级核验。
- 核对时点、主体、协议方向、数字和文件版本。
- 将终止/撤回项目单列；无证据时不得归因。
- 遇到异常时查阅 `references/troubleshooting.md`，不得为补齐结论虚构页码或原文。

安装、升级或发布前运行 `python3 scripts/case_pipeline.py selftest`；普通检索任务无需重复运行。

## 资源导航

- 任务口径：`references/case-request-template.md`
- 澄清决策：`references/clarification-policy.md`
- 信源与入口：`references/source-priority.yaml`、`references/entry-points.md`
- 主题检索词：`references/case-type-library.md`
- 完整输出：`references/case-output-template.md`
- 使用示例：`references/quick-example.md`
- 故障与误区：`references/troubleshooting.md`
- 可选案例库模板：`references/verified-cases.md`（不自动写入）
