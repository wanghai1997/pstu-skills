# Superpowers：给 Claude 装上"超能力"的故事

## 这是什么？

想象一下，你和 Claude 就像是一支"双人探险队"——你是队长，Claude 是你的得力助手。但问题是，如果每次出发探险前，你都要手把手教助手怎么做，是不是很累？

**Superpowers 就是 Claude 的"武功秘籍库"。** 它不是单一的功夫，而是一整套完整的"武学体系"——从接任务、做计划、写代码、测bug，到最后的验收交付，每个环节都有标准套路。

> 类比：就像麦当劳的标准化操作手册（SOP），不管你走进哪家店，汉堡的味道都差不多。Superpowers 让 Claude 每次处理任务时，都遵循一套经过验证的最佳实践。

---

## 技术架构：这套"武学体系"是怎么组织的？

### 整体结构

```
superpowers/                    # 武学总纲
├── using-superpowers/          # 第一式：如何使用武学
│   └── SKILL.md               # "凡遇到任务，必先查秘籍"
├── brainstorming/              # 第二式：需求梳理拳
├── writing-plans/              # 第三式：计划制定掌
├── executing-plans/            # 第四式：执行腿法
├── test-driven-development/    # 第五式：测试驱动心法
├── systematic-debugging/       # 第六式：系统调试剑
├── subagent-driven-development/# 第七式：分身术
├── using-git-worktrees/        # 第八式：平行空间
├── requesting-code-review/     # 第九式：自我审查眼
└── ... 更多招式
```

### 核心设计思想

**1. 触发机制：自动感应**

每个 SKILL.md 文件开头都有一个"触发器"：

```yaml
---
name: brainstorming
description: "You MUST use this before any creative work..."
---
```

这就像武功的"起手式识别"——Claude 一看到你要"创建功能"，自动就会摆出"需求梳理拳"的架势。

**2. 执行机制：严格的流程控制**

`using-superpowers` 这个核心 skill 规定了一条铁律：

> "只要有 1% 的可能性某个 skill 适用，你就**绝对必须**调用它。"

这不是建议，是强制要求。Claude 必须先用 `Skill` 工具检查是否有适用的 skill，然后才能回应你。

**3. 分层设计：什么时候用什么武功**

| 层级 | Skills | 使用时机 |
|------|--------|----------|
| **流程层** | brainstorming, debugging | 先决定"怎么做" |
| **执行层** | frontend-design, mcp-builder | 再决定"具体做什么" |

> 类比：就像看病，先挂号分诊（流程层），再找专科医生（执行层）。

---

## 代码各部分怎么串联？

### 工作流程：一次完整的"探险任务"

让我们用**"开发一个新功能"**来演示这套武学怎么用：

```
【第一阶段：接任务】
你："我想做一个 todo 应用"
     ↓
Claude 检测：这是 creative work → 触发 brainstorming skill
     ↓
【第二阶段：需求梳理拳】
Claude："等等，让我先理解清楚..."
   - 查看现有项目状态（git log, 文件结构）
   - 一个问题一个问题地问（不是一次性问一堆）
   - 给出 2-3 种方案，推荐最佳方案并解释原因
     ↓
【第三阶段：设计定稿】
Claude："好的，方案是这样的..."
   - 把设计拆成小块（每块 200-300 字）
   - 每块都问你"这样对吗？"
   - 确认后写入 docs/plans/2026-01-31-todo-design.md
     ↓
【第四阶段：创建平行空间】
Claude："现在开始实施，让我先搭个干净的环境..."
   - 使用 using-git-worktrees skill
   - 新建分支，隔离开发环境
   - 运行项目初始化脚本
   - 验证测试基线是否通过
     ↓
【第五阶段：制定作战计划】
Claude："让我把大任务拆成小任务..."
   - 使用 writing-plans skill
   - 每个任务 2-5 分钟能完成
   - 每个任务包含：文件路径、完整代码、验证步骤
     ↓
【第六阶段：按计划执行 + 测试驱动】
Claude："开始执行任务..."
   - 使用 executing-plans 或 subagent-driven-development
   - 每个任务派一个"小弟"（子代理）去完成
   - 同时触发 test-driven-development skill：
     * 先写测试（RED）
     * 运行测试，确认失败
     * 写最少代码让测试通过（GREEN）
     * 重构优化（REFACTOR）
     * 删除测试前写的任何代码（严格！）
     ↓
【第七阶段：质量审查】
Claude："让我检查一下做得怎么样..."
   - 使用 requesting-code-review skill
   - 对照计划检查：是否符合 spec？
   - 代码质量检查：是否有问题？严重问题必须修复
     ↓
【第八阶段：收尾】
Claude："任务完成了，现在决定..."
   - 使用 finishing-a-development-branch
   - 验证所有测试通过
   - 给你选项：合并/提PR/保留/丢弃
   - 清理 worktree 环境
```

