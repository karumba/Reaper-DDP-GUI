# Reaper-DDP-GUI
This script assists you in preparing a DDP in the Audio DAW "Reaper".
Refer to https://www.finemastering.de/downloads/ for more info.

REQUIREMENTS

The script is written in Python. Due to that, you need Python installed on your system. You can download Python v3.4 (recommended) here. Please make sure to install either the 32Bit or 64Bit version depending on the Reaper version you are using:
https://www.python.org/downloads/release/python-340/

NOTES

You have to place your items on the timeline yourself just as you would like to have them later on the CD, including the desired pause times.
The first item is not allowed to start earlier than “2 seconds + Pregap for tracks”. This is to ensure red book compatiblity.
All codes (EAN, ISRC) are checked for correct format.
Artist, album and song names are checked for unsupported CD-Text characters. The script will output a warning in that case.
You might want to consider Reaper-DDP-Marker-Editor coded by "WyattRice":
https://forum.cockos.com/showpost.php?p=2034321&postcount=476

I hope the script is useful for some of you. I’m open for comments & suggestions for improvement. Thanks!
