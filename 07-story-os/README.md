# Story OS

創作(物語制作)で使っているプロンプト・ルール一式。iOSファイルアプリで手動保存していたmdファイルを、git管理に移行する試験運用。

## 構成

- `story-os-file.md` : Story OSファイル(第一原理・16ビート・ゲームエンジンなど、物語理論の本体・語彙カタログ)。旧ファイル名: Story OS ファイル_v9.md
- `story-os-prompt.md` : Story OSプロンプト(I/O契約・PHASE手順)。旧ファイル名: story os プロンプト_v9.md
- `works/` : 個別作品ごとの設定資料(soft)。OSファイル・プロンプトの内容を、各作品に当てはめる際に使う
  - `works/bb/soft.md` : BBの設定資料。旧ファイル名: BB soft_v7.md
  - `works/bb/sub-soft.md` : BBの補助設定資料。旧ファイル名: BB sub soft_v2.md
  - `works/st/soft.md` : STの設定資料。旧ファイル名: ST soft_v7.md
  - `works/st/sub-soft.md` : STの補助設定資料。旧ファイル名: ST sub soft_v2.md
  - `works/hs/soft.md` : HSの設定資料。旧ファイル名: HS soft_v7.md

「OS」(story-os-file.md / story-os-prompt.md)が全作品共通のベース、`works/`配下がそれぞれの作品固有の設定という位置づけ。

## 運用ルール(mj汎用プロンプトと同じ考え方)

- ファイル名にバージョン番号を付けない。中身の変更は普通に上書き保存(コミット)していけば、履歴はgitが持つ
- 過去のバージョン(v3〜v8など)は、今回は移行対象外。iOSファイルアプリ側にそのまま残している

## 由来

2026-09、iOSファイルアプリ内「Story OS_v9」フォルダから移行。移行時点で「現在使っている版」として指定されたもの。
