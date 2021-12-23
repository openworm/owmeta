#!/bin/bash -xe
HEAD_REV=$(git rev-parse HEAD)
git ls-remote origin refs/heads/dev | grep -q -E -o "^$HEAD_REV" || \
    echo "Not deploying since we aren't on the 'dev' branch" >&2 && \
    exit 0

git log --format=%s -n 1 "$HEAD_REV" | grep -E -q '(^MINOR:)|(\[skip-deploy\])' && exit 0

date=$(date +"%Y%m%d%H%M%S")
sed -i -r "s/__version__ = '([^']+)\\.dev0'/__version__ = '\\1.dev$date'/" owmeta/__init__.py
python setup.py egg_info sdist bdist_wheel
twine upload -c "Built by CI. Uploaded after $(date +"%Y-%m-%d %H:%M:%S")" dist/owmeta*tar.gz dist/owmeta*whl
