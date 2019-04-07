# parody
## 1. 概要
- これは `python3` で記述された，駅名替え歌などの替え歌を自動で作詞するプログラムです。
- 現在は，駅名替え歌のみに対応しています。
- 動作は `macOS 10.13.6`, `python3.7.3` で確認しています。その他の環境での動作は保証できません。Mac または Ubuntu 上での実行を推奨します。
- ### 大変申し訳ありませんが， **駅データの準備中のため，このパッケージはまだ使用できません** 。

## 2. 必要なパッケージのインストール，データの用意
### 2.1 パッケージの用意
- このリポジトリを次のコマンドでクローンします (例えば，ホームディレクトリ `~/` の直下など)。
  - `git clone https://github.com/Ryo-Kashimura/parody`
- `parody/bin/requirements.txt` に記述されたパッケージを事前にインストールする必要があります。
- `pip -r ./bin/requirements.txt` 等のコマンドでインストールできます。
### 2.2 駅名データの用意
- ### **ただいま編集中**

## 3. 使い方
### 3.1 元の歌の歌詞の準備
- 替え歌の元となる歌詞を **ひらがな** で `.txt` ファイルに記述し， `parody/data/lyrics/` に置いてください。
- 歌詞の記述の際，歌詞を文節に区切ってそれぞれの間に半角スペースを挟むことを推奨します。
### 3.2 実行
1. ディレクトリ `parody/bin/` (`.py` ファイルのあるディレクトリ) に移動
  - 例) `cd ~/parody/bin`
2. `python ./search_station_path.py --verbose --lyrics_filename 元の歌詞のファイル名 替え歌のファイル名` を実行 (20 - 30 分ほどかかるかもしれません)
  - 例) `python ./search_station_path.py --verbose --lyrics_filename 故郷.txt station_parody_故郷.tsv`
  - 元の歌詞のファイルは `.txt` ファイル，替え歌のファイルは `.tsv` ファイルである必要があります。
  - 替え歌のファイルはテキストエディタでも閲覧できますが，Microsoft Excel または Numbers などのアプリケーションの方が見やすいです。
### 3.3 オプション機能
- 実行中に替え歌の進捗を見たい場合は実行コマンドに `--verbose` オプションをつける必要があります。
- 元の歌詞は `.txt` ファイルとして用意する他に， `--lyrics` オプションを使うこともできます。
  - 例) `python ./search_station_path.py --verbose --lyrics 'うさぎ おいし かの やま' example_parody.tsv`
- デフォルトでは，同じ駅を重複して使用しません。重複を許す場合は， `parody/data/hparams/hparams_v1.json` を編集し， `"repeated": false` を `"repeated": true` に変更してください。
- デフォルトでは，廃止された駅を使用しません。廃止駅を使用する場合は， `parody/data/hparams/hparams_v1.json` を編集し， `"no_deprecated": true` を `"no_deprecated": false` に変更してください。
  
## 4. 注意事項
- 現在のところ，元となる歌詞は **すべてひらがなで** 記述する必要があります。
- 入力となる，元の歌詞に改行を挟むと，出力となる替え歌の歌詞の単語は必ずその場所で分割されます。
- 入力となる，元の歌詞に半角スペースを挟むと，出力となる替え歌の歌詞の単語は分割されやすいです (確実ではありません)。
- 入力の歌詞に関しては， **全角スペースを含めて，ひらがな以外の文字には一切対応しておりません** ので，ご注意ください。
