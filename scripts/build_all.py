#!/usr/bin/env python3
"""Build the whole site in dependency order: section builders first, then the shared pages and maps."""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINAL = 'scripts/build.py'  # Reads the pages the other builders wrote to refresh both site maps.
# Files that build the site but are not part of it.
PRIVATE_ROOT = {'.git', '.github', '.vscode', '_site', 'content', 'scripts', 'tests', '.gitignore', 'AGENTS.md', 'README.md', 'requirements.txt'}
PRIVATE_ANYWHERE = {'__pycache__', 'content', 'templates', 'build.py'}


def builders(root):
    found = {path.relative_to(root).as_posix() for pattern in ('education/*/build.py', '*/build.py') for path in root.glob(pattern)}
    return sorted(found - {FINAL}) + [FINAL]


def build(root):
    for builder in builders(root):
        result = subprocess.run([sys.executable, builder], cwd=root, capture_output=True, text=True)
        if result.returncode:
            sys.exit(f'{builder} failed:\n{result.stdout}{result.stderr}')


def private(path):
    parts = path.parts
    return (parts[0] in PRIVATE_ROOT or PRIVATE_ANYWHERE.intersection(parts) or path.suffix == '.in'
            or (parts[0] == 'education' and (len(parts) == 2 and path.suffix == '.py' or parts[1] == 'checks')))


def publish(root, target):
    """Copy the built site without its sources, ready for hosting."""
    target = Path(target)
    if target.exists(): shutil.rmtree(target)
    for path in sorted(root.rglob('*')):
        name = path.relative_to(root)
        if path.is_file() and not private(name):
            (target / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target / name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', type=Path, metavar='DIR', help='after building, copy the public site to DIR')
    args = parser.parse_args()
    build(ROOT)
    print(f'Built the site with {len(builders(ROOT))} builders.')
    if args.publish:
        publish(ROOT, args.publish)
        print(f'Published to {args.publish}.')


if __name__ == '__main__':
    main()