### 数据流向

```
[你的需求]
    ↓
[brainstorming] → docs/plans/*-design.md
    ↓
[using-git-worktrees] → git worktree add...
    ↓
[writing-plans] → docs/plans/*-plan.md
    ↓
[executing-plans/subagent-driven-development]
    ↓ (循环每个任务)
    ├→ [test-driven-development] → 代码 + 测试
    ├→ [systematic-debugging] → 如有bug
    └→ [requesting-code-review] → 质量检查
    ↓
[finishing-a-development-branch] → git merge/PR/cleanup
```

---

## 为什么选这套方案？

### 1. 解决"直接写代码"的陷阱

**没有 Superpowers 的时候：**
```
你："做个 todo 应用"
Claude："好的！"（直接开始写代码）
     ↓
3小时后...
     ↓
Claude："写完了！"
你："等等，我要的是本地存储，不是云端..."
     ↓
（推倒重来）
```

**有了 Superpowers：**
```
你："做个 todo 应用"
Claude："等等，让我先理解需求..."（brainstorming）
     ↓
确认：本地存储？支持标签？截止日期提醒？
     ↓
方案确认后再动手
     ↓
（一次做对）
```

### 2. 解决"大任务恐惧症"

人（和AI）面对大任务都会懵。Superpowers 把任务拆成 2-5 分钟的小块，就像吃大象——一口一口吃。

### 3. 强制测试，防止"看起来对"

TDD skill 的铁律：**先写测试，再写代码**。这防止了"看起来能跑，实际有坑"的情况。

### 4. 子代理分工，避免"注意力疲劳"

Claude 处理长对话时会有"注意力疲劳"。subagent-driven-development 让"新鲜的小弟"处理每个小任务，保持高质量输出。

---

## 我们遇到的错误及修复

### 问题 1：VSCode 插件不支持 `/plugin` 命令

**现象：**
官方安装文档说用 `/plugin install superpowers`，但在 VSCode 插件里报错"未知命令"。

**原因：**
`/plugin` 是 Claude Code CLI 工具（命令行版）的功能，VSCode 插件版本不支持。

**修复：**
手动安装：
```bash
# 直接克隆到项目 skills 目录
cd /tmp
git clone https://github.com/obra/superpowers.git
cp -r superpowers/skills/* /path/to/your/project/skills/
```

**教训：**
技术文档要区分不同平台的限制。不要假设"Claude Code"就等于所有形态。

### 问题 2：Skill 触发机制的理解误区

**现象：**
以为安装了 skills，Claude 会自动用。但实际上需要理解触发逻辑。

**真相：**
- 不是每个 skill 都会自动触发
- 有些 skill 有明确的触发条件（如 "before any creative work"）
- 有些需要用户明确说"/skill name"或在设置里配置

**教训：**
要仔细阅读每个 skill 开头的 `description` 字段，了解它的触发条件。

### 问题 3：Superpowers 和 Anthropic 官方 skills 的混淆

**现象：**
一开始以为是 anthopics/skills 仓库里的 skill，找了半天没找到。

