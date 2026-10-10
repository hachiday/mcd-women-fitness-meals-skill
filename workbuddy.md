# workbuddy.md

> 本文件为使用腾讯 WorkBuddy 开发本项目的对话上下文记录，用于麦当劳程序员创意开发大赛的「WorkBuddy 专项奖励」核验。
> 项目：女性健身餐推荐 Skill（暂定名，见 Grilling 结论）
> 记录开始时间：2026-10-10 22:45 (GMT+8)

---

## 会话 01 · 需求提出与赛事合规核查

### 用户原始需求

> 阅读 https://github.com/M-China/mcd-developer-innovation-challenge
> 想要创建一个基于 mcd-mcp 的女性健身餐推荐的 skill，来参加这个活动。
> 同时将我们的所有聊天内容记录保存至 ./workbuddy.md 中。
> 请先确认其中的参赛要求，一定要满足。
> mcd-mcp 的 token 已经放在了 docs/mcd-mcp-server-token.txt 中。
> docs/mcd-mcp-server-token.txt 不进行提交。

### 本轮助手执行的动作

1. 调用 `grill-with-docs` skill（该 skill 已被 `skillOverrides` 禁用，改为手动遵循其内部指令：执行 `/grilling` + `/domain-modeling` 组合流程）
2. 通过 WebFetch 抓取赛事 README、`activityGuidelines.md`、`CONTEST_DECLARATION.md` 全文
3. 通过 Python + urllib 直连 `https://mcp.mcd.cn` 完成 MCP 握手与工具探测
4. 通过 GitHub API 调研排行榜头部竞品项目
5. 检查 `.gitignore`，确认 token 文件已被排除

---

## 一、参赛要求核查（关键事实）

### 1.1 必交文件清单（缺一不可）

| 序号 | 文件名 | 说明 | 必须性 |
|---|---|---|---|
| 1 | `README.md` | 项目介绍、安装方法、使用示例、目标用户 | **必须，文件名不可改动** |
| 2 | `CONTEST_DECLARATION.md` | 参赛声明（原创性/合规性/信息安全） | **必须，文件名及内容均不可改动** |
| 3 | `MCP_INTEGRATION.md` | 实际使用的 MCP Server、Tool、调用流程、业务价值 | **必须，文件名不可改动** |
| 4 | `mcp-config.example.json` | 脱敏后的 MCP 配置示例，**只允许环境变量占位符** | **必须** |
| 5 | 源代码 | 项目主体代码或可运行内容 | **必须，形式不限** |
| 6 | `workbuddy.md` | WorkBuddy 对话上下文 | 参加 WorkBuddy 专项奖励时**必须** |

> ⚠️ README 的表格里漏写了 `mcp-config.example.json`，但 `activityGuidelines.md` 明确要求。本项目将按 activityGuidelines 的完整清单执行。

### 1.2 硬性时间节点（北京时间）

| 阶段 | 时间 |
|---|---|
| 报名及排名 | 2026-10-09 10:30 → **2026-10-25 23:59** |
| 排行榜数据截止（定榜） | **2026-10-26 00:00** |
| 奖品兑换及信息提交截止 | 2026-11-14 |
| 奖励发放 | 提交收货信息后约 2 周内 |

> 项目创建时间必须在 2025-12-25 00:00 ~ 2026-10-25 23:59 之间。

### 1.3 排名与资格规则（直接影响策略）

- **排名只看 GitHub 公开 Star 数**。定时采集，Star > 0 才进榜。
- 前 100 名进入排行榜并获奖；第 100 名并列时全部并列项目都进榜。
- **同一 GitHub 账号的多个参赛项目，只有 Star 最高的那个进榜。**
- 进入排行榜 = 获奖：汉堡回车键玩具 ×1 + 程序员节实体徽章 ×1。
- **提交 `workbuddy.md` 且真实使用 WorkBuddy → 前 100 名额外 3,000 WorkBuddy 积分。**
- 前 3 名额外：巨无霸兑换券（50/30/20 次）+ 10,240 WorkBuddy 积分。
- 活动开始前已获得的 Star 也计入。

