## Overview

Fletとspacy、ginzaの技術検証のために作ったPythonデスクトップアプリです。
CSVを読み取り、カラムを選択すると、指定したカラムの人名やメールアドレス、電話番号をマスクします。

## Dependencies
- [Task](https://taskfile.dev/) - 開発コマンド用のタスクランナー
- [uv](https://github.com/astral-sh/uv) - Pythonパッケージ管理に必要


## セットアップ
必要な依存のインストール
```
uv sync
```

## アプリの実行

以下のコマンドを実行すると自動でアプリが立ち上がります。

```
uv run flet run
```

## アプリのビルド
アプリケーションのビルドは[pyinstaller](https://github.com/pyinstaller/pyinstaller)を利用します。
pyinstallerではいくつかの方法がありますが、ここでは起動速度を重視し`--onedir`を採用しています。

以降の項目にて、各OSでのビルドコマンドを示します。ビルドが完了すると`dist`ディレクトリにアプリケーションが生成されます。

### macOS

依存も含めて変更する必要がある場合は、以下のコマンドのように直接パラメータ指定すると良い。
```bash
task full_mac_build
```

依存の変更等がない場合は、specファイルを起点にバンドルすると良い。
```bash
task mac_build
```

### Windows

依存も含めて変更する必要がある場合は、以下のコマンドのように直接パラメータ指定すると良い。
```bash
task full_win_build
```

依存の変更等がない場合は、specファイルを起点にバンドルすると良い。
```bash
task win_build
