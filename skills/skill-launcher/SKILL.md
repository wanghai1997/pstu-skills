---
name: skill-launcher
description: 帮助用户发现、理解和使用已下载到本地的 Claude Code skills。当用户想要使用某个 skill 但不知道如何使用，或想查看有哪些可用 skills 时使用。
---

# Skill 启动器

这个 skill 解决了 "skill 已下载但无法通过 /command 调用" 的问题。它提供了一个简单的方式来管理和使用本地 skills。

## 核心问题

当前环境限制：
- ✅ Skills 已下载到 `C:\Users\fuyon\.claude\plugins\marketplaces\anthropics-skills\skills\`
- ❌ 不支持 `/plugin` 或 `/skill-name` 命令
- ❌ Skills "躺在文件夹里"无法自动调用

## 解决方案

### 方式 1：列出所有可用 Skills

```bash
# 查看所有已下载的 skills
cd C:\Users\fuyon\.claude\plugins\marketplaces\anthropics-skills\skills
ls
```

可用 skills 包括：
- **pdf** - PDF 文件处理（提取文字、合并、分割、表单填写）
- **docx** - Word 文档处理
- **xlsx** - Excel 表格处理
- **pptx** - PowerPoint 处理
- **skill-creator** - 创建新 skill 的指南
- **algorithmic-art** - 生成算法艺术作品
- **canvas-design** - Canvas 设计工具
- **webapp-testing** - Web 应用测试
- **mcp-builder** - MCP 服务器构建
- **frontend-design** - 前端设计
- **internal-comms** - 内部沟通文档
- **slack-gif-creator** - Slack GIF 创建
- **theme-factory** - 主题工厂
- **web-artifacts-builder** - Web 产物构建

### 方式 2：查看 Skill 详细说明

```bash
# 查看某个 skill 的详细文档
cat "C:\Users\fuyon\.claude\plugins\marketplaces\anthropics-skills\skills\pdf\SKILL.md"
```

### 方式 3：在对话中直接使用（推荐）

不需要特殊命令，直接在对话中说明：

> "我想使用 pdf skill，请帮我提取 PDF 的文字"

> "请用 xlsx skill 帮我分析这个 Excel 文件"

> "我想了解 algorithmic-art skill 能做什么"

### 方式 4：复制 Skill 到当前项目

将常用 skill 复制到项目目录，方便重复使用：

```bash
# 复制 pdf skill 到当前项目的 skills/ 目录
mkdir -p skills
cp -r "C:\Users\fuyon\.claude\plugins\marketplaces\anthropics-skills\skills\pdf" skills/
```

复制后，Claude 可以直接读取并使用这些 skill。

## 实用示例

### 示例 1：使用 PDF Skill

用户请求：
> "请使用 pdf skill 帮我提取 'document.pdf' 的文字"

执行步骤：
1. 读取 `skills/pdf/SKILL.md` 了解 pdf skill 的功能
2. 根据需要执行操作（提取文字、合并PDF等）
3. 提供代码示例或直接使用 skill 中的脚本

### 示例 2：使用 Excel Skill

用户请求：
> "请用 xlsx skill 分析我的销售数据"

执行步骤：
1. 读取 `skills/xlsx/SKILL.md` 了解功能
2. 帮助用户处理 Excel 文件（读取、写入、数据分析）

### 示例 3：了解可用 Skills

用户请求：
> "我有哪些可用的 skills？"

回答方式：
1. 列出所有已下载的 skills
2. 简要说明每个 skill 的功能
3. 提供使用建议

## Skill 使用流程图

```
用户请求
    ↓
识别需要的 skill
    ↓
查看本地 skills 目录
    ↓
找到对应的 skill
    ↓
读取 SKILL.md 了解功能
    ↓
根据指导执行操作
    ↓
完成任务
```

## 常见问题

**Q: 为什么我不能直接用 `/pdf` 命令？**
A: 当前环境不支持自动 skill 调用，需要手动指定。

**Q: 如何知道某个 skill 能做什么？**
A: 查看该 skill 的 `SKILL.md` 文件，开头有详细描述。

**Q: 需要每次都复制 skill 到项目吗？**
A: 不需要。可以直接指示 Claude 使用特定 skill。

**Q: 如何创建自己的 skill？**
A: 使用 skill-creator skill，或参考 `skills/skill-creator/SKILL.md`。

## 最佳实践

1. **明确表达需求**：在对话中清楚地说明你需要的 skill
2. **提供上下文**：说明要处理什么文件、期望的输出
3. **查看示例**：许多 skill 包含 examples 目录，提供使用示例
4. **复用脚本**：skill 的 scripts/ 目录下有即用脚本

## 扩展建议

如果想进一步提升使用体验，可以：
- 创建常用 skill 的快捷方式
- 编写包装脚本简化调用
- 构建 skill 索引文件
- 定期更新 skills 仓库

这个 skill-launcher 本身也是一个示例，展示了如何创建实用的 skill 来扩展 Claude 的功能。
