#!/usr/bin/env python

import os
import re
import sys
import shutil
from stat import S_IMODE
from subprocess import call


RH_ARROW = u"\u2192"
MH_VERSION = 1.0
BUILD_ROOT = "./mh-tracerbn-%s" % MH_VERSION

PKG_LEAF_DIRS = ["DEBIAN",
                 "etc/uwsgi/apps-available",
                 "usr/local/bin",
                 "etc/supervisor/conf.d",
                 "var/lib/grafana"]

DEB_FILES = ["conffiles",
             "control",
             "postinst",
             "preinst"]

MH_FILES_SRC_DST = [["../tracerbn-api/mh-tracerbn-api.py", "%s/mh-tracerbn-api.py" % PKG_LEAF_DIRS[2]],
                    ["../tracerbn-api/mhtracerbn.py", "%s/mhtracerbn.py" % PKG_LEAF_DIRS[2]],
                    ["../tracerbn-api/mh-tracerbn-api-uwsgi.ini", "%s/mh-tracerbn-api-uwsgi.ini" % PKG_LEAF_DIRS[1]],
                    ["../data-acquisition/mh-data-acquisition.py", "%s/mh-data-acquisition.py" % PKG_LEAF_DIRS[2]],
                    ["../data-acquisition/mh-data-acquisition-supervisor.conf", "%s/mh-data-acquisition-supervisor.conf" % PKG_LEAF_DIRS[3]],
                    ["../data-acquisition/mh-data-acquisition.conf", "etc/mh-data-acquisition.conf"],
                    ["../grafana/grafana.db", "%s/grafana.db" % PKG_LEAF_DIRS[4]]]


CONFFILES_PATH = "%s/%s/%s" % (BUILD_ROOT, PKG_LEAF_DIRS[0], DEB_FILES[0])
CONTROL_FILE_PATH = "%s/%s/%s" % (BUILD_ROOT, PKG_LEAF_DIRS[0], DEB_FILES[1])
POSTINST_FILE_PATH = "%s/%s/%s" % (BUILD_ROOT, PKG_LEAF_DIRS[0], DEB_FILES[2])
PREINST_FILE_PATH =  "%s/%s/%s" % (BUILD_ROOT, PKG_LEAF_DIRS[0], DEB_FILES[3])

#
# Error handler
#
def fail_and_exit(msg, e=None):
    print("\t%s" % msg)
    if e: print("\tReason: %s" % e)
    sys.exit(-1)


print("Beggining build process in: %s/" % os.getcwd())

# Remove any existing old build root
try:
    if os.path.isdir(BUILD_ROOT) and os.path.exists(BUILD_ROOT):
        print("Removing existing build root directory and contents")
        shutil.rmtree(BUILD_ROOT)
except Exception as e:
    fail_and_exit("Failed to remove existing build root directory", e)

# Create directory structure
for dir in PKG_LEAF_DIRS:
    dir_path = "%s/%s" % (BUILD_ROOT, dir)

    try:
        print("Creating directory: %s" % dir_path)
        os.makedirs(dir_path)
    except Exception as e:
        fail_and_exit("Failed to create directory: %s" % dir_path, e)


# Update version number in control file
# Read in the file
with open(DEB_FILES[1], 'r') as control_fh:
    control_file_txt = control_fh.read()

# Search for the line of interest.
m = re.search('\nVersion: \d+\.\d+.*\n', control_file_txt)
if m:
    # Replace the target string
    print("Setting Version number to: %s in control file" % MH_VERSION)
    control_file_txt = control_file_txt.replace(m.group(), '\nVersion: %s\n' % MH_VERSION)

    # Write the file out again
    with open(DEB_FILES[1], 'w') as control_fh:
        control_fh.write(control_file_txt)
else:
    print("Failed to find existing Version number in control file")


#
# Simple file copy function, with nice output and clear errors.
# Exits on failure.
#
def copy_files_to_buildroot(src_path, dst_path):
    try:
        print("Copying file: %s %s %s" % (src_path, RH_ARROW, dst_path))
        shutil.copyfile(src_path, dst_path)
    except Exception as e:
        fail_and_exit("Failed to copy file: %s %s %s" % (src_path, RH_ARROW, dst_path), e)


# Copy DEBIAN files
for deb_file in DEB_FILES:
    src_path = "./%s" % deb_file
    dst_path = "%s/%s/%s" % (BUILD_ROOT, "DEBIAN", deb_file)
    copy_files_to_buildroot(src_path=src_path, dst_path=dst_path)


# Copy source and config files for the package payload
for src_dst in MH_FILES_SRC_DST:
    dst_path = "%s/%s" % (BUILD_ROOT, src_dst[1])
    copy_files_to_buildroot(src_path=src_dst[0], dst_path=dst_path)

# Check / Set DEBIAN file permissions
for file_path in [CONTROL_FILE_PATH, PREINST_FILE_PATH, POSTINST_FILE_PATH]:
    try:
        file_stats = os.stat(file_path)
        file_mode = oct(S_IMODE(file_stats.st_mode))

        if 555 <= int(file_mode) <= 775:
            os.chmod(file_path, 0755)
            print("Changed mode %s to %o of file: %s" % (file_mode, 0755, file_path))
    except Exception as e:
        fail_and_exit("Failed to check/change file mode(s) of %s" % file_path, e)


# Build package
pkg_name = "./mh-tracerbn-%s_all.deb" % MH_VERSION
if call(["dpkg", "-b", BUILD_ROOT, pkg_name]) != 0:
    fail_and_exit("Failed to build package: %s" % pkg_name)
else:
    print("Package built ok")
    sys.exit(0)
