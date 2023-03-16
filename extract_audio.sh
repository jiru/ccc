#!/bin/bash

print_silences() {
  ffmpeg -nostdin -i "$1" -filter_complex "[0:a]silencedetect=n=-70dB:d=1.3[outa]" -map [outa] -f s16le -y /dev/null 2>&1
}

split_by_silence() {
  local ext output_file book_number="$1" input_file="$2" output_dir="$3"

  case "$book_number" in
    5) split_start=2 ;;
    *) split_start=1 ;;
  esac

  ext=${input_file/*\./}
  output_file=$output_dir/B$book_number.${input_file/*\//}
  output_file=${output_file%.*}
  print_silences "$input_file" \
    | perl -ne '
      INIT { printf "set -e\n"; $ss=0; $se=0; $margin=0.25; }
      if (/silence_start: (\S+)/) {
        $ss=$1;
        if ($ctr >= '"$split_start"') {
          printf "ffmpeg -nostdin -i \"'"$input_file"'\" -ss %f -t %f -c copy -vn -sn -dn -y \"'"$output_file"'.%03d.'$ext'\"\n", $se-$margin, ($ss-$se)+$margin*2, $ctr;
        }
        $ctr+=1;
      }
      if (/silence_end: (\S+)/) {
        $se=$1;
      }' \
    | bash -x
    if [ $? -ne 0 ] || ! find "$output_dir" -type f | grep -q .; then
      echo "Unable to split file '$input_file' by silence"
      exit 1
    fi
}

get_spectrum_entropy() {
  ffmpeg -nostdin -loglevel quiet "$@" -af aspectralstats,ametadata=print:file=- -f null - 2>&1 | grep -o 'entropy=.*' | cut -d= -f2
}

is_bell_sound() {
  local numbers sum n avg1000

  numbers=$(get_spectrum_entropy "$@")
  sum=$(bc <<<"`echo $numbers | sed 's,\S\+,(\0),g;s,e-,*10^-,g' | tr ' ' +`")
  n=$(echo $numbers | tr ' ' '\n' | wc -l)
  avg1000=$(bc <<<"$sum*1000/$n")
  [ "$avg1000" -le 28 ] && return 0 || return 1
}

get_vocab_start_pos() {
  local margin="0.25" input_file="$1" skip="$2"

  start=$(ffmpeg -nostdin -i "$input_file" -af silencedetect=d=0.15:noise=-35dB -f null - 2>&1 \
    | grep -om $skip 'silence_end: [^ ]\+' \
    | tail -n 1 \
    | grep -o '[0-9.]\+'
  )
  start=$(awk "BEGIN {print $start-$margin}")
  echo "$start"
}

remove_prefix() {
  local book_number="$1" input_file="$2"
  local skip=2 duration start ext output_file

  start=$(get_vocab_start_pos "$input_file" "$skip")
  if is_bell_sound -to "$start" -i "$input_file"; then
    if [ "$book_number" -eq 5 ]; then
      # skip the whole file as it just contains "課文一" phrase
      rm "$input_file"
      return
    fi
    let skip++ # skip bell sound
    start=$(get_vocab_start_pos "$input_file" "$skip")
  fi
  ext=${input_file/*\./}
  output_file="$input_file".tmp.$ext
  ffmpeg -nostdin -ss "$start" -i "$input_file" -c copy -y "$output_file"

  # Check if result looks okay
  duration=$(ffprobe -i "$output_file" -show_entries format=duration -v quiet -of csv="p=0")
  if awk "BEGIN { if ($duration < 0.5) { print \"fail\" }}" | grep -q fail; then
    echo "Failed to remove prefix from '$input_file': truncated file way too short"
    exit 1
  else
    mv "$output_file" "$input_file"
  fi
}

count_silences() {
  print_silences "$1" | grep -c silence_duration:
}

find_vocab_chaps() {
  local book_number="$1" output_basedir="$2"
  local vocab_files chapfile chapfiles lesson lessons

  case "$book_number" in
    5|6) vocab_files=2367 ;;
    *)   vocab_files=24 ;;
  esac

  lessons=$(ls -1 "$output_basedir"/*-0[$vocab_files].??? | sed 's,.*/,,;s/-.*//' | uniq)
  for lesson in $lessons; do
    chapfiles=("$output_basedir"/$lesson-0[$vocab_files].???)
    if [ "${#chapfiles[@]}" -gt 2 ]; then
      for chapfile in "${chapfiles[@]}"; do
        echo $(count_silences "$chapfile") $chapfile
      done \
        | sort -n \
        | tail -n 2 \
        | cut -d' ' -f 2-
    else
      for chapfile in "${chapfiles[@]}"; do
        echo "$chapfile"
      done
    fi
  done
}

if [ $# -ne 2 ]; then
  echo "Usage: $0 <book-number> <chapter-audio-directory>"
  echo "Example: $0 1 '當代中文課程 第一冊 課本/'"
  exit 1
fi

book_number="$1"
output_basedir="$2"
while [ "${output_basedir}" != "${output_basedir%/}" ]; do
  output_basedir=${output_basedir%/};
done

while read -r chapter; do
  output_dir=${chapter/.*\//}.split
  rm -rf "$output_dir"
  mkdir -p "$output_dir"
  split_by_silence "$book_number" "$chapter" "$output_dir"

  for file in "$output_dir"/*; do
    remove_prefix "$book_number" "$file"
  done
done < <(find_vocab_chaps "$book_number" "$output_basedir")