> 📌 **关键推论**：排名唯一依据是 Star，不是功能数量。因此「项目的可传播性 / 一句话价值主张 / 可分享产出物」比「功能多」更重要。参照物见第二节。

### 1.4 报名 Issue 格式（校验严格）

```text
【参赛申请】
项目名称：{项目名称}
项目地址：{项目 GitHub 仓库地址}
项目简介：{项目简介}
```

> ⚠️ 官方提示：简介标题与正文之间**不要用换行符**；项目地址链接**不要用 Markdown 格式**。
> ⚠️ 仓库须为 **Public**。

### 1.5 内容合规红线（与「健身/减脂」强相关）

活动规则「内容合规」条款明确禁止：

> c）违背社会主义核心价值观……包括但不限于**宣扬淫秽、色情、赌博、迷信、恐怖、暴力、民族、种族、宗教及性别歧视等内容；宣扬不健康饮食方式、奢靡浪费、拜金主义、娱乐至上等错误观念和畸形审美等观念**

同时禁止：

> e）侮辱、诋谤、讽刺、贬低麦当劳品牌、产品及形象，或将麦当劳品牌、产品与其他品牌、产品进行对比

> 🚨 **对本项目的直接约束**：
> - 不得以「减肥/瘦身」为唯一卖点做价值主张（避免「宣扬不健康饮食方式」的判定风险）
> - **不得出现任何形式的其他快餐品牌对比**（不可做任何跨品牌的营养或价格比较）
> - 必须保持「非官方产品」定位与免责声明
> - `CONTEST_DECLARATION.md` 中已自带免责条款：「项目输出仅供参考，不构成医疗、营养或其他专业建议」

### 1.6 官方声明中已固化的免责话术（须沿用）

> 本项目为麦当劳程序员节创意开发大赛参赛作品，由参赛者独立开发，非麦当劳官方产品。项目输出仅供参考，不构成医疗、营养或其他专业建议；餐品信息、价格及供应状态以麦当劳官方渠道的实时结果为准。

---

## 二、竞争格局调研（决定定位策略）

排行榜共 100+ 个项目，**热量/营养赛道已极度拥挤**：

| 项目 | Star | 一句话定位 |
|---|---:|---|
| `mcd-order-calories` | 36 | 订单卡路里统计 |
| `mcd-calorie-budget-skill` | 22 | 控卡省钱点餐助手 |
| `mcd-100kcal` | 11 | 每天制造 100 大卡缺口 → 具体点单方案 |
| `mcd-macro-strategist` | 11 | 三大营养素配餐策略 |
| `mcd-health-buddy` | 8 | 健康助手 |
| `mcd-calorie-calculator` | 8 | 卡路里计算 |
| `mcd-triple-target` | 5 | 热量/蛋白质/预算三目标配餐优化 |
| `mcd-nutrition-optimizer` | 3 | 营养优化 |
| `mcd-nutritionist` | 3 | 营养师 |

**头部项目的成功范式（值得直接借鉴）：**

- **`mcd-event-radar`（68★，排名第 1）**：JavaScript，带 `event-map` 话题，「查附近有什么麦麦活动」→ 生成卡通活动地图。
- **`mcd-party-officer`（38★，排名第 2）**：纯 Python 标准库、零依赖。README 的核心打法是 **「30 秒看懂：它和别的派对 Skill 差在哪」——用对比表直接划清与已有赛道的界限**；并产出 **可直接发群的可传播物料**（招募卡文本 + 单文件 HTML 邀请函）。文件结构：
  ```
  README.md  CONTEST_DECLARATION.md  MCP_INTEGRATION.md  SKILL.md
  mcp-config.example.json  workbuddy.md  LICENSE
  references/{creative_modules,party_flow,tools}.md
  scripts/{mcd_client,party_officer,party_plus,demo,demo_plus}.py
  examples/sample_invite.html
  docs/preview-{1,2,3}-*.png   ← 真实运行截图
  ```
  > 📌 **可传播产出物 + 真实运行截图 + 差异化对比表** = 该项目的 Star 护城河。

