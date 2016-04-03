# archive_scripts
A small collection of Python scripts to archive certain data from the internet

### youtube.py
- Download YouTube videos and move them to a folder of your choice. (You'll need to change the path [in the code](https://github.com/lukaskollmer/archive_scripts/blob/master/youtube.py#L51)).
- This script will read YouTube links from an Evernote note, download them and mark them as downloaded in the note.
- You can add urls to the note using [this Pythonista script](https://github.com/lukaskollmer/pythonista-youtube-archiving)
- Note: you need to create a ``config.json`` file with the following contents:

```json
{
  "auth_token" : "__YOUR_EVERNOTE_AUTH_TOKEN__",
  "note_guid"  : "__THE_GUID_OF_THE_NOTE_WHERE_YOU_STORE_THE_YOUTUBE_LINKS__"
}

```
