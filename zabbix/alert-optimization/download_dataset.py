#!/usr/bin/env python3
""" Zabbix dataset downloader """

import csv
import os
import re
import sys
from datetime import datetime

from dotenv import load_dotenv
from zabbix_utils import ZabbixAPI

# # case 1:
# HOST_NAME = "host1"
# ITEM_PATTERN = "SMART [*]: Temperature"   # main item filter (zabbix-style)
# ITEM_FILTER_REGEX = r'nvme0|nvme3'      # Additional (regex)
# MARK = 'temp'  # additional case marking
# STR_FROM = '2025-03-01 00:00:00'
# STR_TO = '2025-03-08 00:00:00'


# case 2:
HOST_NAME = "host22"
ITEM_PATTERN = "Load average (*)"   # main item filter (zabbix-style)
ITEM_FILTER_REGEX = r'.+'      # Additional (regex)
MARK = 'loadavg'  # additional case marking
STR_FROM = '2025-03-09 00:00:00'
STR_TO = '2025-03-14 12:00:00'


CSV_DIR = "data"


def str_to_unix(time_str):
    """Convert string to Unix timestamp"""
    return int(datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S').timestamp())


load_dotenv()

with ZabbixAPI() as api:
    hosts = api.host.get(
        output=['hostid'],
        filter={'name': [HOST_NAME]}
    )

    if not hosts:
        print(f"Host '{HOST_NAME}' not found")
        sys.exit()

    host_ids = hosts[0]['hostid']

    items = api.item.get(
        output=['itemid', 'name', 'value_type'],
        hostids=host_ids,
        search={'name': ITEM_PATTERN},
        searchWildcardsEnabled=True
    )
    # Do additional filtering
    filtered_items = [item for item in items if re.search(ITEM_FILTER_REGEX, item['name'])]

    time_from = str_to_unix(STR_FROM)
    time_till = str_to_unix(STR_TO)

    # check and create data dir
    os.makedirs(CSV_DIR, exist_ok=True)

    # Get each item and save to csv file
    for item in filtered_items:
        history_type = int(item['value_type'])

        history = api.history.get(
            itemids=[item['itemid']],
            time_from=time_from,
            time_till=time_till,
            history=history_type,
            output=['clock', 'value'],
            sortfield='clock',
            sortorder='ASC'
        )

        if not history:
            print(f"No data for item {item['itemid']}")
            continue

        filename = os.path.join(CSV_DIR, f"history-{MARK}-{item['itemid']}.csv")
        metric_name = item['name'].strip()

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Datetime', metric_name])
            for record in history:
                dt = datetime.fromtimestamp(int(record['clock']))
                writer.writerow([
                    dt.strftime('%Y-%m-%d %H:%M:%S'),
                    record['value']
                ])
        print(f"File created: {filename}")

    # Saving all host events
    events = api.event.get(
        output='extend',
        hostids=host_ids,
        time_from=time_from,
        time_till=time_till,
        sortfield='clock',
        sortorder='ASC'
    )

    if events:
        filename = os.path.join(CSV_DIR, f"events-{MARK}.csv")
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Datetime', 'Event ID', 'Name', 'Severity', 'Status'])
            for event in events:
                dt = datetime.fromtimestamp(int(event['clock']))
                writer.writerow([
                    dt.strftime('%Y-%m-%d %H:%M:%S'),
                    event['eventid'],
                    event['name'],
                    event['severity'],
                    'OK' if event['value'] == '0' else 'PROBLEM'
                ])
            print(f"File created: {filename}")
    else:
        print("No events found.")
