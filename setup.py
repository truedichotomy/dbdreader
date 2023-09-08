import sys
import os

import setuptools
import packaging.version

with open("dbdreader/__init__.py", "r") as fh:
    VERSION = fh.readline().strip().split("=")[1].replace('"', '')

with open("README.rst", "r") as fh:
    long_description = fh.read()
    
with open('requirements.txt') as fh:
    install_requires = [line.strip() for line in fh]


# Now determine what we need to build ourselves.    
sources = ["extension/py_dbdreader.c",
           "extension/dbdreader.c",
           "extension/decompress.c"]
include_dirs = ['extension/include']
library_dirs = []


def check_header_file_version(p):
    version=dict(MAJOR=0, MINOR=0, RELEASE=0)
    counter=0
    with open(p) as fp:
        for line in fp:
            if line.startswith("#define LZ4_VERSION"):
                fields = line.strip().split()
                for k in version.keys():
                    if k in fields[1]:
                        version[k] = fields[2]
                        counter+=1
            if counter==3:
                break
    if counter==3:
        v = ".".join((version["MAJOR"],
                      version["MINOR"],
                      version["RELEASE"]))
    else:
        v=""
    return v
            
def has_header_file(header_file='lz4.h',required_version=None):
    include_dirs = ['/usr/include',
                    '/usr/local/include']
    found = False
    for d in include_dirs:
        p = os.path.join(d, header_file)
        if os.path.exists(p):
            found = True
            break
    if found:
        version = check_header_file_version(p)
        if version and required_version is None:
            return True
        else:
            V = packaging.version.parse(version)
            Vreq = packaging.version.parse(required_version)
            return V>=Vreq
    else:
        return False


if sys.platform.startswith('linux'):
    # we're on linux, so check for a system-wide installed library of
    # lz4 and use that if available.
    import ctypes
    try:
        # Try to load the lz4 library
        ctypes.CDLL("liblz4.so.1")
    except OSError:
        liblz4_found = False
    else:
        # Library found, what about the include file?
        if has_header_file('lz4.h', required_version='1.7.5'):
            liblz4_found = True
        else:
            liblz4_found = False
elif sys.platform.startswith("win"):
    liblz4_found=False
else:
    liblz4_found=False


if liblz4_found:
    # We are on a linux platform, and have access to system-wide
    # installed library of lz4.
    libraries = ['lz4']
else:
    # we need to integrate the lz4 code in our build.
    sources += ["lz4/lz4.c"]
    libraries = []
    include_dirs += ['lz4/include']
    
setuptools.setup(
    name="dbdreader",
    version=VERSION,
    author="Lucas Merckelbach",
    author_email="lucas.merckelbach@hereon.de",
    description="A python module to access binary data files generated by Teledyne WebbResearch gliders",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url='https://dbdreader.readthedocs.io/en/latest/',
    packages=['dbdreader'],
    py_modules=[],
    entry_points = {'console_scripts':['dbdrename=dbdreader.scripts:dbdrename',
                                        'cac_gen=dbdreader.scripts:cac_gen'],
                    'gui_scripts':[]
    },
    scripts = [],
    install_requires = install_requires,
    ext_modules = [
           setuptools.Extension("_dbdreader",
                                sources = sources,
                                libraries = libraries,
                                include_dirs = include_dirs, 
                                library_dirs = library_dirs)
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        "Operating System :: POSIX",
    ],
)
