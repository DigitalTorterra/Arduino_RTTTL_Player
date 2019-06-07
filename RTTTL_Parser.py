import openpyxl #a library for working with spreadsheets

class RTTTLSongs():
	def __init__(self):
		self.rtttl_dir = 'rtttl/'
		
		#Reading in frequencies from Excel in order to translate from "A6" to the frequency of that note
		#keys-dict which gives the value from the D6, etc.
		note_sheet = 'Note_Table.xlsx'
		wb = openpyxl.load_workbook(note_sheet)
		sheet = wb['Sheet1']
		data = sheet['A2:B49']
		self.keys = {}
		for item in data:
			self.keys[item[0].value] = item[1].value

	def read_song(self,filename,octave_offset=0):
		#read in the RTTTL file
		#example filename: 0071.txt
		#octave_offset: the number of octaves to go up or down
		with open(self.rtttl_dir+filename,'r') as f:
			song = f.readline()
		#parse the rtttl file
		song = song.replace('\n','') #remove newline character
		song = song.replace(' ','') #remove any spaces from the string
		
		#split the song up into sections
		sections = song.split(':')

		#begin parsing into songInfo
		songInfo = {}
		songInfo['Name'] = sections[0]
		
		parameters = sections[1].split(',')
		songInfo['Duration'] = int([i for i in parameters if 'd='in i][0][2:])
		songInfo['Octave'] = int([i for i in parameters if 'o='in i][0][2:])
		songInfo['Tempo'] = int([i for i in parameters if 'b='in i][0][2:])
		"""
		Durations
		1 - whole note
		2 - half note
		4 - quarter note
		8 - eighth note
		16 - sixteenth note
		32 - thirty-second note
		"""
		frequencies = []
		durations = []

		notes = sections[2].split(',')
		for note in notes:
			#parse the information
			letter_location = [i for (i,val) in enumerate(note.lower()) if val in 'abcdefgp'][0]
			
			#setting the duration key
			if letter_location != 0:
				duration_nums = int(note[:letter_location])
			else:
				duration_nums = songInfo['Duration']
			
			#calculates the duration of the note in milliseconds to store
			duration_millis = 240000/(duration_nums*songInfo['Tempo']) 
			if '.' in note:
				duration_millis *= 1.5
			durations.append(int(duration_millis))
			
			#setting the note letter, finding existence of #
			note_letter = note[letter_location].upper()
			
			#setting the octave
			if note[-1] in '0123456789':
				octave = int(note[-1])
			else:
				octave = songInfo['Octave']
			
			#finding the frequency
			if note_letter == 'P':
				frequencies.append(0)
			else:
				key = note_letter
				if '#' in note:
					key += '#'
				key += str(octave+octave_offset)
				frequencies.append(int(self.keys[key.upper()]))
		
		songInfo['Frequencies'] = frequencies
		songInfo['Durations'] = durations

		"""
		Structure of songInfo:
		Name-the name of the song
		Duration-the default duration of each note
		Octave-the default octave value
		Tempo-the beats per minute
		Frequencies-the list of frequencies for each note
		Durations-the list of durations for each note
		"""
		return(songInfo)
		
	def generateCode(self,songnames,offsets):
		#songnames: a list of song files-.txt not required
		#offsets: list of numbers to offset by
		#create a new file to write code to
		f = open('OutputCode.ino','w')
		f.write('#define NUM_SONGS '+str(len(songnames))+'\n\n')
		
		#important info to dump
		names = []
		frequencies = []
		durations = []
		
		for (i,songname) in enumerate(songnames):
			#read the data
			songInfo = self.read_song(songname+'.txt',offsets[i])
			
			#extract the relevant data
			names.append(songInfo['Name'])
			frequencies.append(songInfo['Frequencies'])
			durations.append(songInfo['Durations'])
		
		#generate the list of song names
		song_names_c = 'char *song_names[] = {'
		for (i,name) in enumerate(names):
			song_names_c += '"'+name+'"'
			if i != len(names) - 1:
				song_names_c += ','
			else:
				song_names_c += '};\n\n'
		f.write(song_names_c)
		
		#generate lists of frequencies and durations for each song
		for (i,name) in enumerate(names):
			#handling frequencies
			frequency_list_c = 'const int '+name+'_frequency[] = {'
			for (j,frequency) in enumerate(frequencies[i]):
				frequency_list_c += str(frequency)
				if j != len(frequencies[i])-1:
					frequency_list_c += ','
				else:
					frequency_list_c += '};\n'
			
			#handling durations
			duration_list_c = 'const int '+name+'_duration[] = {'
			for (j,duration) in enumerate(durations[i]):
				duration_list_c += str(duration)
				if j != len(durations[i])-1:
					duration_list_c += ','
				else:
					duration_list_c += '};\n'
			f.write(frequency_list_c)
			f.write(duration_list_c)
		
		f.write('\n//This part will always contain the same arrays')
		
		#generate the master lists of frequency and duration
		frequency_list_c = '\nconst int *frequencies[] = {'
		duration_list_c = '\nconst int *durations[] = {'
		for (i,name) in enumerate(names):
			frequency_list_c += name+'_frequency'
			duration_list_c += name+'_duration'
			if i != len(names) - 1:
				frequency_list_c += ','
				duration_list_c += ','
			else:
				frequency_list_c += '};'
				duration_list_c += '};'
		f.write(frequency_list_c)
		f.write(duration_list_c)
		
		#generate a list of the lengths of each song
		length_list_c = '\nconst int song_lengths[] = {'
		for (i,freq) in enumerate(frequencies):
			length_list_c += str(len(freq))
			if i != len(frequencies) - 1:
				length_list_c += ','
			else:
				length_list_c += '};'
		f.write(length_list_c)
			
		
		f.close()
		
#Modify these two lines to change the output songs!
songs = ['adams','Mission Impossible','NDFightSong','beethoven']
offsets = [0,-1,0,0]
		
#initialize the class and have it generate code for the given songs
converty = RTTTLSongs()
converty.generateCode(songs,offsets)
