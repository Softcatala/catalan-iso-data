#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2015 Jordi Mas i Hernandez <jmas@softcatala.org>
# Copyright (c) 2020 Xavi Ivars <xavi.ivars@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import polib
import json
import re
import requests

EXTRA_639_1_DATA = "https://raw.githubusercontent.com/haliaeetus/iso-639/master/data/iso_639-2.json"

TEXTS = {
    "source": "Anglès",
    "target": "Català",
    "code": "Codi"
}

class Translation(dict):

    def __init__(self, source, target, code):
        dict.__init__(self)
        self["source"] = source
        self["target"] = target
        self["code"] = code

def _read_po_file(filename):
    input_po = polib.pofile(filename)
    translations = []

    for entry in input_po:
        if entry.translated() is False:
            continue

        m = re.search('(.*)for[ ](.*)', entry.comment, re.IGNORECASE)
        code = ''
        if m:
            code = m.group(2)

        translation = Translation(entry.msgid, entry.msgstr, code)
        translations.append(translation)

    return {
        "text": TEXTS,
        "data": translations
    }

def _save_file(filename, content):
    mode = 'w' if isinstance(content, str) else 'wb'

    with open(filename, mode) as f:
        f.write(content)

def _load_iso_files(filename):
    if filename is None:
        return None

    with open(filename) as json_data:
        data = json.load(json_data)

    return data

def _download_file(filename, source):
    r = requests.get(source)
    
    _save_file(filename, r.content)
    
    return filename

def _add_639_1(translations):

    _download_file("iso-639-1.json", EXTRA_639_1_DATA)
    data = open("iso-639-1.json")
    iso_639_1 = json.load(data)

    for translation in translations['data']:
        code = translation['code']
        if code in iso_639_1 and "639-1" in iso_639_1[code]:
            translation[code] = f'{code}, {iso_639_1[code]["639-1"]}'

def _enrich(key, translations):
    if key == "iso-639-3":
        _add_639_1(translations)
    

def main():

    iso_files = _load_iso_files('data.json')
    all = []

    for key in iso_files.keys():
        iso_file = iso_files[key]
        source = iso_file['source']

        translations = _read_po_file(source)
        _enrich(key, translations)

        _save_file(f'output/{key}.json', json.dumps(translations, indent=4))
        all.append(key)

    _save_file('output/index.json', json.dumps({"files": all}))

if __name__ == "__main__":
    main()
