#!/usr/bin/env python3
import argparse
import os
import re
import sys

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tif', '.tiff'}


def parse_data_yaml(path):
    classes = []
    if not os.path.isfile(path):
        return classes
    with open(path, 'r', encoding='utf-8') as f:
        lines = [line.rstrip('\n') for line in f]

    names_section = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('names:'):
            names_section = True
            continue
        if names_section:
            if not stripped or stripped.startswith('#'):
                continue
            m = re.match(r'^(\d+)\s*:\s*(.+)$', stripped)
            if m:
                classes.append(m.group(2).strip())
            else:
                break
    return classes


def load_classes(data_yaml, classes_txt):
    classes = parse_data_yaml(data_yaml)
    if classes:
        return classes
    if os.path.isfile(classes_txt):
        with open(classes_txt, 'r', encoding='utf-8') as f:
            classes = [line.strip() for line in f if line.strip()]
    return classes


def list_images(images_dir):
    if not os.path.isdir(images_dir):
        return []
    files = []
    for entry in os.scandir(images_dir):
        if not entry.is_file():
            continue
        ext = os.path.splitext(entry.name)[1].lower()
        if ext in IMAGE_EXTS:
            files.append(entry.name)
    return sorted(files)


def list_label_files(labels_dir):
    if not os.path.isdir(labels_dir):
        return []
    files = []
    for entry in os.scandir(labels_dir):
        if not entry.is_file():
            continue
        if entry.name.lower().endswith('.txt'):
            files.append(entry.name)
    return sorted(files)


def image_to_label(image_name):
    return os.path.splitext(image_name)[0] + '.txt'


def report(images, labels, classes):
    image_set = {image_to_label(img) for img in images}
    label_set = set(labels)

    missing = sorted(image_set - label_set)
    orphan = sorted(label_set - image_set)

    print('Dataset report:')
    print(f'  images: {len(images)}')
    print(f'  label files: {len(labels)}')
    print(f'  missing labels: {len(missing)}')
    print(f'  orphan labels: {len(orphan)}')
    print(f'  classes: {len(classes)}')
    if classes:
        for idx, name in enumerate(classes):
            print(f'    {idx}: {name}')
    if missing:
        print('\nMissing label files for these images:')
        for name in missing[:50]:
            print(f'  {name}')
        if len(missing) > 50:
            print(f'  ... and {len(missing) - 50} more')
    if orphan:
        print('\nOrphan label files (no matching image):')
        for name in orphan[:50]:
            print(f'  {name}')
        if len(orphan) > 50:
            print(f'  ... and {len(orphan) - 50} more')
    return missing, orphan


def create_empty_labels(labels_dir, missing, dry_run=False):
    if not missing:
        print('\nNo missing label files to create.')
        return
    os.makedirs(labels_dir, exist_ok=True)
    for filename in missing:
        path = os.path.join(labels_dir, filename)
        if os.path.exists(path):
            continue
        if dry_run:
            print(f'  [dry-run] create {path}')
        else:
            with open(path, 'w', encoding='utf-8') as f:
                pass
            print(f'  created {path}')


def main():
    parser = argparse.ArgumentParser(
        description='Label dataset helper for YOLO-style labels.'
    )
    parser.add_argument('--images', default='images', help='Image folder path')
    parser.add_argument('--labels', default='labels', help='Label folder path')
    parser.add_argument('--data', default='data.yaml', help='Dataset YAML with class names')
    parser.add_argument('--classes', default='classes.txt', help='Class list file fallback')
    parser.add_argument('--create-empty', action='store_true', help='Create empty label files for missing images')
    parser.add_argument('--dry-run', action='store_true', help='Do not modify files; only show actions')
    parser.add_argument('--quiet', action='store_true', help='Only print summary counts')
    args = parser.parse_args()

    images_dir = os.path.abspath(args.images)
    labels_dir = os.path.abspath(args.labels)
    data_yaml = os.path.abspath(args.data)
    classes_txt = os.path.abspath(args.classes)

    classes = load_classes(data_yaml, classes_txt)
    images = list_images(images_dir)
    labels = list_label_files(labels_dir)

    missing, orphan = report(images, labels, classes)
    if args.quiet:
        return

    if args.create_empty:
        print('\nCreating missing label files...')
        create_empty_labels(labels_dir, missing, dry_run=args.dry_run)
    else:
        if missing:
            print('\nRun with --create-empty to generate blank label files for missing images.')

    if orphan and not args.quiet:
        print('\nTip: remove orphan labels if they are no longer needed or if images have been renamed.')

if __name__ == '__main__':
    main()