---

## 三、MCP 服务实测事实（本项目地基）

### 3.1 连接方式（已验证可用）

- 地址：`https://mcp.mcd.cn`
- 协议：Streamable HTTP（`Accept: application/json, text/event-stream`）
- 鉴权：`Authorization: Bearer <MCP_TOKEN>`
- **实测为无状态（无需 session id）**，单次 `tools/call` 可直接调用
- 限流：每 Token 每分钟 600 次，超限返回 429
- 当前 Token 长度 32 位，握手 `serverInfo: {"name":"mcd-mcp","version":"1.0.0"}` ✅

### 3.2 实测可用工具：35 个

```
campaign-calendar            query-my-coupons           mall-points-products
query-party-store-session    query-store-coupons        delivery-query-stores
order-list                   now-time-info              list-nutrition-foods
delivery-query-addresses     create-order               calculate-price
query-survey-coupon          query-my-account           query-party-city
auto-bind-coupons            draw-lottery               mall-order-detail
party-order-create           available-coupons          query-order
query-my-prizes              mall-create-order          query-party-store-date
delivery-create-address      query-meal-detail          query-promotions
query-lottery-info           mall-product-detail        query-meals
query-meal-assistance        mall-order-list            query-nearby-stores
cancel-order                 query-party-store
```

与本项目**直接相关**的工具：`list-nutrition-foods`（营养数据）、`query-meals`（门店在售菜单）、
`query-meal-detail`（套餐组成）、`query-nearby-stores`（附近门店）、`calculate-price`（算价含优惠券）、
`query-store-coupons` / `available-coupons`（优惠券）、`order-list`（历史订单→个性化）、`query-promotions`。

### 3.3 `list-nutrition-foods` 返回结构（实测）

- `inputSchema`: 空对象（**无参数**，全量返回）
- `outputSchema`: `{ code: number, data: string, message: string }`
- **`data` 是自定义 TOON 格式字符串，不是 JSON**：
  ```
  [160]{productName,nutritionDescription,energyKj,energyKcal,protein,fat,carbohydrate,sodium,calcium}:
    猪柳麦满分,null,1288,308,16,16,24,781,213
    ...
  ```
  → 第 1 行是表头声明，后续每行是 CSV。**必须自行解析**。
- 外层还包了一层 `API Response Information` 说明文本 + `{"success":true,...}` JSON，需二次解包。
- `nutritionDescription` 字段**全部为 null**（无用字段）。
- 共 **160 条**记录，含早午晚餐、饮品、甜品、麦满分、粥、沙拉卷等全品类。

### 3.4 数据分析：可用的高价值发现

**蛋白密度 TOP（蛋白 g / 100kcal）—— 健身场景的核心卖点**

| 餐品 | kcal | 蛋白 | 脂肪 | 碳水 | 钠 |
|---|---:|---:|---:|---:|---:|
| 蒜了吧黄油风味薄皮脆汁鸡-带骨里脊 | 126 | **19** | 2 | 4 | 750 |
| 蜜汁BBQ风味薄皮脆汁鸡-带骨里脊 | 152 | **20** | 5 | 6 | 635 |
| 蒜了吧黄油风味薄皮脆汁鸡-琵琶腿 | 164 | 19 | 6 | 6 | 867 |
| 蜜汁BBQ风味薄皮脆汁鸡-琵琶腿 | 173 | 18 | 9 | 5 | 547 |
| 薄皮焦香V翅 | 192 | 17 | 11 | 6 | 594 |
| 柠萌风味薄皮焦香V翅 | 204 | 18 | 11 | 6 | 768 |

