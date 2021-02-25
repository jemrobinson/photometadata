# Photometadata
Simple scripts to check for consistent EXIF metadata in photos and correct some common issues.


## Check
Check for consistent EXIF data.

```
USAGE
  python application.py check <path>

ARGUMENTS
  <path>                 Location to look for photos under

GLOBAL OPTIONS
  -h (--help)            Display this help message
  -q (--quiet)           Do not output any message
  -v (--verbose)         Increase the verbosity of messages: "-v" for normal output, "-vv" for more verbose output and "-vvv" for debug
  -V (--version)         Display this application version
  --ansi                 Force ANSI output
  --no-ansi              Disable ANSI output
  -n (--no-interaction)  Do not ask any interactive question
```

## Classify
Classify photos according to their contents using Azure Computer Vision.
Note that this requires a **Microsoft Azure** subscription.

```
USAGE
  python application.py classify <path>

ARGUMENTS
  <path>                 Location to look for photos under

OPTIONS
  -s (--settings)        If set, load settings from the specified YAML file (default: "settings.yaml")

GLOBAL OPTIONS
  -h (--help)            Display this help message
  -q (--quiet)           Do not output any message
  -v (--verbose)         Increase the verbosity of messages: "-v" for normal output, "-vv" for more verbose output and "-vvv" for debug
  -V (--version)         Display this application version
  --ansi                 Force ANSI output
  --no-ansi              Disable ANSI output
  -n (--no-interaction)  Do not ask any interactive question
```

## Fix
Fix inconsistent EXIF data.

```
USAGE
  python application.py fix [-f] [-s <...>] <path>

ARGUMENTS
  <path>                 Location to look for photos under

OPTIONS
  -f (--filename)        If set, the date stored in the filename will be used in case of conflict
  -s (--settings)        If set, load settings from the specified YAML file (default: "settings.yaml")

GLOBAL OPTIONS
  -h (--help)            Display this help message
  -q (--quiet)           Do not output any message
  -v (--verbose)         Increase the verbosity of messages: "-v" for normal output, "-vv" for more verbose output and "-vvv" for debug
  -V (--version)         Display this application version
  --ansi                 Force ANSI output
  --no-ansi              Disable ANSI output
  -n (--no-interaction)  Do not ask any interactive question
```

## Settings

### Azure
The secrets needed to connect to Azure computer vision should be stored in the settings file

```yaml
azure:
  endpoint: https://cv-98c13140-692e.cognitiveservices.azure.com/  # name of the endpoint to use
  subscription_key: 6c56389abe524a8aa6c8b1c74f7b704d               # key for the endpoint
```

### Copyright
The copyright notice can be extracted using a set of rules encoded in YAML.
For each `name`d individual, if any of their rules are matched, the copyright will be assigned to them

```yaml
copyright:
  - name: Thomas Edison
    whenever:
      - filename-regex: Thomas-DSCN\d\d\d\d.jpg  # match files of this type
      - filename-regex: TEdison-.*               # ... or of this type
  - name: Katharine Hepburn
    whenever:
      - Camera: KODAK PIXPRO FZ152               # match any photos taken with this camera
      - EXIF Flash: Flash fired                  # ... or where flash is used
      - filename-regex: .*KH.jpg                 # ... or matching this regex
```