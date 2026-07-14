# A股偏门案例检索 Skill

面向投行和 PE 团队的 A 股 IPO、再融资及并购重组边界案例检索方法论。它把“规则先行、明确口径、高召回找候选、回到原始文件核验、分层形成结论”的研究纪律固化为可复用 Skill。

适合处理：

- “这种安排有没有 A 股先例？”
- “某种边界情形监管是否认可？”
- “按特定阈值、时点或主体身份筛选案例。”
- “核验二手文章列举的案例能否放进内部 Memo。”

## 核心原则

1. **先规则，后案例。** 先核实现行有效规则、具体条款和规则性质，再搜索案例。
2. **一手文件形成结论。** 搜索摘要、数据库标签、公众号和律所文章只能发现线索。
3. **区分定位与核验。** 找到文件不等于实际读到相关条款。
4. **不把暂未发现写成不存在。** 明确检索范围、截止日、盲区和置信度。
5. **不错误归因终止项目。** 某事项出现在终止项目中，不代表它就是终止主因。

## 核实层级

| 层级 | 含义 | 使用方式 |
|---|---|---|
| A | 严格符合，且已读取一手条款原文 | 可在核对引用后使用 |
| B | 高度接近，或文件已定位但条款未读取 | 需要补充核验 |
| C | 形似而实质不符 | 作为排除案例 |
| D | 仅有二手线索 | 仅用于继续检索 |

## 平台兼容

本仓库采用“一套核心方法论 + 平台适配层”：

| 平台 | 使用入口 | 说明 |
|---|---|---|
| Claude | 根目录 `SKILL.md` | 将完整 skill 文件夹上传或放入 Claude Skills 目录 |
| Codex | 根目录 `SKILL.md` + `agents/openai.yaml` | 支持自然语言或 `$a-share-corner-case-finder` 调用 |
| ChatGPT | `adapters/chatgpt/` | Instructions 与 Knowledge 分开配置 |

运行以下命令可以生成两个独立安装包：

```bash
bash scripts/build-packages.sh
```

输出：

```text
dist/a-share-corner-case-finder-claude.zip
dist/a-share-corner-case-finder-chatgpt.zip
```

## 在 Claude 中安装

运行打包脚本后，上传 `dist/a-share-corner-case-finder-claude.zip`；也可以直接使用包含 `SKILL.md`、`references/` 和 `assets/` 的完整仓库目录。

## 在 Codex 中安装

将本仓库克隆或下载后，把整个文件夹放入：

```text
~/.codex/skills/a-share-corner-case-finder/
```

确保目录中直接包含 `SKILL.md`。重新打开 Codex 任务后，可以自然语言触发，也可以显式调用：

```text
使用 $a-share-corner-case-finder，帮我查找发行人与控股股东共有产权的 A 股 IPO 先例。先核实现行监管规则，再确认检索口径。
```

典型触发词包括“找案例”“有没有先例”“偏门案例”“corner case”“审核口径”和“是否符合发行条件”。

## 在 ChatGPT 中使用

ChatGPT 不能直接安装 Codex Skill ZIP，但可以将同一内容配置成自定义 GPT：

1. 将 `adapters/chatgpt/instructions.md` 放入 GPT **Instructions**；
2. 按 `adapters/chatgpt/config.md` 上传六个 Knowledge 文件；
3. 开启 **Web Search** 与 **Code Interpreter & Data Analysis**；
4. 在 Instructions 中保留“一手文件、核实层级、不得虚构页码”等约束。

也可以运行打包脚本，然后按照 `dist/a-share-corner-case-finder-chatgpt.zip` 内的 `CONFIG.md` 配置。案例库在自定义 GPT 中是静态知识文件；新增案例后需要重新上传，或者通过外部数据库和 GPT Action 实现持续读写。

## Demo

完整演示见 [`demo/demo.md`](demo/demo.md)。它展示：

- 如何先拆分监管规则和权益类型；
- 如何确认严格/宽口径；
- 如何输出 A/B/C/D 分层；
- 如何在无法读取一手条款时保持 B 类；
- 如何避免将虚构 Demo 当成真实案例。

## 推荐调用方式

### 直接检索

```text
帮我找科创板上市前发明专利数量接近监管阈值的已上市案例，注册制以来，终止项目单列。
```

### 先确认口径

```text
使用 $a-share-corner-case-finder，先按口径单确认严格口径、宽口径、时间范围和排除项，再开始检索。
```

### 补齐一手核验

```text
把排名靠前的两个候选案例继续核验到 A 类；如果无法读取原始条款，保留为 B 类并说明障碍。
```

## 文件结构

```text
a-share-corner-case-finder/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── adapters/
│   └── chatgpt/
│       ├── instructions.md
│       └── config.md
├── assets/
│   ├── case-request-template.md
│   └── case-output-template.md
├── demo/
│   └── demo.md
├── scripts/
│   └── build-packages.sh
└── references/
    ├── source-priority.md
    ├── entry-points.md
    ├── case-type-library.md
    └── verified-cases.md
```

- `SKILL.md`：核心工作流、触发条件和质量控制；
- `agents/openai.yaml`：Codex 界面展示及默认调用提示；
- `adapters/chatgpt/`：ChatGPT 自定义 GPT 的 Instructions 和配置清单；
- `assets/`：检索口径单与最终 Memo 模板；
- `demo/`：端到端调用演示；
- `scripts/build-packages.sh`：生成 Claude 和 ChatGPT 独立安装包；
- `references/`：信源优先级、官方入口、案例概念树和案例库。

## 案例库

公开仓库中的 `references/verified-cases.md` 保持为空白模板。实际项目形成的案例、数据和核验进度可能属于内部研究成果，建议只在私有副本中维护，不要直接提交到公开仓库。

## 边界声明

本 Skill 是研究和检索工具，不替代律师法律意见、保荐机构内核意见或与监管机构的正式沟通。对外使用前，应再次核对现行规则、项目状态和一手文件原文。
