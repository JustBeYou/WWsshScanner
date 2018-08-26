from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [
    Extension("password", ["password.py"]),
    Extension("session", ["session.py"]),
    Extension("ips", ["ips.py"]),
    Extension("art", ["art.py"]),
    Extension("scan", ["scan.py"]),
]

setup(
    name = 'WWsshScanner',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)
