# A-Share Corner Case Finder

面向投行、PE、证券法律及资本市场研究人员的 A 股边界案例检索 Skill。它把“先核实监管规则、再定义口径、广泛发现候选、回到一手文件核验、分层形成结论”的研究流程固化为可复用的 ChatGPT/Codex 工作流。

> 本 Skill 是研究辅助工具，不替代律师法律意见、保荐机构内核意见或与监管机构的正式沟通。

## Skill 解决什么问题

常规数据库适合查标准化字段，但以下问题往往需要拆解口径、跨文件检索和人工判断：

- 某种非标准安排是否存在 A 股先例；
- 某个边界事项监管是否曾接受、问询或要求整改；
- 按板块、时点、主体身份或数值阈值筛选案例；
- 判断二手文章列举的案例能否作为项目依据；
- 区分严格案例、近似案例、反例和未核实线索。

## 适用场景

- A 股 IPO、再融资、并购重组案例研究；
- 科创属性指标、在审期间股权激励、三类股东、突击入股；
- 对赌协议及特殊股东权利清理；
- 发行人与控股股东或实际控制人共有产权；
- 同业竞争、客户供应商重叠、上市前分红、会计差错更正；
- 分拆上市、红筹架构或 VIE 拆除等边界问题。

典型触发问题包括“找案例”“有没有先例”“审核口径是什么”“是否符合发行条件”和“有没有类似 corner case”。

不适用于实时行情、常规财务数据查询、个股投资建议、纯文字润色，或只需摘要用户已提供文件而不需要检索先例的任务。

## 核心工作流

新手默认使用四步快速模式：复述问题并区分“必须/最好” → 找3—5个候选 → 深读最可能命中的1—2个 → 输出结论、案例、排除理由和来源。只有完整底稿、候选很多或口径变化时，才展开下列专业流程：

1. **定位现行监管规则**：核对规则名称、条款、版本、生效状态，并判断规则性质。
2. **定义检索口径**：明确严格口径、宽口径、板块、时间范围、项目状态、阈值和排除项。
   对“必须/最好/可参考/含义未明”分别标注hard、preferred、fallback和unresolved；只有真正影响严格结论且无法并行覆盖的歧义才阻塞追问。
3. **建立概念树**：形成对象词、事项词、时点词、同义词和反向排除词。
4. **高召回获取候选**：优先扫描标准化披露字段，并用多轮检索和知名案例反查覆盖度。
5. **锁定一手文件**：调取交易所、证监会、巨潮等原始披露，核对文件版本和问询轮次。
6. **读取关键条款**：记录文件名、披露日期、章节和页码，区分“文件已定位”和“条款原文已读取”。
7. **必要条件测试与动态分层**：按当前问题口径逐项测试，给出 A/B/C/D 匹配等级和独立的 E1—E4 证据状态；条件变化后重新评级并说明升降级原因。
8. **输出研究 Memo**：结论先行，附监管依据、严格案例、近似案例、案例卡片和置信度。

## 可执行能力

Skill 内置了无第三方依赖的 `scripts/case_pipeline.py`，将重复且容易漂移的环节程序化：

- `fetch`：网络超时重试、备用官方 URL、PDF 载荷校验；
- `inspect`：检查 PDF 文字层，识别需要 OCR/页面渲染的情形；
- `classify`：按 hard/preferred/fallback 和证据状态生成 A/B/C/D、E1—E4；
- 日期门禁：拒绝未来检索截止日和晚于截止日的事件；假设场景必须显式标记；
- `selftest`：一条命令验证安装包的程序能力。

```bash
python3 scripts/case_pipeline.py selftest
python3 scripts/case_pipeline.py schema > /tmp/cases.json
python3 scripts/case_pipeline.py classify /tmp/cases.json
```

`selftest`只需在安装、升级或发布前运行；普通检索直接使用快速模式。

脚本不会替代对主体性质、法律关系和监管规则的专业判断。

## A/B/C/D 动态匹配等级

| 等级 | 定义 | 使用方式 |
|---|---|---|
| **A** | 满足当前严格口径的全部硬性条件 | 严格命中 |
| **B** | 核心结构接近，但缺少一项可放宽条件 | 近似参考 |
| **C** | 违反硬性必要条件、协议方向相反或逻辑结构不同 | 明确排除并说明理由 |
| **D** | 现有信息不足，暂时无法判断匹配度 | 待核验线索 |

A/B/C/D不是公司的永久标签，而是“案例 × 当前问题口径”的动态结果。同一案例在宽口径下可以是A，增加“无实际控制人”后可能降为C。

证据完成度另行标记：E1为已读取一手条款原文，E2为仅定位一手文件，E3为仅有二手材料，E4为无可用证据。口径版本使用S1、S2、S3标记。只有 **A-E1** 可以进入严格研究结论。

## 安装

### ChatGPT

1. 下载 [`dist/a-share-corner-case-finder.zip`](dist/a-share-corner-case-finder.zip)。
2. 在支持 Skills/Plugins 的 ChatGPT 客户端或工作区中打开 Skill 安装入口。
3. 上传 ZIP 并完成安装；可用下方示例测试是否触发。

