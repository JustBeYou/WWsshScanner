#!/bin/sh

rm -rf *.c
rm -rf bin

python compile.py build_ext --inplace
cython --embed main.py -o main.c
gcc -Os -I /usr/include/python2.7 -o scanner main.c -lpython2.7 -lpthread -lm -lutil -ldl

mkdir bin
mv *.so bin
mv scanner bin

mkdir bin/ssh2
cp -r ~/.local/lib/python2.7/site-packages/ssh2/.libs bin/ssh2
cp ~/.local/lib/python2.7/site-packages/ssh2/*.so bin/ssh2
cp ~/.local/lib/python2.7/site-packages/ssh2/__init__.py bin/ssh2
cp ~/.local/lib/python2.7/site-packages/ssh2/_version.py bin/ssh2
cp -r data bin/