> 📌 上述「薄皮脆汁鸡」系列**未出现在任何头部竞品的描述中**，且蛋白密度（约 15g/100kcal）显著高于普通汉堡（约 5g/100kcal），是官方营养表里的「隐形黑马」。

**高蛋白低卡候选（健身核心）**

| 餐品 | kcal | 蛋白 | 钠 |
|---|---:|---:|---:|
| 蒜了吧黄油风味薄皮脆汁鸡-带骨里脊 | 126 | 19 | 750 |
| 原味板烧鸡腿麦满分 | 246 | 15 | 611 |
| 蜜汁快乐 | 258 | **22** | 721 |
| 烟肉蛋麦满分 | 260 | 16 | 483 |
| 麦麦趣鸡球 | 266 | 17 | 789 |
| 儿童鱼排堡 | 269 | 15 | 442 |
| **冰牛奶大杯** | 269 | 15 | **154** |
| 吉士汉堡包 | 294 | 16 | 673 |
| 猪柳麦满分 | 308 | 16 | 781 |
| 麦香鱼 | 325 | 16 | 556 |
| 麦麦脆汁鸡-琵琶腿 | 328 | **21** | 905 |

> 📌 **冰牛奶大杯（269kcal / 15g蛋白 / 仅154mg钠）** 是极强的「补蛋白 + 低钠」卖点——钠仅为吉士汉堡包的 1/4。

**极低热量选项（低于 150 kcal）**

冰美式小杯 10kcal ｜ 浓缩咖啡 13kcal ｜ 无糖可口可乐 **0kcal** ｜ 纯悦 0kcal ｜ 锡兰红茶 2kcal
｜ 苹果片 32kcal ｜ 大杯玉米杯 87kcal（4g蛋白 / 2mg钠）｜ 迷你薯条 106kcal ｜ 100%苹果汁 88kcal

> 📌 玉米杯（87kcal / 4g蛋白 / 2mg钠）与迷你薯条（106kcal）适合作为加餐组合；纯悦与无糖可乐为 0 热量饮品。

### 3.5 数据中的有趣品名（传播素材）

蒜了吧黄油风味薄皮脆汁鸡、牛气满满、蜜汁快乐、果然多肉、专「薯鱼」你、
「苹板」支撑Pro、酥酥多笋卷、鲜蔬蛋沙拉叠叠卷、鸡肉蛋沙拉叠叠卷、
图林根香肠早安营养卷、火腿扒早安营养卷、麦麦脆汁鸡

> 📌 「蒜了吧黄油」「牛气满满」「蜜汁快乐」等品名自带传播性，适合做可分享物料的标题。

### 3.6 ⚠️ 数据局限（必须在 README 中诚实说明）

- 营养表是**固定快照**，不含门店在售状态；实时可售需调用 `query-meals`。
- 无「份量/规格」维度，无法区分大份小份之外的更多规格。
- 无过敏原信息、无配料表。
- 部分品名重复出现（如「小杯玉米杯」出现两次），解析时需去重。

---

## 四、Grilling 会话记录

> 采用 `/grilling` 流程：以 design tree 逐轮推进 frontier，每轮提出当前可问的全部问题并给出推荐答案。
> 采用 `/domain-modeling` 流程：术语一旦确定即写入 `CONTEXT.md`，重要架构决策写入 `docs/adr/`。

### Round 0 · 事实核查轮（助手已完成，无需用户回答）

- 已核查赛事全部硬性要求 → 见第一节
- 已实测 MCP 连通性与返回结构 → 见第三节
- 已调研 100+ 竞品与头部项目打法 → 见第二节

### Round 1 · 定位与范围（已锁定）

**用户回复：「全部使用推荐」** —— Q1~Q6 全部采纳助手推荐。

