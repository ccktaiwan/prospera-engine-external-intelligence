# ── Prospera SYSTEM HEADER (ADR-0032/SBOM) ──
# 性質:engineering ｜設計:Kevin 架構 ｜執行:AI 工具(claude.ai+Claude Code)
# 驗證:實測 oauth/access_token ｜IP:創造性歸 Kevin(發明人), AI 為執行工具 (ADR-0032)
"""meta_token_exchange.py — 用 App ID + App Secret 換 Meta App Access Token（純 API，不碰瀏覽器）。

換取端點：GET https://graph.facebook.com/oauth/access_token
  ?client_id=<APP_ID>&client_secret=<APP_SECRET>&grant_type=client_credentials

來源優先序：環境變數 META_APP_ID/META_APP_SECRET，否則讀同目錄 .env。
成功 → 寫回 .env 的 META_ACCESS_TOKEN（.env 已 gitignore，不進 git）。
安全：絕不把 secret/token 印到 stdout（只印遮罩後尾 4 碼確認）。
"""
from __future__ import annotations
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent / ".env"


def _load_env_file(path: Path) -> dict:
    d = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip()
    return d


def _mask(s: str) -> str:
    return f"<…{s[-4:]}>" if s and len(s) >= 4 else "<set>"


def _write_env_token(path: Path, token: str) -> None:
    """更新/插入 META_ACCESS_TOKEN，保留其餘行。"""
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    out, done = [], False
    for line in lines:
        if line.strip().startswith("META_ACCESS_TOKEN="):
            out.append(f"META_ACCESS_TOKEN={token}")
            done = True
        else:
            out.append(line)
    if not done:
        out.append(f"META_ACCESS_TOKEN={token}")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def main() -> int:
    file_env = _load_env_file(ENV_PATH)
    app_id = os.environ.get("META_APP_ID") or file_env.get("META_APP_ID", "")
    app_secret = os.environ.get("META_APP_SECRET") or file_env.get("META_APP_SECRET", "")

    if not app_id or not app_secret:
        print("[meta-token] ❌ 缺 META_APP_ID / META_APP_SECRET。")
        print("  → 請於 .env 填入（範本 .env.example），或設環境變數後重跑。")
        return 2

    params = {
        "client_id": app_id,
        "client_secret": app_secret,
        "grant_type": "client_credentials",
    }
    url = "https://graph.facebook.com/oauth/access_token?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:200]
        print(f"[meta-token] ❌ HTTP {e.code}：{body}")
        print("  → 多為 App ID/Secret 錯誤或 app 未啟用；核對 developers.facebook.com 設定。")
        return 1
    except Exception as e:
        print(f"[meta-token] ❌ {type(e).__name__}: {str(e)[:120]}")
        return 1

    token = data.get("access_token", "")
    if not token:
        print(f"[meta-token] ❌ 回應無 access_token：{str(data)[:160]}")
        return 1

    _write_env_token(ENV_PATH, token)
    print(f"[meta-token] ✅ 取得 App Access Token {_mask(token)} 已寫入 .env（gitignore，不進 git）。")
    print("  → 下一步：python3 -c 'load .env' 跑眼4 ads_archive 實測。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
