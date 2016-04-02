#coding: utf-8


import os


def files():
    files = []
    disallowed_files = [
        'podcast.py',
        '.gitignore',
        '.DS_Store',
        'utils.py',
        'utils.pyc',
        'youtube.py',
        'config.json',
        '.git'
    ]
    for f in os.listdir('.'):
        if not f in disallowed_files:
            files.append(f)

    return files

if __name__ == '__main__':
    print(files())
