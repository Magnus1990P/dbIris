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
from 		PIL	 import	Image, ImageDraw
from		time import sleep
import	MySQLdb
import	base64
import	json
import cv2

################################################################################
##	Variables
################################################################################
BASEPATH			= "/development/dbIris/"
scriptPath 		= BASEPATH + "osiris_conf/osiris_man_param.conf"
orgImgPath 		= BASEPATH + "db_periocular/"
parImgPath 		= BASEPATH + "man_parameters/"
saveFile			= BASEPATH + "osiris_processed_imgs.txt"
curFileImg		= BASEPATH + "osiris_current_img.txt"
imageCounter	= 0
imageFails		= 0
regExp 				= {'ERROR':re.compile("Segmentation|fault|Error|" + 	#
																		"error|ERROR|SIGKILL|" 			+		#
																		"cannot|Cannot"),								#
					 			 'WARNING':re.compile("Warning|warning|WARNING")}		#


################################################################################
##	Validate parameters
################################################################################
processedFile = open( saveFile, 	"a"  )											#w processed imgs
currentImage	= open( curFileImg, "r+" )											#rw cur img
currentImage.truncate( )																			#remove file

processedFile.write("---%%%%----\tNEW RUN\t\t---%%%---\n")

db 		= MySQLdb.connect(host="localhost", user="root", passwd="toor", db="webIIC")
cur 	= db.cursor()
cur.execute("SELECT AID, ORG, COORD FROM image WHERE COORD!=''")


def sortCoords( D ):
	coord = json.loads( base64.b64decode( D ) )

	if int(coord[2]['X']) > int( coord[0]['X'] ):
		c 				= coord[2]
		coord[2]	= coord[0]
		coord[0]	= c
	
	if int(coord[2]['X']) > int(coord[1]['X']):
		c 				= coord[2]
		coord[2]	= coord[1]
		coord[1]	= c
	
	if int(coord[1]['X']) > int(coord[0]['X']):
		c 				= coord[1]
		coord[1]	= coord[0]
		coord[0]	= c

	return coord


################################################################################
## Loop through the images in list
################################################################################
for data in cur.fetchall( ):													#
	osirisResult	= "FAIL"
	osirisOutput 	= ""																					#Reset output
	imageCounter	= imageCounter + 1														#inc counter
	image 				= data[1].rstrip("\n")[len(orgImgPath):]			#Rm trailing chars

	print imageCounter,
	print image

	currentImage.seek(  0 )																			#Start of file
	currentImage.write( image )														#Write filename to file

	coords = sortCoords( data[2] )

	pRad	= (int( coords[0]['X'] ) - int( coords[1]['X'] ) ) / 2
	pCX		= int( coords[0]['X'] ) - pRad
	pCY		=	int( coords[0]['Y'] ) 
	iRad	= (pCX - int(coords[2]['X']))
	
	im 		= Image.open( data[1] ).convert("LA").convert("RGB")
	draw	= ImageDraw.Draw(im)
	draw.ellipse([pCX-pRad,pCY-pRad, pCX+pRad, pCY+pRad], outline=(0,255,0))
	draw.ellipse([pCX-iRad,pCY-iRad, pCX+iRad, pCY+iRad], outline=(0,255,0))
	
	del draw
	
	print "./img_processed/"+image[image.rfind("/")+1:]

	break

	##############################################################################
	## Try config
	##############################################################################
	cmd 			= [	"./osiris.exe", scriptPath ]
	confType= "MANUAL"																					#

	############################################################################
	##	Try to execute OSIRIS on current image
	############################################################################
	try:																												#Process the
		if cmd is not None:
			osirisOutput = subprocess.check_output(cmd, 						#	image using
																		stderr=subprocess.STDOUT)	#	OSIRIS
	except subprocess.CalledProcessError as e:									#If failure
		osirisResult	= "FAIL"																		#	Set result   
		
	if regExp['ERROR'].search( osirisOutput ) is None:
		osirisResult = "SUCCESS"																	# occured
	else:
		osirisResult = "FAIL"
		
	if osirisResult == "FAIL":																		#If fail
		imageFails = imageFails + 1																	#	inc count

	#Write result to file
	processedFile.write( str( image ) + "\n" )										#Write result
	currentImage.truncate( )																			#Truncate file

	print str(imageCounter)	+	"\t"	+ str(image),							#Print status
	print " - " + str(configNumber) + "/", 				 						#	message
	print str(confType) 	+ " - " 	+ osirisResult						#
	
	if imageCounter % 50 == 0:																			#Print status
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

