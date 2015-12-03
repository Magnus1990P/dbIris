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
orgImgPath 		= BASEPATH + "db_periocular/"
savImgPath 		= BASEPATH + "img_processed/"
savImgPath 		= BASEPATH + "man_parameters/"
imageCounter	= 0
green					= (0, 255, 0)

################################################################################
##	Sort coordinates in the order right to left
################################################################################
def sortCoords( D ):
	print "\tSorting coordinates",
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
	print "\t\t\tDone with sorting"

	return coord


################################################################################
##	Draw circles around pupil and iris, then save to folder
################################################################################
def drawCircles( fname, cX, cY, rP, rI ):
	sname 		= savImgPath + fname[ fname.rfind("/")+1 : fname.rfind(".")  ] + "_segm.bmp"
							#left    top   Right  Bottom
	boxPupil	= [cX-rP, cY-rP, cX+rP, cY+rP ]
	boxIris		= [cX-rI, cY-rI, cX+rI, cY+rI ]

	print "\tDrawing pupil and iris circle image",
	im 				= Image.open( fname ).convert("LA").convert("RGB")
	size 			= im.size
	draw			= ImageDraw.Draw(im)
	draw.ellipse(boxPupil, 	outline=green )
	draw.ellipse(boxIris, 	outline=green )
	del draw
	im.save( sname )
	print "\tDone drawing circle"

	print "\tGenerating binary mask for image",
	sname 		= savImgPath + fname[ fname.rfind("/")+1 : fname.rfind(".")  ] + "_mask.bmp"
	im 				= Image.new("RGB", size, "black")
	draw			= ImageDraw.Draw( im )
	draw.ellipse(boxIris, 	fill=(255,255,255) )
	draw.ellipse(boxPupil, 	fill=(0,0,0) )
	del draw
	im.save( sname )	
	print "\tDone drawing circle"

	return


################################################################################
##	Calculate points along circumference of the eye
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
	print "\t\tcoordinates calculated"
	return pts


################################################################################
##	Draw circles around pupil and iris, then save to folder
################################################################################
def calcParams( fname, cX, cY, rP, rI ):
	sname 			= savImgPath + fname[ fname.rfind("/")+1 : fname.rfind(".") ] + "_para.txt"
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

	print "\tWriting parameters to file: ",
	f = open( sname, "w" );
	f.write( str(pointsPN) + "\n" + str(pointsIN) + "\n" )
	
	for p in ptsP:
		f.write( str(p) + " " )
	f.write("\n" )

	for p in ptsI:
		f.write( str(p) + " " )
	
	f.close()
	print "\t\tParameters written"
	




################################################################################
##	Validate parameters
################################################################################
db 		= MySQLdb.connect(host="localhost", user="root", passwd="toor", db="webIIC")
cur 	= db.cursor()
cur.execute("SELECT AID, ORG, COORD FROM image WHERE COORD!=''")



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

	coords = sortCoords( data[2] )											#Sort coordinates

	rP		= (int( coords[0]['X'] ) - int( coords[1]['X'] ) ) / 2
	cX		=  int( coords[0]['X'] ) - rP
	cY		=	 int( coords[0]['Y'] ) 
	rI		= (cX - int(coords[2]['X']))

	drawCircles( data[1], cX, cY, rP, rI )							#Gen BW img w/green circle
	calcParams(  data[1], cX, cY, rP, rI )							#Calc points on circle

	print str(imageCounter)	+	"\t"	+ str(image),								#Print status
	print ""
	print ""
######### LOOP STOPPED ########


