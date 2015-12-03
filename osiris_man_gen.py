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
from 		PIL	 import	Image, ImageDraw
import	MySQLdb
import	base64
import	json
import	math

################################################################################
##	Variables
################################################################################
BASEPATH			= "/development/dbIris/"
scriptPath 		= BASEPATH + "osiris_conf/osiris_man_param.conf"
orgImgPath 		= BASEPATH + "db_periocular/"
parImgPath 		= BASEPATH + "man_parameters/"
curFileImg		= BASEPATH + "osiris_current_img.txt"
imageCounter	= 0
imageFails		= 0
regExp 				= {'ERROR':re.compile("Segmentation|fault|Error|" + 	#
																		"error|ERROR|SIGKILL|" 			+		#
																		"cannot|Cannot"),								#
					 			 'WARNING':re.compile("Warning|warning|WARNING")}		#
cmd 					= [	"./osiris.exe", scriptPath ]
confType			= "MANUAL"																					#
green					= (0, 255, 0)

################################################################################
##	Sort coordinates in the order right to left
################################################################################
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
##	Draw circles around pupil and iris, then save to ./test/
################################################################################
def drawCircles( fname, cX, cY, rP, rI ):
	sname 		= parImgPath + fname[ fname.rfind("/")+1 : -4 ] + "_segm.bmp"
							#left    top   Right  Bottom
	boxPupil	= [cX-rP, cY-rP, cX+rP, cY+rP ]
	boxIris		= [cX-rI, cY-rI, cX+rI, cY+rI ]

	im 				= Image.open( fname ).convert("LA").convert("RGB")
	size = im.size
	draw			= ImageDraw.Draw(im)
	draw.ellipse(boxPupil, 	outline=green )
	draw.ellipse(boxIris, 	outline=green )
	del draw
	im.save( sname )

	sname 		= parImgPath + fname[ fname.rfind("/")+1 : -4 ] + "_mask.bmp"
	im 				= Image.new("RGB", size, "black")
	draw			= ImageDraw.Draw( im )
	draw.ellipse(boxIris, 	fill=(255,255,255) )
	draw.ellipse(boxPupil, 	fill=(0,0,0) )
	del draw
	im.save( sname )	

	return


################################################################################
##	Draw circles around pupil and iris, then save to ./test/
################################################################################
def calcPoints(cX, cY, R, N):
	print "\tCalculating coordinates: ",
	inc = (2*math.pi) / N
	pts = [ cX-R, cY, 0 ]
	a = inc
	while a < 2*math.pi:
		tX = int( cX + R * math.cos( a ) )
		tY = int( cY + R * math.sin( a ) )
		tA = math.atan2( (tY-cY), (tX-cX) )
		if tA < 0:
			tA = 2*math.pi + tA
		pts.extend( [tX, tY, tA] )
		a = a + inc
	print "\tcoordinates calculated"
	return pts


################################################################################
##	Draw circles around pupil and iris, then save to ./test/
################################################################################
def calcParams( fname, cX, cY, rP, rI ):
	sname 			= parImgPath + fname[ fname.rfind("/")+1 : -4 ] + "_para.txt"
	circPupil 	= 2 * rP * math.pi
	circIris		= 2 * rI * math.pi
	pointsPN		= int( circPupil/3 );
	pointsIN		= int( circIris/3 );

	if pointsPN > 125:
		pointsPN	= 125
	if pointsIN > 200:
		pointsIN	= 200

	ptsP = calcPoints(cX, cY, rP, pointsPN)
	ptsI = calcPoints(cX, cY, rI, pointsIN)

	print "\tWriting parameters to file: " + str(sname)
	f = open( sname, "w" );
	f.write( str(pointsPN) + "\n" + str(pointsIN) + "\n" )
	
	for p in ptsP:
		f.write( str(p) + " " )
	f.write("\n" )

	for p in ptsI:
		f.write( str(p) + " " )
	
	f.close()
	print "\tParameters written"
	





################################################################################
##	Validate parameters
################################################################################
currentImage	= open( curFileImg, "r+" )											#rw cur img
currentImage.truncate( )																			#remove file

db 		= MySQLdb.connect(host="localhost", user="root", passwd="toor", db="webIIC")
cur 	= db.cursor()
cur.execute("SELECT AID, ORG, COORD FROM image WHERE COORD!='' LIMIT 5")



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

	currentImage.seek(  0 )															#Start of file
	currentImage.write( image )													#Write filename to file
	coords = sortCoords( data[2] )											#Sort coordinates

	rP		= (int( coords[0]['X'] ) - int( coords[1]['X'] ) ) / 2
	cX		=  int( coords[0]['X'] ) - rP
	cY		=	 int( coords[0]['Y'] ) 
	rI		= (cX - int(coords[2]['X']))

	drawCircles( data[1], cX, cY, rP, rI )							#Gen BW img w/green circle
	calcParams(  data[1], cX, cY, rP, rI )							#Calc points on circle

	print "\tgenerating osiris_config"
	cOrgCont = open(scriptPath + ".org", "r").read()
	cCur = open(scriptPath, "w")
	cCur.write(cOrgCont)
	cCur.write("\n")
	cCur.write("Minimum diameter for pupil = " + str((2*rP)-5) + "\n")
	cCur.write("Maximum diameter for pupil = " + str((2*rP)+5) + "\n")
	cCur.write("Minimum diameter for iris  = " + str((2*rI)-5) + "\n")
	cCur.write("Maximum diameter for iris  = " + str((2*rI)+5) + "\n")
	cCur.close();
	print "\tgenerated"

	print "\tRunning OSIRIS v4.1 on current image"

	try:																												#Process the
		osirisOutput = subprocess.check_output(cmd, 							#	image using
															stderr=subprocess.STDOUT)				#	OSIRIS
	except subprocess.CalledProcessError as e:									#If failure
		osirisResult	= "FAIL"																		#	Set result   

	if regExp['ERROR'].search( osirisOutput ) is None:
		osirisResult = "SUCCESS"																	# occured
	else:
		osirisResult = "FAIL"
	if osirisResult == "FAIL":																	#If fail
		imageFails = imageFails + 1																#	inc count

	print "\tOSIRIS v4.1 finished"

	#Write result to file
	currentImage.truncate( )																		#Truncate file

	print str(imageCounter)	+	"\t"	+ str(image),								#Print status
	print str(confType) 
	print ""
	
######### LOOP STOPPED ########

currentImage.close(  )																						#Close file


