#!/usr/bin/env python3
"""
指定したURLの記事を Notion ページに保存するスクリプト

使い方:
    python save_to_notion.py
"""

import os
import re
import sys
import requests
from bs4 import BeautifulSoup

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
PARENT_PAGE_ID = os.environ.get("NOTION_PAGE_ID", "")
NOTION_VERSION = "2022-06-28"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
}
FETCH_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

# Notion ブロック1件あたりの最大文字数
BLOCK_MAX_CHARS = 1900


def fetch_article(url):
    """URLから記事のタイトルと本文テキストを取得する"""
    resp = requests.get(url, headers=FETCH_HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # タイトル
    title = ""
    if soup.title:
        title = soup.title.string or ""
    title = title.strip() or url

    # 不要なタグを除去して本文を抽出
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()

    paragraphs = []
    for p in soup.find_all(["p", "h1", "h2", "h3", "h4", "li"]):
        text = p.get_text(separator=" ", strip=True)
        if len(text) > 30:
            paragraphs.append(text)

    return title, paragraphs


def make_blocks(paragraphs):
    """段落リストを Notion ブロックのリストに変換する（2000文字制限対応）"""
    blocks = []
    for para in paragraphs:
        # 長い段落は分割する
        chunks = [para[i:i + BLOCK_MAX_CHARS] for i in range(0, len(para), BLOCK_MAX_CHARS)]
        for chunk in chunks:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": chunk}}]
                }
            })
    return blocks


def create_notion_page(title, url, blocks, parent_id):
    """Notion にページを作成する（ブロックを100件ずつ追加）"""
    # ページ作成（最初の100ブロックまで）
    payload = {
        "parent": {"page_id": parent_id},
        "properties": {
            "title": {
                "title": [{"text": {"content": title[:255]}}]
            }
        },
        "children": blocks[:100]
    }
    resp = requests.post(
        "https://api.notion.com/v1/pages",
        headers=HEADERS,
        json=payload
    )
    resp.raise_for_status()
    page_id = resp.json()["id"]

    # 100件を超えるブロックは追記
    for i in range(100, len(blocks), 100):
        batch = blocks[i:i + 100]
        requests.patch(
            f"https://api.notion.com/v1/blocks/{page_id}/children",
            headers=HEADERS,
            json={"children": batch}
        )

    return page_id


def create_folder_page(folder_name, parent_id):
    """フォルダ用のサブページを作成する（既存チェックなし）"""
    payload = {
        "parent": {"page_id": parent_id},
        "properties": {
            "title": {
                "title": [{"text": {"content": folder_name}}]
            }
        }
    }
    resp = requests.post(
        "https://api.notion.com/v1/pages",
        headers=HEADERS,
        json=payload
    )
    resp.raise_for_status()
    return resp.json()["id"]


def main():
    if not NOTION_TOKEN or not PARENT_PAGE_ID:
        print("エラー: NOTION_TOKEN と NOTION_PAGE_ID を環境変数に設定してください。")
        sys.exit(1)

    print("=== Notion 記事保存ツール ===\n")
    folder_name = input("フォルダ名（Notionのサブページ名）を入力してください: ").strip()
    if not folder_name:
        folder_name = "保存した記事"

    print("\n保存したいURLを1行ずつ入力してください。")
    print("入力が終わったら空行を入力してEnterを押してください。\n")

    urls = []
    while True:
        url = input("URL > ").strip()
        if not url:
            break
        if url.startswith("http"):
            urls.append(url)
        else:
            print("  ※ http から始まるURLを入力してください。")

    if not urls:
        print("URLが入力されませんでした。終了します。")
        sys.exit(0)

    print(f"\n{len(urls)} 件を「{folder_name}」フォルダに保存します。\n")
    confirm = input("よろしいですか？ [y/N] > ").strip().lower()
    if confirm != "y":
        print("キャンセルしました。")
        sys.exit(0)

    print(f"\nNotion にフォルダページ「{folder_name}」を作成中...")
    folder_id = create_folder_page(folder_name, PARENT_PAGE_ID)
    print(f"  -> 作成完了\n")

    success = 0
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] {url}")
        try:
            title, paragraphs = fetch_article(url)
            print(f"  タイトル: {title}")
            blocks = make_blocks(paragraphs)
            create_notion_page(title, url, blocks, folder_id)
            print(f"  -> Notion に保存完了\n")
            success += 1
        except Exception as e:
            print(f"  ✗ 失敗: {e}\n")

    print(f"完了: {success}/{len(urls)} 件を Notion に保存しました。")


if __name__ == "__main__":
    main()
