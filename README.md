# Lotlinx
Lotlinx test application for submitting photo URLs to the PhotoAI optimizer

USAGE:
./optimize_photos.py -h
usage: optimize_photos [-h] [-f FILE] [-t TIMEOUT] [-u USERNAME] [-p PASSWORD]
                       [-d DEALER] [-o DIR]
                       [URL [URL ...]]

Submit photos to the LotLinx PhotoAI optimizer

positional arguments:
  URL                   1 or more URLs to images. Required if -f/--file is not
                        used

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  input file containing a list of URLs to process
  -t TIMEOUT, --timeout TIMEOUT
                        timeout to control how long the program should wait to
                        download files in seconds
  -u USERNAME, --username USERNAME
                        username for PhotoAI
  -p PASSWORD, --password PASSWORD
                        password for PhotoAI
  -d DEALER, --dealer DEALER
                        dealer number/name
  -o DIR, --output DIR  output directory


NOTES:
if -f,--file parameter and URL parameters are absent the optimize_photos.py script
is able to accept a redirect from stdin

The format of the file when the FILE option is used should be a list of URLs, with one URL on each line.

Thus:
./optimize_photos.py  -d \<dealer\> -t \<timeout\> -p \<password\> -u \<username\>  -o \<output directory\> -f \<URL file\>

is equivalent to

./optimize_photos.py  -d \<dealer\> -t \<timeout\> -p \<password\> -u \<username\>  -o \<output directory\>  \<  \<URL file\>
