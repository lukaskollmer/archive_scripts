#coding: utf-8

import sys
import os
import re
import shutil
import json
import utils
import subprocess
from string import Template

import evernote.edam.type.ttypes as Types
from evernote.api.client import EvernoteClient
import evernote.edam.userstore.constants as UserStoreConstants

note_store = None

def replaceInNote(originalText, replacementText, max=-1):
    _note = note_store.getNote(guid, True, True, False, False)

    #Regular expressions used to replicate ENML tags.  These same tags will be used to "rebuild" the note with the existing note metadata
    xmlTag          = re.search('<\?xml.*?>', _note.content).group()
    docTag          = re.search('<\!DOCTYPE.*?>', _note.content).group()
    noteOpenTag     = re.search('<\s*en-note.*?>', _note.content).group()
    noteCloseTag    = re.search('<\s*/en-note.*?>', _note.content).group()
    breakTag        = '<br />'

    #Rebuild the note using the new content
    _content           =  _note.content.replace(xmlTag, '').replace(noteOpenTag, '').replace(noteCloseTag, '').replace(docTag, '').strip()
    content = _content.replace(originalText, replacementText, max)
    template          =  Template ('$xml $doc $openTag $body $closeTag')
    _note.content      =  template.substitute(xml=xmlTag,doc=docTag,openTag=noteOpenTag,body=content,closeTag=noteCloseTag)
    #Update the note
    note_store.updateNote(_note)




def renameAndMoveFile():
    # Rename files (Rename no longer needed, added output name parameter to teh youtube-dl call)
    #print('Renaming downloaded files...')
    #for file in utils.files():
    #    split_comps = file.rsplit('.', 1)
    #    filename = split_comps[0].rsplit('-', 1)[0]
    #    extension = split_comps[1]
    #    new_filename = '{}.{}'.format(filename, extension)
    #    os.rename(file, new_filename)

    # Move files
    print('Moving downloaded file to external drive...')
    destination = '/Volumes/Data/Archive/YouTube/'
    for file in utils.files():
        print('will move', file)
        try:
            shutil.move(file, destination)
        except Exception as e:
            full_path = path = os.path.realpath(file)
            print("file {} already moved. will delete".format(file))
            os.remove(full_path)

def download_files():
    print('Downloading videos...')
    videos_with_error = []
    note = note_store.getNote(guid, True, True, False, False)
    text = note.content.split('<en-todo ')
    text.pop(0) # We remove the first element, as it is the evernote xml definition
    for todo in text:
        #print(todo)
        if not 'checked="true"' in todo and 'http' in todo:
            items = todo.split(' ')
            for item in items:
                if 'youtu.be' in item or 'youtube.com' in item:
                    if 'playlist' in item:
                        file_naming_template = '%(playlist)s (#%(playlist_index)s): %(title)s (%(upload_date)s).%(ext)s'
                    else:
                        file_naming_template = '%(title)s (%(upload_date)s).%(ext)s'
                        #item = 'https://www.youtube.com/watch?v=JhHMJCUmq28'

                    download_video_command = 'youtube-dl -o "{}" {}'.format(file_naming_template, item)
                    #get_filename_command   = download_video_command[:10] + '--get-filename' + download_video_command[10:]
                    #get_filename_command   = get_filename_command[10:]
                    #print(get_filename_command)

                    #file_name = subprocess.Popen(['youtube-dl',  get_filename_command], stdout=subprocess.PIPE).communicate()[0]
                    #print('cmd', get_filename_command)
                    #print('fileName', file_name)
                    os.system(download_video_command)

                    #Todo: add support for youtube.com urls (they have a 'watch?' text before the videoID, that doesnt get cut of by .split(/))
                    videoID = item.rsplit('/', 1)[1]
                    #print(videoID)
                    #sys.exit()
                    _files = utils.files()
                    didFind = False
                    for file in _files:
                        didFind = True
                        print('Ticking ckeckbox in Evernote...')
                        newTodo = todo.replace('checked="false"', 'checked="true"', 1)
                        replaceInNote(todo, newTodo, 1)
                        renameAndMoveFile()
                        if not didFind:
                            videos_with_error.append(item)
                            #sys.exit('ERROR: DIDNT FIND file_name in files')
    print("did finish downloading all items.")
    print("the following items threw an error:")
    print(videos_with_error)

def main():
    global guid
    global note_store

    with open('config.json') as json_file:
        config = json.load(json_file)

    auth_token = config['auth_token']
    guid = config['note_guid']

    client = EvernoteClient(token=auth_token, sandbox=False)
    note_store = client.get_note_store()

    replaceInNote('<en-todo/>', '<en-todo checked="false"/>')

    download_files()


if __name__ == '__main__':
    main()
