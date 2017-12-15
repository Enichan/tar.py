# tar.py
Utility for creating Linux tar.gz archives with proper file permissions (executable bit set) on Windows

```
Usage: tar.py [out] [file1] [file2] ... [fileN]
Do not add extension to out file
Add +x at the end of a file to set executable bit
Directories are added recursively, files already added are skipped
Options:
  -autoexec    Detect and set executable file permissions automatically
```

## Examples

__Compress a directory test to thing.tar.gz__

```python tar.py thing test```

__Compress a directory myapp with various executables to myapp100.tar.gz__

```python tar.py -autoexec myapp100 myapp```

__Compress a readme.txt and executable run.sh file to stuff.tar.gz__

```python tar.py stuff readme.txt run.sh+x```

__Compress a directory payload with executable run.sh file to blah.tar.gz__

```python tar.py blah run.sh+x payload```

Note that run.sh+x must come before the directory so that it is skipped when encountered
