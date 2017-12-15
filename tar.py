#!/usr/bin/env python
import sys
import tarfile
import gzip
import os
from functools import partial

processed = set()
executableFiles = set()

def isExecutable(f):
    bin = open(f, mode='rb')
    buf = [ord(elem) for elem in bin.read(4)] + [0] * 4
    bin.close()
    
    # with thanks to fasterthanlime / itch.io
    # https://github.com/itchio/wharf/blob/7aea59dbdfd3fa9411618ac7ee931f2bffb8ead3/tlc/permissions.go
    
    # intel Mach-O executables start with 0xCEFAEDFE or 0xCFFAEDFE
    # (old PowerPC Mach-O executables started with 0xFEEDFACE)
    if (buf[0] == 0xCE or buf[0] == 0xCF) and buf[1] == 0xFA and buf[2] == 0xED and buf[3] == 0xFE:
        return True
    
    # Mach-O universal binaries start with 0xCAFEBABE
    # it's Apple's 'fat binary' stuff that contains multiple architectures
    if buf[0] == 0xCA and buf[1] == 0xFE and buf[2] == 0xBA and buf[3] == 0xBE:
        return True
    
    # ELF executables start with 0x7F454C46
    # (e.g. 0x7F + 'ELF' in ASCII)
    if buf[0] == 0x7F and buf[1] == 0x45 and buf[2] == 0x4C and buf[3] == 0x46:
        return True
    
    # Shell scripts start with a shebang (#!)
    # https://en.wikipedia.org/wiki/Shebang_(Unix)
    if buf[0] == 0x23 and buf[1] == 0x21:
        return True
    
    return False

def processFile(tar):
    f = tar.name.replace("\\", "/")
    
    if f in processed:
        return # exclude file
    
    processed.add(f)
    isExec = f in executableFiles
    
    if autoExec and not isExec and not tar.isdir():
        isExec = isExecutable(f)
        
    message = "Adding "
    if isExec:
        message = message + "executable "
    elif tar.isdir():
        message = message + "folder "
    message = message + "'" + f + "'"
    
    print message
    
    if isExec or tar.isdir():
        tar.mode = 0755
    else:
        tar.mode = 0644
    
    return tar
    
args = sys.argv

autoExec = False
for i in reversed(range(1, len(args))):
    if args[i].lower() == "-autoexec":
        autoExec = True
        del args[i]
        break

if len(args) <= 1:
  print "Usage: tar.py [out] [file1] [file2] ... [fileN]"
  print "Do not add extension to out file"
  print "Add +x at the end of a file to set executable bit"
  print "Directories are added recursively, files already added are skipped"
  print "Options:"
  print "  -autoexec    Detect and set executable file permissions automatically"
  quit()

if autoExec:
    print "Automatically detecting executables"

outFile = args[1]

print 'Creating tar archive'
out = tarfile.open(outFile + ".tar", mode='w')
        
for i in range(2, len(args)):
    isExec = False
    arg = args[i].replace("\\", "/")
    if arg.endswith("+x"):
        arg = arg[:-2]
        isExec = True
        executableFiles.add(arg)
    out.add(arg, filter=processFile)
    
out.close()

print 'Gzipping archive'
inFile = open(outFile + ".tar", mode='rb')
out = gzip.open(outFile + ".tar.gz", mode='w')

blockSize = 2048
for chunk in iter(partial(inFile.read, blockSize), ''):
    out.write(chunk)

out.close()
inFile.close()

print "Removing tar file"
os.remove(outFile + ".tar")

print "Done"