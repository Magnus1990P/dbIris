#!/usr/bin/python
#-*- coding: utf8 -*-

################################################################################
##	Imports
################################################################################
import sys
import subprocess
import re
import os.path

################################################################################
##	Variables
################################################################################
scriptPath 		= "/development/dbIris/osiris_conf/"
orgImgPath 		= "/development/dbIris/db_periocular/"
saveFile			= "./osiris_processed_imgs.txt"
curFileImg		= "./osiris_current_img.txt"
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
if len( sys.argv ) != 3:																			#
	print "Incorrect amount of parameters, eg. ",								#
	print	"'./osiris_gen.py img_list.dev.txt server'"						#
	exit()																											#

fileListName = str( sys.argv[1] )

if sys.argv[2].lower() == 'server':														#If server
	scriptPath = "/home/jollyjackson/Desktop/iris_qa/"					#	path to configs
	orgImgPath = "/home/jollyjackson/Development/iris_img_db/"	#	path to images
	
processedFile = open( saveFile, 	"a"  )											#w processed imgs
currentImage	= open( curFileImg, "r+" )											#rw cur img
currentImage.truncate( )																			#remove file

imageList 		= open( fileListName, "r" )											#Read images
print "Converting images in list: " + fileListName						#Status msg
processedFile.write("---%%%%----\tNEW RUN\t\t---%%%---\n")

################################################################################
## Loop through the images in list
################################################################################
for image in imageList.readlines( ):													#
	osirisResult	= "FAIL"
	osirisOutput 	= ""																					#Reset output
	configNumber	= 0																						#Reset config num
	imageCounter	= imageCounter + 1														#inc counter
	image 				= image.rstrip("\n\0\r\t")[len(orgImgPath):]	#Rm trailing chars
	
	#print str(imageCounter) + ":\t" + str(image)					#Print image title

	currentImage.seek(  0 )																#Start of file
	currentImage.write( image )														#Write filename to file

	##############################################################################
	## Try each config
	##		If config fails try the next config file
	##		If no error occurs proceed
	##############################################################################
	while configNumber < 3 and osirisResult == "FAIL":							#Loop configs
		if configNumber == 0:																					#Try config
			cmd 			= [	"./osiris.exe", scriptPath + 									#	for small
										"dev_osiris_sm.conf"]													#	irises<F10>
			confType= "SMALL"																						#

		elif configNumber == 1:																				#Try config
			cmd 			= [	"./osiris.exe", scriptPath + 									#	for normal
										"dev_osiris_nm.conf"]													#	irises
			confType= "MEDIUM"																					#

		elif configNumber == 2:																				#Try config
			cmd 			= [	"./osiris.exe", scriptPath + 									#	for large
										"dev_osiris_lg.conf"]													#	irises
			confType	= "LARGE"																					#

		############################################################################
		##	Try to execute OSIRIS on current image
		##
		############################################################################
		try:																													#Process the
			osirisOutput = subprocess.check_output(cmd, 								#	image using
																				stderr=subprocess.STDOUT)	#	OSIRIS
		except subprocess.CalledProcessError as e:										#If failure
			osirisResult	= "FAIL"																			#Set result   
		
		if regExp['ERROR'].search( osirisOutput ) is None:						#If no errors
			osirisResult = "SUCCESS"																		# occured

		configNumber = configNumber + 1; 															#Inc number
	#LOOP CONFIGURATIONS

	if osirisResult == "FAIL":																			#If fail
		imageFails = imageFails + 1																		#	inc count

	#Write result to file
	processedFile.write( str( image ) + "\n" )											#Write result
	currentImage.truncate( )																				#Truncate file

	print str(imageCounter)	+	"\t"	+ str(image),							#Print status
	print " - " + str(configNumber) + "/", 				 						#	message
	print str(confType) 	+ " - " 	+ osirisResult						#	
	
	if imageCounter % 20 == 0:																			#Print status
		print "Fails: " + str(imageFails) + "/" + str(imageCounter)		#	message

######### LOOP STOPPED ########


currentImage.close(  )																						#Close file
processedFile.close( )																						#Close file


################################################################################
## Print final status message
################################################################################
print
print
print "STATUS: "	+	str(imageCounter	-	imageFails) +	"/"	+	str(imageCounter)
print
print

