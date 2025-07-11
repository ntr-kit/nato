#!/bin/bash

# 仮想環境のパス
VENV_PATH="edge-venv"

# 仮想環境が存在しない場合は作成
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment..."
    python -m venv $VENV_PATH
else
    echo "Virtual environment already exists. Updating..."
fi

# 仮想環境をアクティベート
source $VENV_PATH/bin/activate

# pipを最新版にアップデート
echo "Updating pip..."
python -m pip install --upgrade pip

# 必要なパッケージをインストール
echo "Installing required packages..."
pip install -r requirements.txt

# スクリプトをsudoで実行
echo "Running script with sudo..."
sudo python edge_device.py
