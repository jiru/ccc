#!/usr/bin/env python

import genanki
import csv
from sys import argv

# Pseudorandom IDs generated using
# import random; random.randrange(1 << 30, 1 << 31)
deck_id = 1727536177
model_id = 1858604882

class CCCNote(genanki.Note):
  @property
  def guid(self):
    # Use hanzi + part of speech as unique identifier
    return genanki.guid_for(self.fields[0], self.fields[3])

def read_file(file):
  with open(file, 'r') as f:
    return f.read()

def add_notes(deck, model, tsv_file):
  with open(tsv_file) as ccc:
    deckreader = csv.reader(ccc, delimiter='\t')
    for row in deckreader:
      note = CCCNote(
        model=model,
        fields=row[0:5],
        tags=row[5].split(' ')
      )
      deck.add_note(note)

def gen_model():
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

def compile_deck(output_file):
  my_deck = genanki.Deck(deck_id, '當代中文課程')
  my_model = gen_model()
  add_notes(my_deck, my_model, 'ccc.tsv')
  genanki.Package(my_deck).write_to_file(output_file)

def run():
  try:
    output_file = argv[1]
  except IndexError:
    print(f"Usage: {argv[0]} <output_deck.apkg>")
  else:
    compile_deck(output_file)

run()
