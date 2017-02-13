#!/usr/bin/env python3
import os
import sys
import csv
import argparse
import webbrowser
from collections import namedtuple, OrderedDict


BookmarkBase = namedtuple('BookmarkBase', [
    'code',
    'url',
    'description'
])


class Bookmark(BookmarkBase):

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

    def __init__(self):
        self.args = Args()
        self.storage = CSVObjectStorage(self.args.storage_path)
        self.bookmarks = OrderedDict(
            (x.code, x) for x in map(Bookmark._make, self.storage.load()))

    def run(self):
        command = getattr(self, self.args.subcommand)
        command()

    def list(self):
        if not self.bookmarks:
            print("\tIt's empty here!  :(  ")

        for bookmark in self.bookmarks.values():
            print(bookmark)

    def add(self):
        code = self.args.code
        if not self.args.force and code in self.bookmarks:
            msg = ("There is a bookmark with that code:\n"
                   "{0}\n\n"
                   "To override it add option -f")
            raise ApplicationError(msg.format(self.bookmarks[code]))

        self.bookmarks[code] = Bookmark(
            code, self.args.url, self.args.description)
        self.storage.save(self.bookmarks.values())

    def rm(self):
        bookmark = self.bookmarks.pop(self.args.code, None)

        if not bookmark:
            raise ApplicationError("There is no bookmark with that code")

        self.storage.save(self.bookmarks.values())

    def go(self):
        bookmark = self.bookmarks.get(self.args.code)

        if not bookmark:
            raise ApplicationError("There is no bookmark that code")

        webbrowser.open_new_tab(bookmark.url)


class Args:

    def __init__(self):
        self.init_from_args()
        self.init_from_env()

        self.storage_path = os.path.expanduser(self.storage_path)

    def init_from_args(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(title='subcommands',
                                           dest='subcommand')
        parser.add_argument('--storage-path', default='~/.webmark')

        subparsers.add_parser('list')

        subparser_add = subparsers.add_parser('add')
        subparser_add.add_argument('-f', action='store_true', dest='force')
        subparser_add.add_argument('code')
        subparser_add.add_argument('url')
        subparser_add.add_argument('description')

        subparser_rm = subparsers.add_parser('rm')
        subparser_rm.add_argument('code')

        subparser_go = subparsers.add_parser('go')
        subparser_go.add_argument('code')

        parser.parse_args(namespace=self)

    def init_from_env(self):
        self.storage_path = os.environ.get('WEBMARK_STORAGE_PATH',
                                           self.storage_path)


if __name__ == '__main__':
    try:
        error_code = BookmarksApp().run()
    except ApplicationError as e:
        print(e)
        sys.exit(1)
