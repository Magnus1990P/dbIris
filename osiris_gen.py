#!/usr/bin/python
#-*- coding: utf8 -*-

################################################################################
##	Imports
################################################################################
import 	sys
import 	subprocess
import 	re
import 	os.path
import 	os
import 	glob
from		PIL import Image
from		time import sleep

################################################################################
##	Variables
################################################################################
BASEPATH			= "/development/dbIris/"
scriptPath 		= BASEPATH + "osiris_conf/"
orgImgPath 		= BASEPATH + "db_periocular/"
curFileImg		= BASEPATH + "osiris_current_img.txt"
confType			= "SMALL"
imageCounter	= 0
imageFails		= 0
fileListName	= ""
regExp 				= {'ERROR':re.compile("Segmentation|fault|Error|" + 	#
																		"error|ERROR|SIGKILL|" 			+		#
																		"cannot|Cannot"),								#
					 			 'WARNING':re.compile("Warning|warning|WARNING")}		#


################################################################################
##	Validate parameters
################################################################################
if len( sys.argv ) != 2:																			#
	print "Incorrect amount of parameters, eg. ",								#
	print	"'./osiris_gen.py img_list.dev.txt'"									#
	exit()																											#

fileListName = str( sys.argv[1] )															#Grab list name

currentImage	= open( curFileImg, "r+" )											#rw cur img
currentImage.truncate( )																			#remove file

imageList 		= open( fileListName, "r" )											#Read images
print "Converting images in list: " + fileListName						#Status msg


################################################################################
## Loop through the images in list
################################################################################
for image in imageList.readlines( ):													#
	osirisResult	= "FAIL"
	osirisOutput 	= ""																					#Reset output
	configNumber	= 0																						#Reset config num
	imageCounter	= imageCounter + 1														#inc counter
	image 				= image.rstrip("\n")[len(orgImgPath):]				#Rm trailing chars
	
	im						=	Image.open( orgImgPath + image )						#Grab image size
	width					= im.size[0]
	height				= im.size[1]

	currentImage.seek(  0 )																#Start of file
	currentImage.write( image )														#Write filename to file

	##############################################################################
	## Try each config
	##		If config fails try the next config file
	##		If no error occurs proceed
	##############################################################################
	while configNumber < 3 and osirisResult == "FAIL":
		cmd = None;
		if configNumber == 0:
			cmd 			= [	"./osiris.exe", scriptPath + "osiris_sm.conf"]
			confType= "SMALL"																				#

		elif configNumber == 1:		
			cmd 			= [	"./osiris.exe", scriptPath + "osiris_nm.conf"]
			confType= "MEDIUM"																			#

		elif configNumber == 2:
			cmd 			= [	"./osiris.exe", scriptPath + "osiris_lg.conf"]
			confType	= "LARGE"																			#

		############################################################################
		##	Try to execute OSIRIS on current image
		############################################################################
		try:																												#Process the
			if cmd is not None:
				osirisOutput = subprocess.check_output(cmd, 							#	image using
																				stderr=subprocess.STDOUT)	#	OSIRIS
		except subprocess.CalledProcessError as e:									#If failure
			osirisResult	= "FAIL"																		#	Set result   
		
		############################################################################
		##	Check to see if failure was detected
		############################################################################
		if regExp['ERROR'].search( osirisOutput ) is None:
			osirisResult = "SUCCESS"																	
		else:
			osirisResult = "FAIL"
		
		configNumber = configNumber + 1; 														#Inc number

	######### LOOP CONFIGURATIONS STOPPED ########

	if osirisResult == "FAIL":																		#If fail
		imageFails = imageFails + 1																	#	inc count

	#Write result to file
	currentImage.truncate( )																			#Truncate file

	##############################################################################
	##	Print current state of program
	##############################################################################
	print str(imageCounter)	+	"\t"	+ str(image),									#Print status
	print " - " + str(configNumber) + "/", 				 								#	message
	print str(confType) 	+ " - " 	+ osirisResult								#
	
	if imageCounter % 50 == 0:																		#Print status
		print "Fails: " + str(imageFails) + "/" + str(imageCounter)	#	message

######### LOOP STOPPED ########


currentImage.close(  )																					#Close file


################################################################################
## Print final status message
################################################################################
print
print
print "STATUS: "	+	str(imageCounter	-	imageFails) +	"/"	+	str(imageCounter)
print
print

