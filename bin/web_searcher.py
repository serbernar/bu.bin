#!/usr/bin/env python3
"""
Взаимодействие с поисковыми системами через dmenu.

Этот скрипт открывает файл ~/.db/wiki/search-engines.md,
позволяет выбрать поисковую систему из списка, спрашивает запрос.
"""

from subprocess import Popen, PIPE
import os.path
import datetime
import socket
import re
import csv
import urllib.parse
import click

import helpers

ENGINES_PATH = os.path.expanduser('~/.db/wiki/search-engines.md')
HISTORY_PATH = os.path.expanduser('~/.db/wiki/search-history.csv')
CSV_FIELDS = ('engine', 'query', 'time', 'hostname')

def isodatetime():
    """Получить iso строку времени"""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def engines():
    """Получить список поисковых систем"""
    with open(ENGINES_PATH) as f:
        return [t.strip() for t in f.readlines()]

def dmenu_stdin(label, stdin, lines=20):
    """Получить вывод от dmenu, передав ему данные на вход"""
    proc = Popen([os.path.expanduser('~/.bu.bin/bin/dmenu-wrapper'), label, str(lines)],
                 stdout=PIPE,
                 stdin=PIPE,
                 stderr=PIPE)

    stdout_data = proc.communicate(input=stdin.encode('utf-8'))[0]
    return stdout_data.decode('utf-8').strip()

def old_queries(prefer=None):
    """Вернуть список запросов прошлых"""
    with open(HISTORY_PATH) as tfile:
        return list(csv.DictReader(tfile))



def save_query(obj):
    """Сохранить объект в базу"""
    obj['hostname'] = socket.gethostname()
    obj['time'] = isodatetime()
    with open(HISTORY_PATH, 'a') as tfile:
        writer = csv.DictWriter(tfile, CSV_FIELDS)
        writer.writerow(obj)

class Engine():
    """Поисковик"""
    def __init__(self, line):
        self.line = line
    def name(self):
        """Получить название"""
        return re.match('(.*)(https?:.*)', self.line).groups()[0].strip()
    def url(self):
        """Получить ссылку"""
        return re.match('(.*)(https?:.*)', self.line).groups()[1].strip()



def get_engine(label='Выбор системы'):
    """Получить строку-поисковик"""
    return Engine(helpers.dmenu_file(os.path.expanduser(ENGINES_PATH), label=label))

def get_query(prefer=None, label='Запрос'):
    """Спросить поисковый запрос"""
    queries = list({t['query']: None for t in old_queries(prefer=prefer)}.keys())
    return dmenu_stdin(label, "\n".join(reversed(queries)))

def ensure_history_file_exists():
    """Удостовериться что файл для истории запросов есть"""
    if not os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, 'a+') as tfile:
            writer = csv.DictWriter(tfile, CSV_FIELDS)
            writer.writeheader()

@click.group()
def cli():
    """..."""
    pass

@cli.command()
def full_search():
    """Сделать всю работу"""
    engine = get_engine()
    query = get_query(prefer=engine.name(), label="Поиск в {}".format(engine.name()))
    if len(query):
        save_query({'engine': engine.name(), 'query': query})
        url = engine.url().replace("%s", urllib.parse.quote(query))
        helpers.open_in_browser(url)
        helpers.open_i3_workspace('www')

def last_query():
    """Получить последнюю запись из поиска"""
    with open(HISTORY_PATH) as tfile:
        return list(csv.DictReader(tfile))[-1]

def last_engine():
    """Получить последнюю поисковую систему"""
    name = last_query()['engine']
    for engine in engines():
        t = Engine(engine)
        if t.name() == name:
            return t


@cli.command()
def last_engine_search():
    """Задать только запрос для поиска"""
    engine = last_engine()
    query = get_query(prefer=engine.name(), label="Поиск в {}".format(engine.name()))
    if len(query):
        save_query({'engine': engine.name(), 'query': query})
        url = engine.url().replace("%s", urllib.parse.quote(query))
        helpers.open_in_browser(url)
        helpers.open_i3_workspace('www')

@cli.command()
def last_query_search():
    """Задать только систему поиска"""
    query = last_query()['query']
    engine = get_engine(label='Найти "{}" в'.format(query))
    if len(query):
        save_query({'engine': engine.name(), 'query': query})
        url = engine.url().replace("%s", urllib.parse.quote(query))
        helpers.open_in_browser(url)
        helpers.open_i3_workspace('www')

if __name__ == '__main__':
    ensure_history_file_exists()
    cli()