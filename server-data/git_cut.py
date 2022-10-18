#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import argparse
import logging
import sys

logging.basicConfig(format='[%(asctime)s] [%(levelname).1s] %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO,
                    stream=sys.stdout)

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--commit', help='hash of commit', required=True)
parser.add_argument('-m', '--message', help='message of commit', required=False, default='Обрезка истории коммитов')
args = parser.parse_args()

logging.info('Start cut history')

logging.info('Add info commit')
cmd = ['git', 'commit-tree', '-m', args.message, args.commit + '^{tree}']
out = subprocess.run(cmd, capture_output=True, text=True)

logging.info('Rebasing...')
cmd = ['git', 'rebase', '--onto', out.stdout.strip(), args.commit]
out = subprocess.run(cmd)

logging.info('Garbage collecting...')
cmd = ['git', 'gc', '--prune=now', '--aggressive']
out = subprocess.run(cmd)
logging.info('Done')
