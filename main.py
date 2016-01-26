#coding: utf-8

import sys
import os
import re
import shutil
import json
from string import Template

import evernote.edam.type.ttypes as Types
from evernote.api.client import EvernoteClient
import evernote.edam.userstore.constants as UserStoreConstants


#sys.exit()
with open('config.json') as json_file:
    config = json.load(json_file)

auth_token = config['auth_token']
guid = config['note_guid']

client = EvernoteClient(token=auth_token, sandbox=False)
note_store = client.get_note_store()
#Get the note to be updated using the note's guid http://dev.evernote.com/documentation/reference/NoteStore.html#Fn_NoteStore_getNote
note = note_store.getNote(guid, True, True, False, False)


text = note.content.split('<div>')

def files():
    return [f for f in os.listdir('.') if os.path.isfile(f) and f not in os.path.basename(__file__) and '.DS_Store' not in f]

print('Downloading videos...')
text.pop(0) # We remove the first element, as it is the evernote xml definition
for todo in text:
    if not '<en-todo checked="true"' in todo and 'http' in todo:
        items = todo.split(' ')
        for item in items:
            if 'youtu.be' in item or 'youtube.com' in item:
                    if not 'playlist' in item:
                        command = 'youtube-dl {0}'.format(item)
                        os.system(command)

                        videoID = item.rsplit('/', 1)[1]
                        _files = files()
                        didFind = False
                        for fileName in _files:
                            if videoID in fileName:
                                didFind = True
                                oldTodo = todo
                                _note = note_store.getNote(guid, True, True, False, False)
                                todo = todo.replace('checked="false"', 'checked="true"', 1)

                                #Regular expressions used to replicate ENML tags.  These same tags will be used to "rebuild" the note with the existing note metadata
                                xmlTag          = re.search('<\?xml.*?>', _note.content).group()
                                docTag          = re.search('<\!DOCTYPE.*?>', _note.content).group()
                                noteOpenTag     = re.search('<\s*en-note.*?>', _note.content).group()
                                noteCloseTag    = re.search('<\s*/en-note.*?>', _note.content).group()
                                breakTag        = '<br />'

                                #Rebuild the note using the new content
                                _content           =  _note.content.replace(xmlTag, '').replace(noteOpenTag, '').replace(noteCloseTag, '').replace(docTag, '').strip()
                                content = _content.replace(oldTodo, todo, 1)
                                template          =  Template ('$xml $doc $openTag $body $closeTag')
                                _note.content      =  template.substitute(xml=xmlTag,doc=docTag,openTag=noteOpenTag,body=content,closeTag=noteCloseTag)
                                #Update the note
                                client.get_note_store().updateNote(_note)
                        if not didFind:
                            sys.exit('ERROR: DIDNT FIND videoID in files')

# Rename files
print('Renaming downloaded files...')
for file in files():
    split_comps = file.rsplit('.', 1)
    filename = split_comps[0].rsplit('-', 1)[0]
    extension = split_comps[1]
    new_filename = '{}.{}'.format(filename, extension)
    os.rename(file, new_filename)

# Move files
print('Moving downloaded files to external drive...')
destination = '/Volumes/Data/Archive/YouTube/'
for file in files():
    shutil.move(file, destination)
