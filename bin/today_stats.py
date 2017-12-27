#!/usr/bin/env python3
"""Получить статистику за сегодня"""

import time
from itertools import groupby
from datetime import timedelta

from window_activity import log_reader


def workspaces(data):
    """Получить только список workspace из набора"""
    return sorted(set([tt['workspace'] for tt in data]))


def print_line(itm):
    """Напечатать одну строку статистики"""
    print(itm['name'], itm['human'], sep="\t")


def do_magic():
    """Вывести статистику за сегодня"""
    data = list(log_reader())
    prev = None
    for row in data:
        if prev is None:
            prev = row
            continue
        prev['duration'] = float(row['time']) - float(prev['time'])
        prev = row
    prev['duration'] = time.time() - float(prev['time'])

    data = sorted(data, key=lambda itm: itm['software'])
    grouped = groupby(data, key=lambda itm: itm['software'])
    humaned = []
    for group, dat in grouped:
        dat = list(dat)
        seconds = int(sum([t['duration'] for t in dat]))
        humaned.append({
            'name': group,
            'human': timedelta(seconds=seconds),
            'seconds': seconds,
            'data': dat})

    for itm in sorted(humaned, key=lambda t: t['seconds']):
        if itm['name']:
            print_line(itm)


if __name__ == '__main__':
    do_magic()
