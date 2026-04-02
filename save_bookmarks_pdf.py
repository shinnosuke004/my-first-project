#!/usr/bin/env python3
"""
Safari ブックマークの記事を PDF として保存するスクリプト

事前に必要なライブラリをインストール:
    pip install requests weasyprint
"""

import plistlib
import sys
import re
from pathlib import Path

import requests
from weasyprint import HTML


BOOKMARKS_PLIST = Path.home() / "Library" / "Safari" / "Bookmarks.plist"
OUTPUT_DIR = Path("pdfs")
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}


def read_safari_bookmarks(plist_path=BOOKMARKS_PLIST):
    """Safari の Bookmarks.plist からすべてのブックマークを取得する"""
    if not plist_path.exists():
        print(f"エラー: ブックマークファイルが見つかりません: {plist_path}")
        sys.exit(1)

    with open(plist_path, "rb") as f:
        data = plistlib.load(f)

    bookmarks = []
    _collect(data, bookmarks)
    return bookmarks


def _collect(node, result):
    """再帰的にブックマーク（URL）を収集する"""
    if not isinstance(node, dict):
        return
    if node.get("WebBookmarkType") == "WebBookmarkTypeLeaf":
        url = node.get("URLString", "")
        title = node.get("URIDictionary", {}).get("title", "") or url
        if url.startswith("http"):
            result.append({"title": title, "url": url})
    for child in node.get("Children", []):
        _collect(child, result)


def safe_filename(title, max_len=80):
    """タイトルをファイル名として使える形式に変換する"""
    name = re.sub(r'[\\/:*?"<>|]', "_", title)
    name = name.strip().strip(".")
    return name[:max_len] or "untitled"


def save_pdf(title, url, output_dir, index, total):
    """URL の内容を PDF として保存する"""
    print(f"[{index}/{total}] {title}")
    print(f"         {url}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()

        filename = safe_filename(title) + ".pdf"
        output_path = output_dir / filename

        # 重複ファイル名を避ける
        counter = 1
        while output_path.exists():
            output_path = output_dir / f"{safe_filename(title)}_{counter}.pdf"
            counter += 1

        HTML(string=resp.text, base_url=url).write_pdf(str(output_path))
        print(f"         -> 保存完了: {output_path.name}\n")
        return True

    except requests.RequestException as e:
        print(f"         ✗ 取得失敗: {e}\n")
    except Exception as e:
        print(f"         ✗ PDF変換失敗: {e}\n")
    return False


def select_bookmarks(bookmarks):
    """ブックマーク一覧を表示して、保存したいものを選択させる"""
    print("ブックマーク一覧:\n")
    for i, bm in enumerate(bookmarks, 1):
        print(f"  {i:>3}. {bm['title']}")
        print(f"       {bm['url']}")
    print()
    print("保存したいブックマークの番号を入力してください。")
    print("  例: 1 3 5   （スペース区切り）")
    print("  例: 2-6     （範囲指定）")
    print("  例: 1 3 7-10（組み合わせ）")
    print()

    while True:
        raw = input("番号 > ").strip()
        if not raw:
            print("番号を入力してください。")
            continue

        selected = set()
        try:
            for part in raw.split():
                if "-" in part:
                    start, end = part.split("-", 1)
                    selected.update(range(int(start), int(end) + 1))
                else:
                    selected.add(int(part))
        except ValueError:
            print("入力形式が正しくありません。数字またはハイフン区切りの範囲で入力してください。\n")
            continue

        invalid = [n for n in selected if n < 1 or n > len(bookmarks)]
        if invalid:
            print(f"範囲外の番号があります: {sorted(invalid)}（1〜{len(bookmarks)} で入力してください）\n")
            continue

        chosen = [bookmarks[n - 1] for n in sorted(selected)]
        print(f"\n以下の {len(chosen)} 件を保存します:")
        for bm in chosen:
            print(f"  - {bm['title']}")
        print()
        confirm = input("よろしいですか？ [y/N] > ").strip().lower()
        if confirm == "y":
            return chosen
        print()


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("Safari ブックマークを読み込み中...\n")
    bookmarks = read_safari_bookmarks()

    if not bookmarks:
        print("ブックマークが見つかりませんでした。")
        sys.exit(0)

    print(f"{len(bookmarks)} 件のブックマークが見つかりました。\n")
    print("-" * 60 + "\n")

    chosen = select_bookmarks(bookmarks)

    print("-" * 60)
    print(f"PDFの保存先: {OUTPUT_DIR.resolve()}\n")

    success = 0
    for i, bm in enumerate(chosen, 1):
        if save_pdf(bm["title"], bm["url"], OUTPUT_DIR, i, len(chosen)):
            success += 1

    print("-" * 60)
    print(f"\n完了: {success}/{len(chosen)} 件を PDF として保存しました。")
    print(f"保存先: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