**真相：**
- `anthopics/skills`：官方维护的基础 skills（pdf, docx, pptx 等）
- `obra/superpowers`：社区开发的完整工作流体系

**教训：**
技能生态系统很分散，GitHub 搜索时要仔细看仓库作者。

---

## 潜在陷阱及如何避免

### 陷阱 1：过度流程化

**风险：**
小任务（如"写个斐波那契函数"）走完整流程反而浪费时间。

**避免：**
理解每个 skill 的触发条件。简单任务不会触发 brainstorming（因为它明确说"creative work"）。

### 陷阱 2：子代理的上下文隔离

**风险：**
subagent-driven-development 中，每个子代理只看到自己的小任务，可能缺乏全局观。

**避免：**
writing-plans skill 要求每个任务包含"完整上下文"，确保子代理有足够信息。

### 陷阱 3：Git Worktree 的磁盘占用

**风险：**
每个 worktree 都是一份完整代码副本，大项目会占用很多空间。

**避免：**
及时用 finishing-a-development-branch 清理不需要的 worktree。

---

## 我们学到的新技术

### 1. Git Worktree（平行空间）

**是什么：**
让你同时在多个分支工作，不用来回切换。

**用法：**
```bash
# 创建新 worktree
git worktree add -b feature-branch ../feature-worktree

# 切换到那个目录工作
cd ../feature-worktree

# 完成后清理
git worktree remove ../feature-worktree
```

**类比：**
像是有多个平行宇宙，每个宇宙里你在做不同的实验，互不干扰。

### 2. Test-Driven Development（测试驱动开发）

**RED-GREEN-REFACTOR 循环：**
```
1. RED:   先写测试，运行，看它失败（证明测试有效）
2. GREEN: 写最少代码让测试通过（不管代码多丑）
3. REFACTOR: 优化代码，保持测试通过
4. 重复
```

**反直觉的点：**
要先写测试！这强迫你先想清楚"成功是什么样"。

### 3. Skill 系统的设计模式

**优秀的设计：**
- 自描述：SKILL.md 即文档又是指令
- 可组合：小 skills 组合成大流程
- 渐进式：根据任务复杂度选择使用深度

---

## 优秀工程师的思考方式

### 1. "先理解，后动手"

Superpowers 强制执行"brainstorming 优先"。这反映了资深工程师的本能：**花 60% 时间想清楚，40% 时间实现**。

### 2. "证明它坏了，再证明它好了"

TDD 的核心逻辑：先写测试证明当前没这个功能（RED），再实现功能让测试通过（GREEN）。这比"写完后手动测试"更可靠。

### 3. "小问题比大任务更容易对"

把任务拆到 2-5 分钟级别，每个小决策都更容易做对。大项目就是这样一点点啃下来的。

### 4. "代码是负债，不是资产"

TDD skill 里说："删除测试前写的任何代码"。这反映了**YAGNI**原则（You Aren't Gonna Need It）——只写必要的代码，多余的就是技术债务。

---

## 最佳实践总结

| 场景 | 使用 Skill | 关键原则 |
|------|-----------|----------|
| 开始新项目/功能 | brainstorming | 一问一答，确认理解 |
| 设计确认后 | using-git-worktrees | 隔离环境，干净起点 |
| 准备开发 | writing-plans | 任务要小，2-5分钟 |
| 写代码时 | test-driven-development | 先测试，后代码 |
| 遇到 bug | systematic-debugging | 系统化，不猜 |
| 任务很多 | subagent-driven-development | 派小弟，分工做 |
| 完成开发 | requesting-code-review | 对照计划检查 |
| 收尾 | finishing-a-development-branch | 清理环境 |

---

## 一句话总结

> Superpowers 不是让 Claude 变"聪明"，而是让 Claude 变"靠谱"——用可重复、可验证的流程，确保每次交付的质量稳定。

就像米其林餐厅的菜品质量稳定，不是因为厨师某天灵感爆发，而是因为每一步都有 SOP。Superpowers 就是 Claude 的米其林 SOP。
