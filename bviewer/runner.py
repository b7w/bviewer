#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bviewer.settings')

    if len(sys.argv) < 2:
        sys.stderr.write('Usage: bviwer.py config_path [management args]\n')
        sys.exit(1)

    args = sys.argv[:1] + sys.argv[2:]
    os.environ.setdefault('DJANGO_SETTINGS_FILE', sys.argv[1])

    from django.core.management import execute_from_command_line

    execute_from_command_line(args)


if __name__ == "__main__":
    main()
