# Copyright (c) 2022 Jan "karumba" Ohlhorst, more info www.finemastering.de\downloads
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Version 1.13
# Download: https://www.finemastering.de/downloads/

#---------- Prepare Track 1 for DDP export -------------
import os, sys, math, re, string
from reaper_python import RPR_ShowConsoleMsg as log

#---------- default values -----------------------------
d_pregap = 0 # time in [ms] the marker will be placed before the item start
d_postgap = 0 # time in [ms] the marker will be placed after the item end
d_language = 'English'

#---------- init values -----------------------------
logString = '';

#---------- function declaration -----------------------
def check_allowed_genre(testGenre, logString):
	listOfGenres = ["Not Defined", "Adult Contemporary", "Alternative Rock", "Childrens' Music", "Classical", "Contemporary Christian", "Country", "Dance", "Easy Listening", "Erotic", "Folk", "Gospel", "Hip Hop", "Jazz", "Latin", "Musical", "New Age", "Opera", "Operetta", "Pop Music", "Rap", "Reggae", "Rock Music", "Rhythm & Blues", "Sound Effects", "Spoken Word", "World Music"]

	if (testGenre == ''):
		genreFound = 1;
	else:
		genreFound = 0;
		for genre in listOfGenres:
			if genre == testGenre:
				genreFound = 1;

		if (genreFound == 0):
			logString = logString + '\n\n!!! WARNING: Genre not found, see:\nhttps://www.gnu.org/software/libcdio/cd-text-format.html#Misc-Pack-Types\n'

	return (logString)

def check_allowed_chars(testString, logString):
	allowedChars=' !"$%&\'()*+,-./0123456789:<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
	for i in range(0,len(testString)):
		if testString[i] not in allowedChars:
			logString = logString + '\n\n!!! WARNING: ' + testString + ' contains non CD-TEXT chars!\n'
			break

	return (logString)
	
def check_ean(ean, logString):
	str_ean = str(ean)
	result = re.match('^[\d]{13}$', ean)
	
	if (str(result) == 'None'):
		logString = logString + '\n\n!!! WARNING: EAN format not correct! (EAN must be exactly a 13 digit number)\n'

	sum_odd = 0;
	sum_even = 0;
	for i in range(0,len(str_ean)-1):
		if ((i % 2) == 0):
			sum_odd = sum_odd + int(str_ean[i])
		if ((i % 2) == 1):
			sum_even = sum_even + int(str_ean[i])

		ean_crc = int(str_ean[-1])
		sum = (sum_odd+sum_even*3)
		ean_crc_calc = int(math.ceil(float(sum)/10)*10 - sum)

	if ean_crc != ean_crc_calc:
		logString = logString + '\n\n!!! WARNING: EAN CRC not correct!'
		logString = logString + '\n                   EAN CRC (given) = ' + ean[-1]
		logString = logString + '\n                   EAN CRC (should be) = ' + str(ean_crc_calc) + '\n'

	return (logString)

def check_isrc(isrc, logString):
	result = re.match('^[a-zA-Z]{2}[0-9a-zA-Z]{3}\d{2}\d{5}', isrc)

	if (str(result) == 'None'):
		logString = logString + '\n\n!!! WARNING: ISRC ' + str(isrc) + ' not correct!\n'

	return (logString)

def find_pattern(string, pattern):
	result = re.search(pattern + '=([^|]+)', string)

	if (str(result) != 'None'):
		return result.group(1)
	else:
		return ('')

def set_track_name(trackString, selTrack):
	RPR_GetSetMediaTrackInfo_String(selTrack, "P_NAME", trackString, True)


