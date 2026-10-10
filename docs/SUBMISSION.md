# GitHub 仓库简介与报名 Issue 文案

> 用于 `hachiday/mcd-women-fitness-meals-skill` 的仓库设置与赛事报名。
> 所有文案均已通过赛事内容合规红线检查：不出现其他餐饮品牌、不以减肥为叙事、不含医疗建议。

---

## 一、仓库简介（GitHub About）

GitHub 仓库简介上限 **350 字符**。以下为推荐版本。

### 推荐版（110 字符）

```
面向力量训练/增肌期女性的麦当劳配餐 Skill。基于官方 MCP 营养数据，用「钠效率=钠÷蛋白」重排 160 条餐品：同样一份蛋白，钠可以差 6.5 倍。产出可截图分享的 HTML 配餐卡。纯 Python 零依赖。
```

**为什么这样写**：

| 要素 | 作用 |
|---|---|
| 「力量训练/增肌期女性」 | 精准圈定人群，一眼看出与泛营养项目的差异 |
| 「钠效率=钠÷蛋白」 | 亮出独特指标，这是本项目唯一的差异化资产 |
| 「160 条」 | 有具体规模，可信度高于「基于营养数据」 |
| 「6.5 倍」 | 反直觉论断，制造点击欲 |
| 「HTML 配餐卡」 | 说明产出物形态，对标头部项目的传播打法 |
| 「纯 Python 零依赖」 | 降低试用门槛，对标竞品的卖点 |

### 备选版（更短，69 字符）

```
麦当劳官方 MCP 配餐 Skill。用「钠效率」重排营养数据：同样一份蛋白，钠可以差 6.5 倍。面向力量训练人群，输出可分享的配餐卡。
```

### 英文版（如需国际化，201 字符）

```
A McDonald's MCP skill for strength-training women. Re-ranks 160 official nutrition items by sodium-per-gram-of-protein — the same protein can differ 6.5x in sodium. Outputs a shareable HTML meal card.
```

---

## 二、Topics（仓库标签）

在仓库右侧 **Topics** 中添加，有助于被搜索发现。建议 5 个（上限 20）：

```
mcd-mcp
mcdonalds
nutrition
agent-skill
workbuddy
```

> 说明：与头部项目 `mcd-event-radar` 的 topics 策略一致（它用了 `agent-skill` `event-map` `mcdonalds` `mcp` `mcp-server` `skill` `workbuddy`）。

---

## 三、Issue 标题

### 推荐

```
【参赛申请】麦练营养官 · 力量训练女性的蛋白/钠双锚点配餐 Skill
```

### 备选

```
【参赛申请】麦练营养官 mcd-lift-nutrition-coach —— 同样一份蛋白，钠可以差 6.5 倍
```

> 标题中的中文冒号 `：` 后需有一个空格，这是官方模板的原始写法，请勿改动。

---

## 四、Issue 正文

> ⚠️ **官方校验规则（务必遵守）**：
> 1. **【项目简介】的标题与正文之间不要使用换行符** —— 即 `项目简介：xxx` 后面直接接内容
> 2. **项目地址链接不要用 Markdown 格式** —— 直接粘贴纯 URL，不要用 `[]()` 或反引号

### 可直接复制粘贴的完整版

```
【参赛申请】
项目名称：麦练营养官 · mcd-lift-nutrition-coach
项目地址：https://github.com/hachiday/mcd-women-fitness-meals-skill
项目简介：同样吃一份蛋白，麦当劳菜单里钠可以差 6.5 倍。本项目面向力量训练/增肌期女性，把官方 MCP 的 160 条营养数据重排为「钠效率=钠(mg)÷蛋白(g)」这一决策指标，回答训练人群真正关心的问题——蛋白要吃够，代价是多少钠。实测同为约15克蛋白的两款餐品，钠效率从 10.3 到 66.6；引擎给出的方案可在同等蛋白下少摄入约 474mg 钠。产出可直接截图分享的单文件 HTML 配餐卡与纯文本速查表。纯 Python 标准库零依赖，自研 TOON 解析器处理官方返回的非 JSON 营养格式。已附 MCP_INTEGRATION.md 说明实际使用的 Server、Tool、调用流程与业务价值，并提交 workbuddy.md 记录腾讯 WorkBuddy 开发上下文。
```

---

## 五、Issue 正文（精简版）

若校验对长文本敏感，使用此版：

```
【参赛申请】
项目名称：麦练营养官 · mcd-lift-nutrition-coach
项目地址：https://github.com/hachiday/mcd-women-fitness-meals-skill
项目简介：面向力量训练/增肌期女性的麦当劳配餐 Skill。把官方 MCP 的 160 条营养数据重排为「钠效率=钠÷蛋白」指标，实测同为约15克蛋白的餐品钠效率可差 6.5 倍，方案可在同等蛋白下少摄入约 474mg 钠。产出可截图分享的 HTML 配餐卡。纯 Python 零依赖，含 MCP_INTEGRATION.md 与 workbuddy.md。
```

---

## 六、发布步骤

1. 打开 <https://github.com/M-China/mcd-developer-innovation-challenge/issues>
2. 选择 **New issue**
3. 若有模板选择参赛申请模板（若无模板则直接新建空白 issue）
4. 粘贴标题与正文
5. 发布后等待系统回复报名成功/失败通知

---

## 七、报名成功后的必做事项

| # | 事项 | 说明 |
|---|---|---|
| 1 | 确认仓库为 **Public** | 当前状态已确认为 public ✅ |
| 2 | 补充 Topics | 见第二节 |
| 3 | 设置仓库简介 | 见第一节 |
| 4 | 推送本地新提交 | `.workbuddy/` 已从索引移除、标题与数字已修正，需推送 |
| 5 | 保持仓库可访问 | 活动期间不可转为 Private |
| 6 | **争取 Star** | 排名只看 Star，> 0 才能进榜 |

### ⚠️ 关于 Star 的重要性

活动排名**完全依据 GitHub 公开 Star 数**：

- Star = 0 → **不进榜、不获奖**
- 前 100 名 → 汉堡回车键玩具 + 程序员节徽章 + **3,000 WorkBuddy 积分**
- 前 3 名 → 另有巨无霸兑换券 + 10,240 积分

当前 Star = 0。距报名截止（10/25 23:59）还有 15 天。

---

## 八、合规自查清单

发布 Issue 前逐项确认：

- [x] 项目名称不含违规内容
- [x] 项目地址为纯 URL，无 Markdown 格式
- [x] 项目简介标题与正文之间**无换行符**
- [x] 简介中不含任何其他餐饮品牌名称
- [x] 简介不以减肥/瘦身为叙事
- [x] 简介不含医疗或营养建议
- [x] 仓库内 `mcp-config.example.json` 仅含环境变量占位符
- [x] 仓库内无真实 Token（已扫描验证）
- [x] `CONTEST_DECLARATION.md` 为官方原版未改动
- [x] 仓库创建时间在 2025-12-25 ~ 2026-10-25 区间内（实际 2026-10-10）
- [x] 仓库为 Public
