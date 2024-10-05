import re
import os
import shutil
import logging
import traceback
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog as fg

name_parts_regex = r'(^.*(?=\(\d+\)\.(?!.*\.))|^.*(?=\(\d+\)$)|^.*(?=\.)|^.*)(\((\d+)\))?(\..+)?'

#probably should reformat this with oop architechture - a task for the future

def copy_by_match(method: str):
  # dependency injection????
  seen = {}

  for entry_name in os.listdir(to_dir.get()):
    full_entry_path = os.path.join(to_dir.get(), entry_name)

    if os.path.isdir(full_entry_path):
      continue

    groups = re.search(name_parts_regex, entry_name).groups(0)
    original_name = groups[0] + groups[3]
    occurences = int(groups[2])

    if original_name in seen and occurences <= seen[original_name]:
      continue
    
    seen[original_name] = occurences
  
  if not os.path.exists(to_dir.get()):
    os.mkdir(to_dir.get())

  copy_recursively(pattern_entry.get(), from_dir.get(), seen, method)

def copy_recursively(pattern: str, directory: str, seen: dict, method: str):
  for entry_name in os.listdir(directory):
    full_entry_path = os.path.join(directory, entry_name)

    # if it is a directory, go deeper recursively
    if os.path.isdir(full_entry_path):
      copy_recursively(pattern, full_entry_path, seen, method)
      return

    result = None
    
    # this is what we can do as dependency injection probably
    try:
      match method:
        case 'name':
          result = search_by_name(entry_name, pattern)
        case 'contents':
          result = search_by_contents(full_entry_path, pattern)
        case _:
          raise Exception('No such method: ' + method)
    except Exception:
      logging.error(traceback.format_exc())

    if result:
      to_path = os.path.join(to_dir.get(), entry_name)

      if entry_name in seen:
        seen[entry_name] += 1

        [name, extension] = entry_name.rsplit('.', 1)
        to_path = os.path.join(to_dir.get(), name + '({})'.format(seen[entry_name]) + '.' + extension)
      else:
        seen[entry_name] = 0

      shutil.copy(full_entry_path, to_path)

def search_by_contents(path: str, pattern: str):
  with open(path, 'r') as f:
    for i, line in enumerate(f):
      if re.search(pattern, line):
        print(i, line)

        return True
    
    return False
  
def search_by_name(name: str, pattern: str):
  return True if re.search(pattern, name) else False
 
window = Tk()

from_dir = StringVar()
from_dir.set('C:/Users/user/Desktop/portfolio')
to_dir = StringVar()
to_dir.set('C:/Users/user/Desktop/thing')

pattern_label = Label(text='Match')
pattern_label.pack()
pattern_entry = Entry(width=70)
pattern_entry.pack()
copy_button = Button(text='Copy files with matching name', command=lambda: copy_by_match('name'))
copy_button.pack()
copy_by_contents_button = Button(text='Copy files with matching contents', command=lambda: copy_by_match('contents'))
copy_by_contents_button.pack()

from_dir_button = Button(text='Folder to copy from', command=lambda: from_dir.set(fg.askdirectory()))
from_dir_button.pack()
from_dir_entry = Entry(width=70, textvariable=from_dir)
from_dir_entry.pack()

to_dir_button = Button(text='Folder to copy to', command=lambda: to_dir.set(fg.askdirectory()))
to_dir_button.pack()
to_dir_entry = Entry(width=70, textvariable=to_dir)
to_dir_entry.pack()

window.mainloop()