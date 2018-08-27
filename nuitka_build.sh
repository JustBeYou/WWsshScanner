#!/bin/sh

rm -rf main.dist main.build
nuitka --standalone --recurse-on main.py --verbose

cp -rf ~/.local/lib/python2.7/site-packages/ssh2/.libs main.dist/ssh2
cp -f ~/.local/lib/python2.7/site-packages/ssh2/*.so main.dist/ssh2
cp -f ~/.local/lib/python2.7/site-packages/ssh2/__init__.py main.dist/ssh2
cp -f ~/.local/lib/python2.7/site-packages/ssh2/_version.py main.dist/ssh2

cp -r data/ main.dist/