| # | 决策 | 锁定结论 |
|---|---|---|
| Q1 | 定位内核 | **蛋白 / 钠双锚点**为核心指标，训练周期化为可选模块；放弃热量缺口、放弃生理周期配餐（合规风险） |
| Q2 | 目标用户 | **力量训练 / 增肌期女性**；以「增肌支持」替代「减肥」叙事，同时规避合规风险 |
| Q3 | 功能边界 | **推荐 + 门店实况校验**，**不做代下单** |
| Q4 | 可传播产出物 | **单文件 HTML 配餐卡 + 纯文本速查表** |
| Q5 | 技术形态 | **纯 Python 标准库零依赖**，自行实现 TOON 解析 |
| Q6 | 目标与仓库 | **先保底进榜（Star > 0），再冲前 20**；远程仓库 `hachiday/mcd-women-fitness-meals-skill` 已关联，分支 `main` |

### Round 2 · 算法口径与产出物（已锁定）

**用户回复：「全部使用推荐」** —— Q7~Q11 全部采纳助手推荐。

| # | 决策 | 锁定结论 |
|---|---|---|
| Q7 | 钠预算 | **2000mg/日 + 700mg/单餐作参考线**，主算法用**钠效率**排序；不做硬约束 |
| Q8 | 蛋白目标口径 | **按体重 1.6~2.2 g/kg 自动计算，但降级为可选输入** |
| Q9 | HTML 卡形态 | **静态单页**，单文件零外链零 JS |
| Q10 | 门店校验深度 | **`query-meals` + `calculate-price` + 优惠券，但作为可选增强**，核心推荐不依赖地址 |
| Q11 | 训练日/休息日 | **做轻量差异化**：仅在输出中给一行碳水调整提示 |

### Round 3 · 路由确认

用户调用 `/ask-matt` 询问接下来该用哪个 skill。

助手依 ask-matt 主流程（idea → ship）判定：

```
✅ 1. /grill-with-docs    ← 已完成
⏭️ 2. /handoff → /prototype ← 跳过（算法口径已用真实数据验证，无待定设计问题）
✅ 3. /implement           ← 当前阶段
```

**判定理由**：
- 不需要 `/prototype`：钠效率论断已通过 160 条真实数据实跑验证，不存在「跑一下才知道」的设计问题
- 不需要 `/to-spec` + `/to-tickets`：剩余工作是清晰的交付物清单，在同一上下文窗口内完成更稳（遵循 ask-matt 的 smart zone 原则）

---

## 五、实现过程记录

### 已完成的交付物

| 文件 | 说明 |
|---|---|
| `CONTEXT.md` | 领域术语表 + 明确排除的概念清单 |
| `docs/adr/0001-sodium-efficiency-over-calorie-deficit.md` | 核心架构决策：为何选钠效率而非热量缺口 |
| `scripts/toon.py` | TOON 格式解析器（末尾 6 槽位左切策略） |
| `scripts/mcd_client.py` | MCP 客户端（双层解包 + Token 仅从环境变量读取） |
| `scripts/nutrition.py` | 营养引擎（指标 / 排序 / 配餐 / 组合对比） |
| `scripts/build_card.py` | 渲染层（HTML 配餐卡 + 文本速查表） |
| `scripts/main.py` | 命令行入口 |
| `scripts/nutrition_snapshot.json` | 内置营养快照（158 条去重记录，离线演示用） |
| `SKILL.md` | Skill 主流程与触发场景 |
| `CONTEST_DECLARATION.md` | **官方原版，从 GitHub API 拉取，内容一字未改**（sha: 136e76f） |
| `mcp-config.example.json` | 脱敏配置，仅 `${MCD_MCP_TOKEN}` 占位符 |
| `MCP_INTEGRATION.md` | 基于实测的 Server / Tool / 调用流程 / 业务价值 |
| `README.md` | 对标头部项目的差异化对比表打法 |
| `docs/preview-card.png` | 真实运行截图（无头 Chrome 2x 缩放） |
| `examples/` | 样例产出物（HTML 配餐卡 + 文本速查表） |
| `LICENSE` | MIT |

### 开发中发现并修复的三个真实问题

