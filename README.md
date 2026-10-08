# cnki-search — 知网论文检索（16 字段 / 5 排序 / 专业检索）

> CNKI (China National Knowledge Infrastructure) paper search CLI: 16 search
> fields, 5 sort modes, expert query expression. Pure Python, built-in WAF
> solver, no browser needed.

> 引文格式导出（GB/T 7714 / EndNote / 知网研学）见姊妹仓
> **[cnki-citation](https://github.com/66666-design/cnki-citation)**。

## 安装

```bash
pip install requests beautifulsoup4 numpy pillow pycryptodome
# 同目录需要姊妹仓的 cnki_session.py（会话层共用）：
#   git clone https://github.com/66666-design/cnki-session
```

`cnki_search.py` 与 `cnki_session.py` 放同一目录即可运行。

## 用法

```bash
# 按主题搜（默认）
python cnki_search.py search 大语言模型

# 按作者搜、按被引降序
python cnki_search.py search 深度学习 --field AU --sort cited

# 多页 + 结构化 JSON
python cnki_search.py search 碳排放 --pages 3 --json out.json

# 专业检索：知网检索表达式透传（AND/OR/NOT、% 通配、+ 并列、() 分组）
python cnki_search.py expert "TI='知识图谱' AND AU='刘峤'"

# 页码范围：取第 3-4 页（--start-page 起点，--pages 页数）
python cnki_search.py search 大语言模型 --start-page 3 --pages 2
```

退出码：0 成功；2 验证码未通过；3 无结果；1 其他错误。

## 检索字段（16 种，`--field`）

| 代码 | 含义 | 代码 | 含义 |
|---|---|---|---|
| SU | 主题（默认） | RP | 通讯作者 |
| TKA | 篇关摘 | AF | 作者单位 |
| KY | 关键词 | FU | 基金 |
| TI | 篇名 | AB | 摘要 |
| FT | 全文 | CO | 小标题 |
| AU | 作者 | RF | 参考文献 |
| FI | 第一作者 | CLC | 分类号 |
| LY | 文献来源 | DOI | DOI |

## 排序方式（`--sort`）

`relevance`(相关度=FFD) / `time`(发表时间=PT，默认) / `cited`(被引=CF) /
`download`(下载=DFR) / `overall`(综合=ZH)，均为降序。知网侧限制：排序只在
800 万条记录以内有效。

## 页码范围（`--start-page` + `--pages`）

每页固定 20 条（知网 pageSize 固定）。`--start-page N --pages M` 取第 N 页起
共 M 页。`--start-page 1 --pages 10` = 前 200 条。知网翻页上限 300 页
（约 6000 条），排序只在 800 万条内有效。底层实现：boolSearch=true 的搜索
触发形态仅对第 1 页有效（pageNum>0 直接回空），工具先触发搜索拿 turnpage
令牌，再从起点页起用翻页形态取数，跳页也能直接取。

## 专业检索（`expert` 子命令）

知网检索表达式原样透传，等价于网页「专业检索」。运算符：
`AND` / `OR` / `NOT`、`=` 精确、`%` 通配、`+` 并列、`()` 分组、`$` 截词。
字段用上表 16 个代码 + CF(被引频次)。底层走 `SearchType=4 + Field:EXPERT`。

## 工作原理

- 检索：`POST https://kns.cnki.net/kns8s/brief/grid`，表单仿 kns8s 前端 SPA。
  翻页需第 1 页响应里的 `#hidTurnPage` 令牌。
- WAF 过验全自动（详见 [cnki-session](https://github.com/66666-design/cnki-session)
  README）：知网对部分请求随机返回 AJ-Captcha 滑块挑战，会话层内置纯 Python 求解器。
- 会话缓存：`_cnki_state.json`（已 gitignore），减少重复过验。

## 隐私与合规

- `_cnki_state.json` 缓存知网会话 cookie，只存在于本机，请勿分享。
- 只读取公开可浏览的文献元数据，不下载全文，不绕过付费权限。

## License

Copyright (C) 2026 66666-design · **AGPL-3.0-or-later**（同 [cnki-citation](https://github.com/66666-design/cnki-citation)、[cnki-session](https://github.com/66666-design/cnki-session)）。
任何人修改后分发或部署为网络服务，须以同协议提供完整源码。
详见 [LICENSE](LICENSE) 或 https://www.gnu.org/licenses/agpl-3.0.html 。
