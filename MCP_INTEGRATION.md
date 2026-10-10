# MCP 集成说明

本项目基于**麦当劳中国官方 MCP Server** 构建。以下是实际使用的 Server、Tool、调用流程与业务价值。

---

## 一、Server 信息

| 项目 | 内容 |
|---|---|
| Server 名称 | `mcd-mcp` |
| 官方版本 | `1.0.0`（握手响应 `serverInfo` 实测值） |
| 接入地址 | `https://mcp.mcd.cn` |
| 传输协议 | Streamable HTTP |
| 鉴权方式 | 请求头 `Authorization: Bearer <MCP_TOKEN>` |
| 开放平台 | <https://open.mcd.cn/mcp> |
| 限流 | 每 Token 每分钟 600 次请求，超限返回 429 |

> 官方仓库：[M-China/mcd-mcp-server](https://github.com/M-China/mcd-mcp-server)

---

## 二、实际使用的 MCP Tool

本项目**仅使用 1 个 Tool 作为核心数据源**：

### `list-nutrition-foods` · 餐品营养信息列表

| 项 | 内容 |
|---|---|
| 用途 | 获取麦当劳常见餐品的能量、蛋白质、脂肪、碳水化合物、钠、钙等营养成分 |
| 入参 | **无参数**，一次返回全量营养表 |
| 返回 | `code` / `data` / `message`，其中 `data` 为 TOON 格式文本 |
| 实测规模 | **160 条**记录（去重后 158 条唯一餐品） |
| 调用频次 | 每次生成建议调用 1 次 |

### 辅助 Tool（可选增强，核心链路不依赖）

| Tool | 用途 | 本项目使用方式 |
|---|---|---|
| `query-meals` | 查询门店在售餐品列表 | 用户询问「今天还买得到吗」时校验推荐项在售 |
| `query-nearby-stores` | 查询附近门店 | 获取门店编码，供 `query-meals` 使用 |

> 📌 **设计取舍**：核心推荐流程**只依赖 `list-nutrition-foods` 一个工具**。这样用户无需提供地址即可获得完整建议，把门店校验降级为可选增强，避免因地址依赖链阻断主流程。

---

## 三、调用流程

```
用户提问「练后怎么吃，蛋白高钠又低」
        │
        ├─ [1] 读取环境变量 MCD_MCP_TOKEN
        │
        ├─ [2] MCP 握手
        │      POST https://mcp.mcd.cn
        │      method: initialize
        │      protocolVersion: 2024-11-05
        │      → 返回 serverInfo { name: "mcd-mcp", version: "1.0.0" }
        │
        ├─ [3] 声明已就绪
        │      method: notifications/initialized
        │
        ├─ [4] 调用营养工具
        │      method: tools/call
        │      name: list-nutrition-foods
        │      arguments: {}
        │      → 返回 160 条 TOON 格式记录
        │
        ├─ [5] 双层解包
        │      content[0].text  → 剥离 "API Response Information" 说明段
        │                      → 提取内层 {"success":true, "data":"..."}
        │      TOON 文本        → 解析表头 [160]{...} 与 CSV 数据行
        │
        ├─ [6] 营养引擎计算
        │      钠效率 = 钠(mg) ÷ 蛋白(g)
        │      约束：主食蛋白 ≥14g 且热量 ≤700 kcal
        │      → 选出钠效率最优的主食与饮品
        │
        ├─ [7] 组合对比
        │      「主食 + 低钠蛋白锚点」 vs 「同等蛋白量的高钠单品」
        │      → 量化可节省的钠摄入
        │
        └─ [8] 渲染产出物
               单文件 HTML 配餐卡（零外链、可离线打开、可截图分享）
               纯文本速查表（复制即可粘贴到任意聊天工具）
```

---

## 四、实现要点

### 4.1 MCP 响应是双层包裹的

`list-nutrition-foods` 的返回不是直接的营养数据，而是：

```
content[0].text
  └─ "## API Response Information\n\nBelow is the response from an API call..."
       （MCP 自动生成的说明段）
     └─ {"success":true,"code":200,"data":"[160]{productName,...}:\n  猪柳麦满分,null,1288,308,..."}
          └─ data 字段仍是字符串，且为 TOON 格式
```

实现中需**两层解包**：先剥离说明段提取 JSON，再解析 TOON。见 `scripts/mcd_client.py` 的 `extract_payload()`。

### 4.2 `data` 是 TOON 格式，不是 JSON

官方 `data` 字段采用紧凑行式文本格式：

```
[160]{productName,nutritionDescription,energyKj,energyKcal,protein,fat,carbohydrate,sodium,calcium}:
  猪柳麦满分,null,1288,308,16,16,24,781,213
  中薯条,null,1210,289,4,12,38,165,18
```

首行是表头声明（记录数 + 字段名），其后每行是一条 CSV 记录。

**解析难点与对策**：

| 难点 | 对策 |
|---|---|
| 品名可能含逗号 | 从**末尾固定 6 个数值槽位**向左切分，品名取左侧全部内容 |
| `nutritionDescription` 恒为 `null` | 不依赖其位置，固定取末尾 6 个数值 |
| 部分品名重复（如「小杯玉米杯」出现 2 次） | 按品名去重，保留首次出现 |
| 字段数异常 | 跳过该行而非让整批数据失败 |

完整解析实现见 `scripts/toon.py`。

### 4.3 服务端为无状态

实测握手**不返回 session id**，`tools/call` 也无需携带 `Mcp-Session-Id`。因此每次调用独立发起 HTTP 请求即可，不需维持长连接。

---

## 五、业务价值

### 5.1 解决一个未被回答的真实问题

麦当劳官方 MCP 提供了营养数据，但这些数据在默认呈现方式下（每样东西多少卡）**不适合力量训练人群**。

力量训练者的核心约束是**蛋白要吃够**，同时希望**控制钠摄入**（训练后胀气、生理期水肿）。本项目把 160 条原始数据重新组织为一个直接回答该问题的指标：

```
钠效率 = 钠(mg) ÷ 蛋白质(g)
```

### 5.2 从数据中发现的真实差距

对官方 160 条营养表实跑分析后，蛋白含量接近的单品间，钠效率差异显著：

| 餐品 | 蛋白质 | 钠 | 钠效率 |
|---|---:|---:|---:|
| 冰牛奶大杯 | 15 g | 154 mg | **10.3** |
| 儿童鱼排堡 | 15 g | 442 mg | **29.5** |
| 猪柳麦满分 | 16 g | 781 mg | **48.8** |
| 火腿扒早安营养卷 | 16 g | 1065 mg | **66.6** |

> 同为约 15~16 g 蛋白质，钠效率相差 **6.5 倍**。

引擎在真实数据上实测生成的方案：

| 方案 | 蛋白 | 钠 | 钠效率 |
|---|---:|---:|---:|
| 本方案（原味板烧鸡腿炒双蛋堡 + 优品豆浆小杯） | 33 g | 747 mg | 22.6 mg/g |
| 对照：果然多肉（蛋白量接近） | 36 g | 1343 mg | 37.3 mg/g |

> **单次可少摄入约 474 mg 钠**（约合 1.2 g 食盐）。

### 5.3 降低使用门槛

- **体重是可选输入** —— 不提供也能获得完整建议，只是蛋白目标不精确到克
- **门店查询是可选增强** —— 核心流程不依赖地址
- **产出物可离线打开** —— HTML 配餐卡零外链、零 JS、零 CDN 依赖

---

## 六、安全与合规

| 项 | 做法 |
|---|---|
| Token 存储 | **仅从环境变量 `MCD_MCP_TOKEN` 读取**，不落盘、不进代码 |
| 仓库内容 | `mcp-config.example.json` 仅含 `${MCD_MCP_TOKEN}` 占位符 |
| `.gitignore` | 已排除 `docs/mcd-mcp-server-token.txt`、`.env`、`*.token` 等 |
| 外部依赖 | **零第三方依赖**，仅用 Python 标准库 |
| 个人信息 | 不收集、不存储、不上传任何用户数据；体重为用户本地可选输入 |

---

## 七、复现方式

```bash
# 1. 设置 Token（申请：https://open.mcd.cn/mcp）
export MCD_MCP_TOKEN=<你的 MCP Token>

# 2. 运行（实时调用 MCP）
python scripts/main.py --weight 55 --training-day --html out/card.html

# 或离线演示（内置快照，不消耗配额）
python scripts/main.py --demo --weight 55 --training-day
```

实测环境：Python 3.13，Windows 11，握手返回 `mcd-mcp 1.0.0`，营养表 160 条。