Skills/Plugins 的可见性可能受客户端版本、套餐和工作区管理员策略影响。如果当前 ChatGPT 界面没有 Skill 安装入口，可在 Codex 中安装使用。

### Codex

方式一：通过 Codex 的 Skill 安装入口选择本仓库或上传 `dist/a-share-corner-case-finder.zip`。

方式二：手动安装到个人 Skills 目录：

```bash
mkdir -p ~/.codex/skills
unzip a-share-corner-case-finder.zip -d ~/.codex/skills
```

安装后新建任务，并显式调用 `$a-share-corner-case-finder`；也可以使用包含触发词的自然语言问题。

## 使用示例

### 先确认规则和口径

```text
使用 $a-share-corner-case-finder，帮我找注册制以来 IPO 审核期间新增员工持股权益的案例。
先核实现行监管规则，再按口径单确认严格口径和排除项；已上市项目为主，终止项目单列。
```

### 查找共有产权先例

```text
帮我查发行人与控股股东共同登记专利权的 A 股 IPO 先例。
请排除单纯授权使用、申报前已完成整体受让，以及共有方仅为高校但并非控股股东的情形。
```

### 补齐一手核验

```text
把候选案例按当前口径逐项判断并给出 A/B/C/D 匹配等级，同时单列 E1—E4 证据状态。
如果只能定位到一手文件但没有读到原文，匹配度可以暂定，但证据状态只能标 E2，不得进入严格结论或虚构页码。
```

## Evals 与面试 Demo

仓库中的 [`evals/`](evals/) 提供公开测试集，用于分别验证 Skill 触发、口径理解、一手证据核验、案例分层和风险边界。微电生理作为首个 gold case，覆盖“无实际控制人 + 外部投资人与员工持股平台直接一致行动 + 最终成功上市”的完整判断链路。

运行测试集格式检查：

```bash
python3 evals/validate_evals.py
python3 evals/test_case_pipeline.py
```

ChatGPT通用检索、Codex不加载Skill与Codex加载Skill的三组量化方法见 [`evals/comparison-protocol.md`](evals/comparison-protocol.md)。现有微电生理对话的回溯分析见 [`evals/results/retrospective-microport.md`](evals/results/retrospective-microport.md)；单案例只用于形成假设，不作为正式效果数据。

募投实施主体题的两份回答对比、严格案例误分原因和修复要求见 [`evals/results/comparison-ipo-implementation-subjects.md`](evals/results/comparison-ipo-implementation-subjects.md)。

同为GPT-5.6-sol时基于今天任务链形成的纵向测试见 [`evals/pilot-2026-08-13.md`](evals/pilot-2026-08-13.md)。它用于开发回归和面试Demo；正式效果仍需未公开holdout题。

面向 AI Native 金融产品经理岗位的项目讲述、Demo 脚本、简历表述和高频追问见 [`docs/interview-prep.md`](docs/interview-prep.md)。其中效率指标采用“人工 / 通用模型 / Skill”三组对照；在完成盲测前，不把流程估算表述为已经实现的用户效果。

## 仓库结构

```text
A-share-case-finder/
├── README.md
├── docs/
│   └── interview-prep.md
├── evals/
│   ├── README.md
│   ├── trigger-cases.jsonl
│   ├── research-cases.jsonl
│   ├── rubric.md
│   ├── comparison-protocol.md
│   ├── pilot-2026-08-13.md
│   ├── interview-scorecard.md
│   ├── validate_evals.py
│   ├── test_case_pipeline.py
│   ├── results/
│   │   ├── comparison-cicc-semiconductor.md
│   │   ├── comparison-ipo-implementation-subjects.md
│   │   └── retrospective-microport.md
│   └── gold/
│       ├── cicc-semiconductor-latest.md
│       ├── clarification-policy.md
│       ├── ipo-fundraising-implementation-subjects.md
│       ├── microport-ep.md
│       └── scope-evolution.md
├── src/
│   └── a-share-corner-case-finder/
│       ├── SKILL.md
│       ├── agents/
│       │   └── openai.yaml
│       ├── scripts/
│       │   └── case_pipeline.py
│       └── references/
│           ├── case-output-template.md
│           ├── case-request-template.md
│           ├── clarification-policy.md
│           ├── case-type-library.md
│           ├── entry-points.md
│           ├── quick-example.md
│           ├── source-priority.yaml
│           ├── troubleshooting.md
│           └── verified-cases.md
└── dist/
    └── a-share-corner-case-finder.zip
```

- `src/`：完整、可维护的 Skill 源文件；
- `dist/`：可供其他账号直接安装的发布包；
- `references/verified-cases.md`：空白案例库模板，不包含任何私有项目或研究案例。

## 数据与使用边界

- 二手资料只能用于发现线索，不能单独支撑案例成立；
- 现行规则、项目状态和最新披露必须联网复核；
- 终止或撤回项目不得自动归因于被检索事项；
- 公开发布版本的 `verified-cases.md` 始终保持为空白模板；
- 对外引用前，应再次核对文件版本、披露日期、页码和上下文。
