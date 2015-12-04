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
imageCounter	= 0
green					= (0, 255, 0)

################################################################################
##	Sort coordinates in the order right to left
##		@param: D - JSON formatted string encoded with base64
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
##		@param:	fname - filename for image 
##		@param: cX & cY coordinates of circles centrum
##		@param:	rP - radius of pupil circle
##		@param:	rI - radius of iris circle
################################################################################
def drawCircles( fname, cX, cY, rP, rI ):
	sname 		= savImgPath + fname[ fname.rfind("/")+1 : fname.rfind(".")  ] \
							+ "_segm.bmp"
							#left    top   Right  Bottom
	boxPupil	= [cX-rP, cY-rP, cX+rP, cY+rP ]							#Create box for pupil
	boxIris		= [cX-rI, cY-rI, cX+rI, cY+rI ]							#	and iris

	print "\tDrawing pupil and iris circle image",
	im 				= Image.open( fname ).convert("LA").convert("RGB")	#open image in
																																# BW
	size 			= im.size																						#grab img size
	draw			= ImageDraw.Draw(im)																#Start drawing
	draw.ellipse(boxPupil, 	outline=green )												# draw iris &
	draw.ellipse(boxIris, 	outline=green )												# pupil border
	del draw																											# delete draw
	im.save( sname )																							#save new img
	print "\tDone drawing circle"

	print "\tGenerating binary mask for image",
	sname 		= savImgPath + fname[ fname.rfind("/")+1 : fname.rfind(".")  ] \
							+ "_mask.bmp"
	im 				= Image.new("RGB", size, "black")								#fill with black
	draw			= ImageDraw.Draw( im )													# draw
	draw.ellipse(boxIris, 	fill=(255,255,255) )							# Fill iris	w/white
	draw.ellipse(boxPupil, 	fill=(0,0,0) )										# Fill pupil w/black
	del draw																									#
	im.save( sname )																					#save mask to file
	print "\tDone drawing circle"

	return


################################################################################
##	Calculate points along circumference of the eye
##		@param: cX & cY coordinates of circles centrum
##		@param:	R - radius of circle
##		@param:	N - number of points to
################################################################################
def calcPoints(cX, cY, R, N):
	print "\tCalculating coordinates: ",
	inc = (2*math.pi) / N													#Calc incremental number for phi
	pts = [ cX-R, cY, 0 ]													#Generate first point
	a = inc																				#set angle phi
	while a < 2*math.pi:													# while less than 2xPI (360)
		tX = int( cX + R * math.cos( a ) )					#calc points X-coord
		tY = int( cY + R * math.sin( a ) )					#calc points Y-coord
		tA = math.atan2( (tY-cY), (tX-cX) )					#calc temp phi angle
		if tA < 0:																	#If negative phi
			tA = 2*math.pi + tA												# convert to positive
		pts.extend( [tX, tY, tA] )									#Add to list
		a = a + inc																	#increment angle phi
	print "\t\tcoordinates calculated"
	return pts																		#Return points generated


################################################################################
##	Calculate parameters for iris and pupil borders
##		@param:	fname - filename for image 
##		@param: cX & cY coordinates of circles centrum
##		@param:	rP - radius of pupil circle
##		@param:	rI - radius of iris circle
################################################################################
def calcParams( fname, cX, cY, rP, rI ):
	sname 			= savImgPath + fname[ fname.rfind("/")+1 : fname.rfind(".") ] \
								+ "_para.txt"
	circPupil 	= 2 * rP * math.pi								#Circumference
	circIris		= 2 * rI * math.pi								#Curcumference
	pointsPN		= int( circPupil/3 );							#Number of points to generate
	pointsIN		= int( circIris/3 );							#Number of points to generate

	if pointsPN > 125:														#Maximum number of pooints
		pointsPN	= 125
	if pointsIN > 200:														#Maximum number of points
		pointsIN	= 200

	ptsP = calcPoints(cX, cY, rP, pointsPN)				#gen pt list for pupil border
	ptsI = calcPoints(cX, cY, rI, pointsIN)				#gen pt list for iris border

	print "\tWriting parameters to file: ",				#Generate parameter file for img
	f = open( sname, "w" );
	f.write( str(pointsPN) + "\n" + str(pointsIN) + "\n" )
																								#write number of points to come	
	for p in ptsP:																#Write pupil point list
		f.write( str(p) + " " )
	f.write("\n" )
	
	for p in ptsI:																#Write iris point list
		f.write( str(p) + " " )
	
	f.close()
	print "\t\tParameters written"
	




################################################################################
##	Connect and retrieve database list
################################################################################
db 		= MySQLdb.connect(host="localhost", user="root", \
												passwd="toor", db="webIIC")
cur 	= db.cursor()
cur.execute("SELECT AID, ORG, COORD FROM image WHERE COORD!=''")



################################################################################
## Loop through all images in list
################################################################################
for data in cur.fetchall( ):
	imageCounter	= imageCounter + 1														#inc counter
	image 				= data[1].rstrip("\n")[len(orgImgPath):]			#Rm trailing chars

	print ""
	print imageCounter,
	print image

	coords = sortCoords( data[2] )											#Sort coordinates

	rP		= (int( coords[0]['X'] ) - int( coords[1]['X'] ) ) / 2 #Calc radii pupil
	cX		=  int( coords[0]['X'] ) - rP									#Calc coordinate center
	cY		=	 int( coords[0]['Y'] ) 											#Calc coordinate center
	rI		= (cX - int(coords[2]['X']))									#Calc radii iris

	drawCircles( data[1], cX, cY, rP, rI )							#Gen BW img w/green circle
	calcParams(  data[1], cX, cY, rP, rI )							#Calc points on circle

	print ""

######### LOOP STOPPED ########


