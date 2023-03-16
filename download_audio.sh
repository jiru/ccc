#!/bin/bash

set -e

archives=(
  http://mtc.ntnu.edu.tw/upload_files/book/A%20Course%20in%20Contemporary%20Chinese%201%20-%20Textbook%20Audio%20Files.rar
  http://mtc.ntnu.edu.tw/upload_files/book/A%20Course%20in%20Contemporary%20Chinese%202%20-%20Textbook%20Audio%20Files.rar
  http://mtc.ntnu.edu.tw/upload_files/book/A%20Course%20in%20Contemporary%20Chinese%203%20-%20Textbook%20Audio%20Files.rar
  http://mtc.ntnu.edu.tw/upload_files/book/A%20Course%20in%20Contemporary%20Chinese%204%20-%20Textbook%20Audio%20Files.rar
  http://mtc.ntnu.edu.tw/upload_files/book/A%20Course%20in%20Contemporary%20Chinese%205%20-%20Textbook%20Audio%20Files.rar
  http://mtc.ntnu.edu.tw/upload_files/book/A%20Course%20in%20Contemporary%20Chinese%206%20-%20Textbook%20Audio%20Files.rar
)

sha1sums=(
  a4bed58618f0425eafd5ab031909e031e7a6bbf5
  dae3a8c8c3fb7e78f1ede3a671940237da8f5a9a
  9423150fba32c1a3ae5d65c83d6e1ce953ac616f
  04c97d1693696e5df41fdcd275df96fae4cc7e18
  29254c66e122c538a8f494e99409d7265abe041b
  0e4a4607ac8d59c0e4ee3578f148ca225cf22327
)

for book in $(seq 1 "${#archives[@]}"); do
  let i=book-1 || true
  url="${archives[$i]}"
  filename="A Course in Contemporary Chinese $book - Textbook Audio Files.rar"
  wget --continue "$url" -O "$filename"
  sha1sum="${sha1sums[$i]}"
  sha1sum -c <(echo "$sha1sum  $filename")
done

for book in $(seq 1 "${#archives[@]}"); do
  filename="A Course in Contemporary Chinese $book - Textbook Audio Files.rar"
  unrar x -y "$filename"
done
