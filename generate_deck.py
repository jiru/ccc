#!/usr/bin/env python

import genanki
import csv
from sys import argv
from optparse import OptionParser
from glob import glob
import os
import sqlite3
import zipfile

# Pseudorandom IDs generated using
# import random; random.randrange(1 << 30, 1 << 31)
pinyin_deck_id = 1727536177
pinyin_hanzi_id = 1883864453
model_id = 1858604882

class CCCNote(genanki.Note):
  @property
  def guid(self):
    # Use hanzi + part of speech + lesson as unique identifier.
    # Because there are some (hanzi, part of speech) duplicates,
    # and some (hanzi + lesson) duplicates, too
    return genanki.guid_for(self.fields[0], self.fields[3], self.fields[4])

def read_file(file):
  with open(file, 'r') as f:
    return f.read()

def sorted_glob(pattern):
  result = glob(pattern)
  result.sort()
  return result

def add_pos_tags(tags, pos):
  if 'V' in pos:
    tags.append("Verb")
  if 'N' in pos:
    tags.append("Noun")
  if 'M' in pos:
    tags.append("Measure-word")
  if 'Adv' in pos:
    tags.append("Adverb")
  if 'Ptc' in pos:
    tags.append("Particle")
  if 'Conj' in pos:
    tags.append("Conjunction")
  if 'Prep' in pos:
    tags.append("Preposition")

def add_lesson_tags(tags, lesson):
   tags.append("Book-" + lesson[1:2])
   tags.append("Lesson-" + lesson[3:])

def add_notes(deck, model, tsv_file, audios_all_books):
  audios_by_lesson = {}
  book = 1
  for audios_one_book in audios_all_books:
    if audios_one_book:
      dir_number = 1
      lesson_dirs = sorted_glob(audios_one_book + "/*/")
      for lesson_dir in lesson_dirs:
        lesson = int(dir_number/2+0.5)
        sublesson = "I"*((dir_number-1)%2+1)
        fq_lesson = f"B{book}L{lesson:02}-{sublesson}"
        audios_by_lesson[fq_lesson] = sorted_glob(lesson_dir + "/*")
        dir_number = dir_number + 1
    book = book + 1

  added_audios = []
  added_lessons = {}
  with open(tsv_file) as ccc:
    deckreader = csv.reader(ccc, delimiter='\t')
    for row in deckreader:
      try:
        fields = row[0:5] + ['']
        lesson = row[4]
        tags = row[5].split(' ')
      except IndexError:
        line = deckreader.line_num
        print(f"Error parsing '{tsv_file}' at line {line}")
        exit(1)

      add_pos_tags(tags, row[3])
      add_lesson_tags(tags, lesson)

      try:
        audio = audios_by_lesson[lesson].pop(0)
        added_audios.append(audio)
        audio = os.path.basename(audio)
        fields[5] = f"[sound:{audio}]"
      except IndexError:
        print(f"Warning: missing audio for lesson {lesson}, vocab {row[0:3]}")
      except KeyError:
        pass

      added_lessons[lesson] = None
      note = CCCNote(model=model, fields=fields, tags=tags)
      deck.add_note(note)

  for lesson in added_lessons.keys():
    if (lesson in audios_by_lesson and len(audios_by_lesson[lesson]) > 0):
      print(f"Warning: unassigned audios for lesson {lesson}:")
      for audio in audios_by_lesson[lesson]:
        print("  " + audio)

  return added_audios

def gen_model(audios_all_books):
  script = '\n<script>\n' \
        + read_file('colorize_hanzi.js') \
        + '\n</script>'
  return genanki.Model(
    model_id,
    'Chinese vocab',
    fields=[
      {"font": "Arial", "name": "Hanzi"},
      {"font": "Arial", "name": "Pinyin"},
      {"font": "Arial", "name": "English"},
      {"font": "Arial", "name": "Part of speech"},
      {"font": "Arial", "name": "Lesson"},
      {"font": "Arial", "name": "Audio"},
    ],
    templates=[
      {
        'name': '中->英',
        'qfmt': read_file('tmpl.eng.qfmt.html'),
        'afmt': read_file('tmpl.eng.afmt.html') + script,
      },
      {
        'name': '英->中',
        'qfmt': read_file('tmpl.cmn.qfmt.html'),
        'afmt': read_file('tmpl.cmn.afmt.html') + script,
      },
    ],
    css=read_file('tmpl.css'),
  )

def assign_reverse_cards_to_deck_from_ankicol(ankicol_file, deck_id):
  con = sqlite3.connect(ankicol_file)
  cur = con.cursor()
  cur.execute(f"update cards set did = {deck_id} where ord = 1")
  con.commit()
  con.close()

def assign_reverse_cards_to_deck(apkg_file, deck_id):
  new_apkg_file = apkg_file + '.tmp'
  with zipfile.ZipFile(apkg_file, 'r') as apkg, zipfile.ZipFile(new_apkg_file, 'w') as new_apkg:
    for apkg_info_file in apkg.infolist():
      with apkg.open(apkg_info_file) as apkg_info:
        file_contents = apkg_info.read()
        if apkg_info.name == 'collection.anki2':
          tmp_ankicol_file = './' + apkg_info.name
          with open(tmp_ankicol_file, 'wb') as tmp_ankicol:
            tmp_ankicol.write(file_contents)
          assign_reverse_cards_to_deck_from_ankicol(tmp_ankicol_file, deck_id)
          with open(tmp_ankicol_file, 'rb') as tmp_ankicol:
            new_apkg.writestr(apkg_info.name, tmp_ankicol.read())
          os.remove(tmp_ankicol_file)
        else:
          new_apkg.writestr(apkg_info.name, file_contents)
  os.replace(new_apkg_file, apkg_file)

def compile_deck(output_file, audios_all_books):
  my_pinyin_deck = genanki.Deck(pinyin_deck_id, '當代中文課程::拼音')
  my_hanzi_deck = genanki.Deck(pinyin_hanzi_id, '當代中文課程::漢字')
  my_model = gen_model(audios_all_books)
  added_audios = add_notes(my_pinyin_deck, my_model, 'ccc.tsv', audios_all_books)

  my_package = genanki.Package([my_pinyin_deck, my_hanzi_deck])
  my_package.media_files = added_audios
  my_package.write_to_file(output_file)
  assign_reverse_cards_to_deck(output_file, pinyin_hanzi_id)

def run():
  total_books = 6
  parser = OptionParser(usage="Usage: %prog [options] <output_deck.apkg>")
  for i in range(1, total_books+1):
    parser.add_option(f"", f"--audio-{i}", dest=f"audio{i}", metavar="DIR",
                      help=f"get audio files of book {i} from subdirectories of DIR")
  (options, args) = parser.parse_args()

  if len(args) != 1:
    parser.error("incorrect number of arguments")

  audios = [getattr(options, f"audio{i}") for i in range(1, total_books+1)]
  compile_deck(args[0], audios)

if __name__ == "__main__":
  run()