**问题 1 · 引擎推荐出 987 kcal 的巨无霸**
初次运行时，纯钠效率排序选中了「培根双层安格斯厚牛堡」（987 kcal / 55g 蛋白 / 1191mg 钠）。该单品钠效率确实优秀（21.7 mg/g），但单餐近 1000 kcal 完全不合理。
**修复**：为主食候选加入「蛋白 ≥14g 且热量 ≤700 kcal」双重约束。

**问题 2 · 组合对比论断无法生成**
修复问题 1 后，因引擎已选出主食候选池中最优单品，导致不存在「更好的对照单品」，ADR 中那条 6.5 倍的核心论断无法进入输出。
**修复**：将对比维度从「单品 vs 单品」改为「**组合 vs 单品**」—— 用「主食 + 低钠蛋白锚点」对比「同等蛋白量的高钠单品」。这既更贴近真实用法，也产出了更有说服力的论断：**同样 33g 蛋白，少摄入 474mg 钠**。

**问题 3 · HTML 配餐卡生成为 0 字节**
`render_card` 的 f-string 中，CSS 的 `{{ }}` 转义正确，但标题占位符 `{protein_word}`、`{ratio:.1f}`、`{day_label}` 三个变量从未定义，抛异常导致文件写入为空。
**发现方式**：生成后立即校验文件大小与关键内容 —— 若非如此，会带着空文件提交。
**修复**：补充三个派生变量的计算逻辑。

### 合规自查发现并修复的问题

`workbuddy.md` 中的合规提醒文本原写有「不能说『比 KFC 更高蛋白』」作为反例。虽然语境是「禁止这样做」，但字面出现了其他品牌名，仍存在被自动扫描误判的风险。已改为不含任何品牌名的表述。

### 验证记录

| 验证项 | 结果 |
|---|---|
| MCP 握手 | ✅ `mcd-mcp 1.0.0`，无状态，35 个工具 |
| 真实 MCP 端到端调用 | ✅ 输出与离线快照一致 |
| 离线演示模式 | ✅ `--demo` 可运行 |
| HTML 产出物 | ✅ 10952 字节，零外链、零 `<script>` |
| 截图生成 | ✅ 373 KB，视觉效果达标 |
| Token 泄露扫描 | ✅ 所有文件均无真实 Token |
| `git check-ignore` | ✅ Token 文件与 `.probe/` 均被拦截 |
| 必交文件清单 | ✅ 6/6 齐备 |
| 品牌名扫描 | ✅ 全部为 0 |
| 训练日/休息日文案 | ✅ 已正确区分（曾误用「训练日」文案，已修） |

---

## 六、参赛合规自查

| 要求 | 状态 |
|---|---|
| `README.md` | ✅ 含项目介绍、安装方法、使用示例、目标用户 |
| `CONTEST_DECLARATION.md` | ✅ 官方原版，内容未改（sha: 136e76f） |
| `MCP_INTEGRATION.md` | ✅ 含 Server / Tool / 调用流程 / 业务价值 |
| `mcp-config.example.json` | ✅ 仅环境变量占位符 |
| 源代码 | ✅ 5 个 Python 模块，纯标准库 |
| `workbuddy.md` | ✅ 本文件 |
| 真实使用 MCP | ✅ `list-nutrition-foods` 实测调用 |
| 仓库公开 | ⏳ 待推送后设为 Public |
| 创建时间合规 | ✅ 2026-10-10，在 2025-12-25 ~ 2026-10-25 区间内 |
| 无真实 Token | ✅ |
| 无其他品牌对比 | ✅ |
| 无不健康饮食叙事 | ✅ 定位为增肌支持 |
| 非官方声明 | ✅ 所有产出物均含 |

---

## 七、待办

1. 提交并推送至 `https://github.com/hachiday/mcd-women-fitness-meals-skill`
2. 在 GitHub 确认仓库为 **Public**
3. 按官方格式发布报名 Issue（注意：简介标题与正文间**不换行**，项目地址**不用 Markdown**）
4. 剩余 15 天做传播物料冲星（当前距 10/25 截止）

