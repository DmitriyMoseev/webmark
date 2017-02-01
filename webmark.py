#!/usr/bin/env python3
import os
import sys
import csv
import argparse
import webbrowser
from collections import namedtuple, OrderedDict


class Bookmark(namedtuple('BookmarkBase', ['code', 'url', 'description'])):

    def __str__(self):
        return '[{0.code}] {0.url} - {0.description}'.format(self)


class CSVObjectStorage:

    def __init__(self, filename):
        self.filename = filename
        self.csv_format = {'delimiter': ' ', 'quotechar': '"'}

    def load(self):
        if not os.path.isfile(self.filename):
            return

        with open(self.filename, 'r') as f:
            reader = csv.reader(f, **self.csv_format)
            for row in reader:
                yield row

    def save(self, rows):
        with open(self.filename, 'w') as f:
            writer = csv.writer(f, **self.csv_format)
            for row in rows:
                writer.writerow(row)


class ApplicationError(Exception):
    pass


class BookmarksApp:

    def __init__(self, settings):
        self.settings = settings
        self.storage = CSVObjectStorage(self.settings.storage_path)
        self.bookmarks = OrderedDict(
            (x.code, x) for x in map(Bookmark._make, self.storage.load()))

    def run(self):
        command = getattr(self, self.settings.command)
        command()

    def list(self):
        if not self.bookmarks:
            print("\tIt's empty here!  :(  ")

        for bookmark in self.bookmarks.values():
            print(bookmark)

    def add(self):
        bookmark = Bookmark(*self.settings.command_args)

        if not self.settings.force and bookmark.code in self.bookmarks:
            bookmark = self.bookmarks[bookmark.code]
            msg = ("There is a bookmark with that code:\n"
                   "{0}\n\n"
                   "To override it add option -f").format(bookmark)
            raise ApplicationError(msg)

        self.bookmarks[bookmark.code] = bookmark
        self.storage.save(self.bookmarks.values())

    def rm(self):
        code = self.settings.command_args[0]
        bookmark = self.bookmarks.pop(code, None)

        if not bookmark:
            raise ApplicationError("There is no bookmark with code {}".format(code))

        self.storage.save(self.bookmarks.values())

    def open(self):
        code = self.settings.command_args[0]
        bookmark = self.bookmarks.get(code)

        if not bookmark:
            raise ApplicationError("There is no bookmark with code {}".format(code))

        webbrowser.open_new_tab(bookmark.url)


class ArgumentsError(Exception):
    pass


class Settings:

    def __init__(self):
        self.init_from_args()
        self.init_from_env()

        self.storage_path = os.path.expanduser(self.storage_path)

    def init_from_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('command', choices=['list', 'add', 'rm', 'open'])
        parser.add_argument('command_args', nargs='*')
        parser.add_argument('-f', action='store_true', dest='force')
        parser.add_argument('--storage-path', default='~/.webmark')
        parser.parse_args(namespace=self)

        if self.command == 'add' and len(self.command_args) != 3:
            raise ArgumentsError("To add bookmark use following command:\n\t"
                                 "webmark add {code} {url} {description}")
        if self.command == 'open' and len(self.command_args) != 1:
            raise ArgumentsError("To open bookmark use following command:\n\t"
                                 "webmark open {code}")
        if self.command == 'rm' and len(self.command_args) != 1:
            raise ArgumentsError("To remove bookmark use following command:\n\t"
                                 "webmark rm {code}")

    def init_from_env(self):
        self.storage_path = os.environ.get('WEBMARK_STORAGE_PATH',
                                           self.storage_path)


if __name__ == '__main__':
    try:
        settings = Settings()
        error_code = BookmarksApp(settings).run()
    except (ApplicationError, ArgumentsError) as e:
        print(e)
        sys.exit(1)
