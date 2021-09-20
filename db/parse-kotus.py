import xml.etree.ElementTree as ET
import os

mytree = ET.parse('./kotus-sanalista_v1/kotus-sanalista_v1.xml')
myroot = mytree.getroot()
word_elems = myroot.findall('.//s')

print(len(word_elems))

words = []
for word_elem in word_elems:
  text = word_elem.text.lower()
  if 'ari' in text:
    words.append(text)


print(len(words))

words = list(set(words))

print(len(words))

target = './db/init_words.sql'

if os.path.exists(target):
  os.remove(target)

last = len(words) - 1

with open(target, 'a') as word_sql:
  word_sql.write('INSERT INTO ari_word (word, from_dictionary)\n')
  word_sql.write('VALUES\n')
  for i, word in enumerate(words):
    if i < last:
      word_sql.write("('{}', TRUE),\n".format(word))
    else:
      word_sql.write("('{}', TRUE)\n".format(word))
  word_sql.write('ON CONFLICT DO NOTHING;\n')
