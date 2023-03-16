#!/bin/bash

set -e

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <output.apkg>"
  exit 1
fi

./download_audio.sh

./extract_audio.sh 1 '當代中文課程 第一冊 課本/'
./extract_audio.sh 2 '當代中文課程 第二冊 課本/'
./extract_audio.sh 3 '當代中文課程 第三冊 課本/'
./extract_audio.sh 4 '當代中文課程 第四冊 課本/'
./extract_audio.sh 5 '當代中文課程 第五冊 課本/'
./extract_audio.sh 6 '當代中文課程 第六冊 課本/'

./generate_deck.py \
  --audio-1='當代中文課程 第一冊 課本/' \
  --audio-2='當代中文課程 第二冊 課本/' \
  --audio-3='當代中文課程 第三冊 課本/' \
  --audio-4='當代中文課程 第四冊 課本/' \
  --audio-5='當代中文課程 第五冊 課本/' \
  --audio-6='當代中文課程 第六冊 課本/' \
  "$1"
