#!/usr/bin/python
#-*- coding: utf8 -*-
#Generates the lists used by matlab

from 		os.path			import isfile
import 	sys

################################################
##	VALIDATION OF PARAMETERS
################################################
if len( sys.argv ) != 5:
	print "Incorrect amount of parameters, eg. ./gen_imgdb.py filelist base_dir output number_of_lists"
	exit()


################################################
##	VARIABLES
################################################
FNAME		= sys.argv[1]									#Store filename to read from
BDIR		= sys.argv[2]									#Base dir to images
OUTPUT	=	sys.argv[3]									#Output file
LISTNUM	=	sys.argv[4]									#Number of lists to be generated

DB		= 0														#DB counter
pDB		= DB
CL		= 0														#Current Length of read string

################################################
##	FILE INITIATION
################################################
WF = open( OUTPUT, 'w' )							#Open write file
WF.seek( 0 )													#	Go to start of file
WF.truncate()													#	Delete its content

RF = open( FNAME, 'r' )								#Open read file with images in
IL = RF.read().split("\n")						#Read entire file into memory and split
RF.close()														#close file


################################################
##	Loop through all filenames in file
################################################
for line in IL:																#For each line in image list file 

	################################################
	##	IF length of string has changed (new list)
	################################################
	if CL != len( line ) :											#If change in string length
		DB = DB + 1																#Increment DB counter
		if DB != pDB:															#If chLQ images is starting
			pDB = DB																#Update comparison variable
			if DB > 1:															#Add close from 2nd list
				WF.write( '];\n\n' )									#		Write closing tag
			if DB <= LISTNUM:												#Start new list
				WF.write( 'imgList_' + DB + ' = [\n')	#		Write opening tag
		CL = len( line )													#Update current string length

	##################################################
	##	If this is the end of file (blank line at EOF)
	##################################################
	if len( line ) == 0 and DB >= LISTNUM:	#If length = 0 (last line) and at end
		WF.write( '];\n\n' )									#		finish the writin
		WF.close()
		exit()

	##########################################################
	##	If in list
	##########################################################
	else:																#If not last line
																			#Create skeleton name
		SN = "img_processed/" + line[ line.rfind('/')+1 : line.rfind('.')]
																			#Check if file exists
		if	isfile( SN+'_segm.bmp' ) 	is True and \
				isfile( SN+'_mask.bmp' ) 	is True and \
				isfile( SN+'_para.txt' ) 	is True and \
				isfile( BDIR + line ) 		is True:
			WF.write( "\t'" + str(line) + "';\n" )	#Write to file
		else:
			print "NOT FOUND: " + str(line)

WF.close()														#Close write file



