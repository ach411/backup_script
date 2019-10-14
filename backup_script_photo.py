#!/usr/bin/python
# Aurelien Chiron, Fev 2019

import os, sys, shutil
from filecmp import dircmp

# global variables
dry_run = False
remove_confirmation = False

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def text_in_color(color_code):
    return lambda text : color_code + text + bcolors.ENDC

fail_color = text_in_color(bcolors.FAIL)
warning_color = text_in_color(bcolors.WARNING)
header_color = text_in_color(bcolors.HEADER)
bold_color = text_in_color(bcolors.BOLD)

def properly_quit(return_code):
    # remove_temp_directory()
    sys.exit(return_code)

def usage():
    print 'usage: backup_script_photo.py [-y|-d] source_dir dest_dir'
    print '-d option: dry run, just display what script would do'
    print '-y option: remove need for confirmation when some file are deleted'
    properly_quit(1)

def erase_dest_files_or_dirs(dcmp, dest_dir):
    for name in dcmp.right_only:
        if os.path.isfile(dest_dir + '/' + name):
            print "File %s will be erased" % name
            if not dry_run:
                if not remove_confirmation:
                    answer = raw_input(warning_color("Do you really want to erase file %s? (Y)es/(N)o\n" % (dest_dir + '/' + name)))
                    if not (answer == 'Y' or answer == 'y'):
                        continue
                os.remove(dest_dir + '/' + name)
        if os.path.isdir(dest_dir + '/' + name):
            print "Folder %s will be erased" % name
            if not dry_run:
                if not remove_confirmation:
                    answer = raw_input(warning_color("Do you really want to erase folder %s? (Y)es/(N)o\n" % (dest_dir + '/' + name)))
                    if not (answer == 'Y' or answer == 'y'):
                        continue
                shutil.rmtree(dest_dir + '/' + name)

def overwrite_dest_files(dcmp, source_dir, dest_dir):
    for name in dcmp.diff_files:
        print "File %s will be overwritten" % name,
        if os.path.getmtime(dest_dir + '/' + name) > os.path.getmtime(source_dir + '/' + name):
            print warning_color('=> file to be replaced appears to be newer!')
        else:
            print
        if not dry_run:
            if not remove_confirmation:
                answer = raw_input(warning_color("Do you really want to overwrite file %s? (Y)es/(N)o\n" % (dest_dir + '/' + name)))
                if not (answer == 'Y' or answer == 'y'):
                    continue
            shutil.copy(source_dir + '/' + name, dest_dir + '/' + name)

def copy_to_dest(dcmp, source_dir, dest_dir):
    for name in dcmp.left_only:
        if os.path.isfile(source_dir + '/' + name):
            print "File %s will be copied over" % name
            if not dry_run:
                shutil.copy2(source_dir + '/' + name, dest_dir)
        if os.path.isdir(source_dir + '/' + name):
            print "Directory %s will be copied over" % name
            if not dry_run:
                shutil.copytree(source_dir + '/' + name, dest_dir + '/' + name)

def compare_2_folder(source_dir, dest_dir, erase_in_dest):

    if not os.path.exists(source_dir):
        print fail_color("Error: source folder %s is missing" % source_dir)
        properly_quit(2)

    if not os.path.exists(dest_dir):
        print fail_color("Error: destination folder %s is missing" % dest_dir)
        properly_quit(3)

    print header_color("===== Compare folder %s and folder %s =====" % (os.path.abspath(source_dir), os.path.abspath(dest_dir)))
    # dcmp = dircmp(source_dir, dest_dir)
    dcmp = dircmp(source_dir, dest_dir, ["Thumbs.db"])

    # Files or directories that remains only on destination drive
    # to be erased on the destination drive
    if erase_in_dest:
        erase_dest_files_or_dirs(dcmp, dest_dir)

    # Files that are present on both drive but are different!
    # to be overwritten on the destination drive
    overwrite_dest_files(dcmp, source_dir, dest_dir)

    # Files or directories that are only present on source drive
    # to be copied over to the destination drive
    copy_to_dest(dcmp, source_dir, dest_dir)

    # Common Directories to be further parsed
    # recursively call compare function
    for name in dcmp.common_dirs:
        compare_2_folder(source_dir+'/'+name, dest_dir+'/'+name, True)

def main():

    args = sys.argv[1:]

    if not args:
        usage()
    elif args[0] == '-y':
        remove_confirmation = True
        args = args[1:]
    elif args[0] == '-d':
        global dry_run
        dry_run = True
        args = args[1:]

    if len(args) < 2:
            usage()

    print

    compare_2_folder(args[0], args[1], False)
    properly_quit(0)

if __name__ == "__main__":
    main()
