# -*- coding: utf-8 -*-
# cnki-search — 知网(CNKI)论文检索 CLI：16字段/5排序/专业检索表达式
# Copyright (C) 2026 66666-design
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# 引文导出见姊妹仓 cnki-citation（https://github.com/66666-design/cnki-citation）。
"""
用法:
  python cnki_search.py search 大语言模型                       # 按主题搜
  python cnki_search.py search 大语言模型 --field AU --sort cited
  python cnki_search.py search 碳排放 --pages 3 --json out.json  # 多页
  python cnki_search.py expert "TI='知识图谱' AND AU='刘峤'"      # 专业检索表达式
  python cnki_search.py search 大语言模型 --start-page 3 --pages 2  # 取第 3-4 页

字段(--field): SU=主题(默认) TKA=篇关摘 TI=篇名 KY=关键词 FT=全文 AU=作者
  FI=第一作者 RP=通讯作者 AF=作者单位 FU=基金 AB=摘要 CO=小标题
  RF=参考文献 CLC=分类号 LY=文献来源 DOI=DOI
排序(--sort): relevance=相关度 time=发表时间(默认) cited=被引 download=下载 overall=综合
退出码: 0 成功; 2 验证码未通过; 3 无结果; 1 其他错误
"""
import argparse
import json
import sys
from pathlib import Path

from cnki_session import CNKI, FIELD_LABEL, SORT_CODES, CaptchaError


def main():
    ap = argparse.ArgumentParser(description="知网论文检索（16字段/5排序/专业检索）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_s = sub.add_parser("search", help="按关键词+字段检索")
    p_s.add_argument("keyword")
    p_s.add_argument("--pages", type=int, default=1)
    p_s.add_argument("--field", choices=list(FIELD_LABEL), default="SU")
    p_s.add_argument("--sort", choices=list(SORT_CODES), default="time")
    p_s.add_argument("--start-page", type=int, default=1, dest="start_page",
                     help="从第几页开始取（1 起）；与 --pages 组合定义页码范围")
    p_s.add_argument("--json", default="")

    p_e = sub.add_parser("expert", help="专业检索：知网检索表达式透传")
    p_e.add_argument("expr")
    p_e.add_argument("--pages", type=int, default=1)
    p_e.add_argument("--sort", choices=list(SORT_CODES), default="time")
    p_e.add_argument("--start-page", type=int, default=1, dest="start_page")
    p_e.add_argument("--json", default="")

    args = ap.parse_args()
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    cnki = CNKI(state_file=Path(__file__).parent / "_cnki_state.json")
    try:
        if args.cmd == "expert":
            rows = cnki.expert_search(args.expr, args.pages, args.sort, args.start_page)
        else:
            rows = cnki.search(args.keyword, args.pages, args.field, args.sort, args.start_page)
        if not rows:
            print("无结果", file=sys.stderr)
            return 3
        for r in rows:
            print(f"[{r['n']}] {r['title']} | {r['authors']} | {r['journal']} | "
                  f"{r['date']} | 被引 {r['cited']} | {r['db']}")
        if args.json:
            Path(args.json).write_text(
                json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
        cnki.save_state()
        return 0
    except CaptchaError as e:
        print(f"验证失败: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
