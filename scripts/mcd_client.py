"""MCP 客户端 —— 麦当劳 MCP Server（https://mcp.mcd.cn）的最小可运行实现。

特性：
  * 仅依赖 Python 标准库（urllib），无需 pip install
  * Streamable HTTP 协议，无状态（实测无需 session id）
  * 内置 TOON 解析
  * Token 只从环境变量读取，不落盘、不进代码

环境变量：
    MCD_MCP_TOKEN   必填。麦当劳 MCP Token（https://open.mcd.cn/mcp 申请）
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from toon import dedupe_by_name, parse_toon_table

__all__ = ["MCPClient", "MCPError", "MissingTokenError", "extract_payload"]

MCP_URL = "https://mcp.mcd.cn"
TIMEOUT_SEC = 60


class MCPError(RuntimeError):
    """MCP 调用失败。"""


class MissingTokenError(MCPError):
    """未配置 MCD_MCP_TOKEN 环境变量。"""


def extract_payload(text: str) -> Any:
    """从 MCP 工具返回的文本中取出真实负载。

    MCP 工具的 content[0].text 通常包含两段：
      1) 一段自动生成的「API Response Information」说明
      2) 紧随其后的原始 JSON（可能被 ``` 包裹）
    本函数定位第一个 { 或 [ 起始的 JSON 片段并解析。
    """
    text = text.strip()

    # 优先寻找 ``` 代码块
    if "```" in text:
        for block in text.split("```")[1:]:
            block = block.strip()
            for prefix in ("json", "JSON", ""):
                if block.startswith(prefix):
                    block = block[len(prefix) :].strip()
                    break
            if block.startswith("{") or block.startswith("["):
                try:
                    return json.loads(block)
                except json.JSONDecodeError:
                    continue

    # 否则回退：扫描第一个可解析的 JSON 片段
    for i, ch in enumerate(text):
        if ch in "{[":
            try:
                return json.loads(text[i:])
            except json.JSONDecodeError:
                continue
    return text


class MCPClient:
    """麦当劳 MCP Server 的轻量客户端。"""

    def __init__(self, token: str | None = None, url: str = MCP_URL) -> None:
        token = token or os.environ.get("MCD_MCP_TOKEN", "")
        if not token.strip():
            raise MissingTokenError(
                "未找到 MCP Token。请先访问 https://open.mcd.cn/mcd-cn 申请，\n"
                "然后设置环境变量：\n"
                "  Linux/macOS: export MCD_MCP_TOKEN=你的Token\n"
                "  Windows PowerShell: $env:MCD_MCP_TOKEN=\"你的Token\""
            )
        self._token = token.strip()
        self._url = url
        self._inited = False

    # ---------- 底层 ----------

    def _rpc(self, method: str, params: dict[str, Any] | None = None, _id: int = 1) -> Any:
        body: dict[str, Any] = {"jsonrpc": "2.0", "id": _id, "method": method}
        if params is not None:
            body["params"] = params

        req = urllib.request.Request(
            self._url, data=json.dumps(body).encode("utf-8"), method="POST"
        )
        req.add_header("Authorization", f"Bearer {self._token}")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json, text/event-stream")

        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
                raw = resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:400]
            hint = {
                401: "Token 无效或已过期，请重新申请",
                429: "触发限流（600 次/分钟），请降低调用频率",
            }.get(exc.code, "")
            raise MCPError(f"HTTP {exc.code} {hint}\n{detail}") from exc
        except urllib.error.URLError as exc:
            raise MCPError(f"网络请求失败: {exc.reason}") from exc

        # Streamable HTTP 可能返回 SSE 帧
        for line in raw.splitlines():
            line = line.strip()
            if line.startswith("data:"):
                raw = line[5:].strip()
                break

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise MCPError(f"响应不是合法 JSON: {raw[:300]}") from exc

        if "error" in parsed:
            raise MCPError(f"MCP 返回错误: {parsed['error']}")
        return parsed.get("result")

    def _init(self) -> None:
        if self._inited:
            return
        self._rpc(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "mcd-women-fitness-meals-skill", "version": "1.0.0"},
            },
        )
        # 通知服务端（失败可忽略，服务端为无状态）
        try:
            nreq = urllib.request.Request(
                self._url,
                data=json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}).encode(),
                method="POST",
            )
            nreq.add_header("Authorization", f"Bearer {self._token}")
            nreq.add_header("Content-Type", "application/json")
            nreq.add_header("Accept", "application/json, text/event-stream")
            urllib.request.urlopen(nreq, timeout=30).read()
        except Exception:  # noqa: BLE001 - 通知失败不应阻断调用
            pass
        self._inited = True

    def call(self, tool: str, arguments: dict[str, Any] | None = None) -> str:
        """调用一个 MCP 工具，返回其 content[0].text 原文。"""
        self._init()
        result = self._rpc("tools/call", {"name": tool, "arguments": arguments or {}}, _id=2)
        try:
            return result["content"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise MCPError(f"工具 {tool} 返回结构异常: {str(result)[:200]}") from exc

    # ---------- 业务方法 ----------

    def list_nutrition_foods(self) -> list[dict[str, Any]]:
        """获取官方营养快照（已去重）。

        Returns:
            每条记录含 productName / energyKcal / protein / fat /
            carbohydrate / sodium / calcium 等字段。
        """
        text = self.call("list-nutrition-foods")
        payload = extract_payload(text)

        if isinstance(payload, dict):
            if payload.get("success") is False:
                raise MCPError(f"接口返回失败: {payload.get('message')}")
            data = payload.get("data")
        else:
            data = payload

        if isinstance(data, str):
            records = parse_toon_table(data)
        elif isinstance(data, list):
            records = data
        else:
            raise MCPError(f"无法识别的 data 结构: {type(data).__name__}")

        return dedupe_by_name(records)

    def list_tools(self) -> list[str]:
        """列出服务端所有可用工具名。"""
        self._init()
        result = self._rpc("tools/list", {}, _id=3)
        return [t["name"] for t in result.get("tools", [])]

    def query_meals(self, store_code: str, **kwargs: Any) -> Any:
        """查询门店在售菜单（可选增强项）。"""
        args = {"storeCode": store_code}
        args.update(kwargs)
        return extract_payload(self.call("query-meals", args))
