#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import shutil
import logging
import argparse
import xml.etree.cElementTree as ET

logging.basicConfig(format='[%(asctime)s] [%(levelname).1s] %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO,
                    stream=sys.stdout)


def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def get_all_dir(prod_dir):
    all_dir = []
    for item in os.listdir(prod_dir):
        if os.path.isdir(os.path.join(prod_dir, item)):
            all_dir.append(item)

    return all_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', help='build version', required=True)  # default='5.5.5') for test
    parser.add_argument('-d', '--delete', help='delete branch', nargs='*', required=False)
    parser.add_argument('-r', '--del_resource', help='delete resources', nargs='*', required=False)
    parser.add_argument('-f', '--force', help='force update', nargs='*', required=False)
    parser.add_argument('-s', '--soft', help='soft update', nargs='*', required=False)
    args = parser.parse_args()

    prod_dir = os.path.join(os.getcwd(), 'prod')
    platform_dir = get_all_dir(prod_dir)

    # DELETE VERSION
    if args.delete is not None:
        for platform in platform_dir:
            try:
                shutil.rmtree(os.path.join(prod_dir, platform, args.version))
                logging.info("Delete folder: " + os.path.join(platform, args.version))
            except FileNotFoundError:
                logging.info("Not found folder: " + os.path.join(platform, args.version))

    # DELETE ALL FOLDERS FROM VERSION EXCLIDE PATCHES FOLDERS
    if args.del_resource is not None:
        for platform in platform_dir:
            try:
                dirs = get_all_dir(os.path.join(prod_dir, platform, args.version))
                for dir in dirs:
                    if dir[0] != "_":
                        shutil.rmtree(os.path.join(prod_dir, platform, args.version, dir))
                        logging.info("Delete folder: " + os.path.join(platform, args.version, dir))
            except FileNotFoundError:
                logging.info("Not found folder: " + os.path.join(platform, args.version))

    # CREATE FORCE OR SOFT UPDATE FILES
    if args.force is not None or args.soft is not None:
        file_name = "config.xml"

        root = ET.Element("root")
        version = ET.SubElement(root, "Version", {
            "update": "true",
            "mandatory": "true" if args.force is not None else "false",
            "update_time": str(time.time())[:10]})

        indent(root, 1)
        resourcesTree = ET.ElementTree(root)

        for platform in platform_dir:
            try:
                resourcesTree.write(os.path.join(prod_dir, platform, args.version, file_name),
                                    encoding="utf-8",
                                    xml_declaration=True,
                                    method="xml")
                logging.info("Write file: " + os.path.join(platform, args.version, file_name))
            except FileNotFoundError:
                logging.info("Not found folder: " + os.path.join(platform, args.version))

    logging.info('Done')