#---------- Main ---------------------------------------
def main(logString):
	RPR_Main_OnCommand(40297, 0) # unselect all tracks
	selTrack = RPR_GetTrack(0, 0) # get the first track
	RPR_SetTrackSelected(selTrack, 1) # select the first track
	
	string = RPR_GetSetMediaTrackInfo_String(selTrack, "P_NAME","", False)[3]
	
	pattern = 'PERFORMER'
	performer = find_pattern(string, pattern)
	pattern = 'ALBUM'
	album = find_pattern(string, pattern)
	pattern = 'SONGWRITER'
	songwriter = find_pattern(string, pattern)
	pattern = 'COMPOSER'
	composer = find_pattern(string, pattern)
	pattern = 'ARRANGER'
	arranger = find_pattern(string, pattern)
	pattern = 'MESSAGE'
	message = find_pattern(string, pattern)
	pattern = 'GENRE'
	genre = find_pattern(string, pattern)
	pattern = 'LANGUAGE'
	language = find_pattern(string, pattern)
	pattern = 'EAN'
	ean = find_pattern(string, pattern)
	pattern = 'PREGAP'
	pregap = find_pattern(string, pattern)
	pattern = 'POSTGAP'
	postgap = find_pattern(string, pattern)
	pattern = 'ISRC'
	isrc = find_pattern(string, pattern)
	
	if pregap == '':
		pregap = d_pregap

	if postgap == '':
		postgap = d_postgap

	if language == '':
		language = d_language

	# setting up the user input field
	names ='\
Pause at project start [sec]:,\
Pregap for tracks [ms]:,\
Postgap on last track [ms]:,\
Performer:,\
Album Title:,\
Composer:,\
Songwriter:,\
Arranger:,\
Message:,\
Genre:,\
Language Title:,\
EAN Code:,\
ISRC (12 chars):'

	defvalues = '2,' + str(pregap) + ',' + str(postgap) + ',' + performer + ',' + album + ',' + songwriter + ',' + composer + ',' + arranger + ',' + message + ',' + genre + ',' + language + ',' + ean + ',' + isrc; # default values
	
	maxreturnlen = 999         # one more than what you expect to get back
	nitems = len(defvalues.split(',')) # number of items in the dialog (6 in this case, but I left the counting in for future ease and because it's nice)
	Query = RPR_GetUserInputs('DDP Setup',nitems,names,defvalues,maxreturnlen) # call dialog and get result

	if Query[0] == 1: # user clicked OK
		UserValues = Query[4].split(',')          # the fourth item holds the input values
		pregap = float(UserValues[1])
		firstTrackSilence = float(UserValues[0]) + 0.000000 + pregap / 1000
		postgap = float(UserValues[2])
		performer = (UserValues[3])
		album = (UserValues[4])
		composer = (UserValues[5])
		songwriter = (UserValues[6])
		arranger = (UserValues[7])
		message = (UserValues[8])
		genre = (UserValues[9])
		language = (UserValues[10])
		ean = (UserValues[11])
		isrc = (UserValues[12])
		
		#Remove all markers:
		Marker = RPR_EnumProjectMarkers2(0, 0, 0, 0, 0, 0, 0) #(integer, proj, idx, is region, position, region end position, name, markerindexnumber)
		IDX = Marker[0]
		while IDX > 0:
			is_Region = Marker[3]
			MarkIdx = Marker[7]  # gets the last (seventh) item of the return array, the marker index number
			RPR_DeleteProjectMarker( 0, MarkIdx, is_Region)
			Marker = RPR_EnumProjectMarkers2(0, 0, 0, 0, 0, 0, 0)
			IDX = Marker[0]

		
		# check if start time of first item is > 2 seconds
		item = RPR_GetMediaItem(0, 0)
		#RPR_SetMediaItemInfo_Value(item, "B_UISEL", 1) # "physically" selects the first of the items.
		RPR_Main_OnCommand(40182, 0) # select all items
		item_start = RPR_GetMediaItemInfo_Value(item, "D_POSITION")         # getting the current item's start time to calculate nudge amount and direction.

		if item_start < firstTrackSilence:
			logString = logString + "\nERROR: First track needs a starting pause time of at least " + str(round(firstTrackSilence,3)) + " seconds (is now " + str(round(item_start, 3)) + " seconds)!"
		else:
			RPR_AddProjectMarker(0, 0, 0, 8, "!", 100 + 0) # add a "!" marker at zero position
			(track_name, selTrack, flags) = RPR_GetTrackState(selTrack, 0);

			trackString = ''
			returnFlag = 1

			logString = check_allowed_chars(performer,logString)
			logString = check_allowed_chars(album,logString)
			logString = check_allowed_chars(composer,logString)
			logString = check_allowed_chars(songwriter,logString)
			logString = check_allowed_chars(arranger,logString)
			logString = check_allowed_chars(message,logString)
			#logString = check_allowed_chars(genre,logString)
			logString = check_allowed_genre(genre,logString);
			logString = check_allowed_chars(language,logString)

			if performer == '':
				RPR_ShowMessageBox("WARNING: Performer not specified!", "Sorry", 0)
			else:
				trackString = trackString + '@PERFORMER=' + performer
				logString = logString + '\n==================================================='
				logString = logString + '\nPERFORMER = ' + performer

			if album == '':
				RPR_ShowMessageBox("WARNING: Album-Title not specified!", "Sorry", 0)
			else:
				trackString = trackString + '|ALBUM=' + album
				logString = logString + '\nALBUM-TITLE = ' + album

			if (composer != ''):
				trackString = trackString + '|COMPOSER=' + composer

			if (songwriter != ''):
				trackString = trackString + '|SONGWRITER=' + songwriter 

			if (arranger != ''):
				trackString = trackString + '|ARRANGER=' + arranger 

			if (message != ''):
				trackString = trackString + '|MESSAGE=' + message

			if (genre != ''):
				trackString = trackString + '|GENRE=' + genre 

			if (language != ''):
				trackString = trackString + '|LANGUAGE=' + language 

			if ean != '':
				logString = check_ean(ean, logString)
				trackString = trackString + '|EAN=' + ean
				logString = logString + '\nEAN = ' + ean

			# force LANGUAGE=English to avoid Eclipse error in pressing plants
			#trackString = trackString + '|LANGUAGE=English'
			#logString = logString + '\nLANGUAGE=English'
			
			#trackString = trackString + '|COMPOSER=Various|SONGWRITER=Various'
			#logString = logString + '\n|COMPOSER=Various\n|SONGWRITER=Various'

			logString = logString + '\n==================================================='

			if (isrc != ''):
				trackString = trackString + '|ISRC=' + isrc 

			RPR_AddProjectMarker(0, 0, 1, 8, trackString, 100 + 1) # add second marker with project infos, EAN, etc. from "track name" -> #@CD-Title|PERFORMER=XYZ|EAN=XYZ

			trackString = trackString + '|PREGAP=' + str(pregap) + '|POSTGAP=' + str(postgap)
			set_track_name(trackString, selTrack)

			Item_Count = RPR_CountSelectedMediaItems(0) # Get number of media items in current project
			#log('Item_Count = ' + str(Item_Count))
			ItemIndex = 0
			
			while ItemIndex < Item_Count: 
				item = RPR_GetSelectedMediaItem(0, ItemIndex)
				item_start = RPR_GetMediaItemInfo_Value(item, "D_POSITION") # getting the current item's start time
				item_length = RPR_GetMediaItemInfo_Value(item, "D_LENGTH")         # getting the current item's length
				
				active_take = RPR_GetActiveTake(item) # pointer to active take
				try:
					take_name = RPR_GetSetMediaItemTakeInfo_String(active_take, "P_NAME", "", False)[3] # gets name of active take
				except:
					logString = logString + '\nERROR: File name of item #' + str(ItemIndex+1) + ' contains unsupported characters!\n'
					return (1,logString)

				logString = check_allowed_chars(take_name,logString)

				marker_name = "#" + take_name # prefixes the take's name with "#". This will be the name of our "#" markers #Track-Name|ISRC=XYZ|PERFORMER=XYZ
				
				logString = logString + '\n#' + str(format(ItemIndex, '02d')) + ' ' + take_name
				logString = logString + " - " + str(math.floor(item_length/60)) + ":" + str( format(int((item_length) - (math.floor(item_length/60)*60)), '02d') )
				
				marker_name = marker_name + '|PERFORMER=' + performer
				
				# prepare isrc
				if isrc != '':
					isrc_prefix2    = re.search('(.{7}).*', isrc).group(1)
					isrc_increment2 = re.search('.{7}(.*)', isrc).group(1)
							
					isrc2 = str(isrc_prefix2) + str(format(int(isrc_increment2)+ItemIndex, '05d'))

					logString = check_isrc(isrc2, logString)
					marker_name = marker_name + '|ISRC=' + isrc2
					logString = logString + ' - ISRC: ' + isrc2

				position = item_start - (pregap/1000)
				position = round(position * 75) / 75 # quantize to [frames]
				
				if ItemIndex == 0:
					position = 2.000 # first marker at 2 seconds
									
				RPR_AddProjectMarker(0, 0, position, 8, marker_name, 100 + ItemIndex + 2) # puts "#" marker at first item's start.
				
				ItemIndex +=1 

			item_length = RPR_GetMediaItemInfo_Value(item, "D_LENGTH")         # getting the current item's length time
			position = item_start + item_length + (postgap/1000)
			position = round(position * 75) / 75 # quantize to [frames]
			RPR_AddProjectMarker(0, 0, position, 8, "!", 100 + ItemIndex + 2) # end marker = end + last item + postgap
		return (1,logString)
	else:
		return (0,logString)

#---------- Flow Control ---------------------------------
RPR_Undo_BeginBlock()
(returnValue,logString) = main(logString)

if returnValue > 0:
	log(logString)

RPR_Undo_EndBlock("Prepare markers for DDP",-1)


