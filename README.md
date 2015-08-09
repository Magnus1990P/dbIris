#dbIris

Folder Structure
----------------
* /								- contains all files and executables to be used
* /db_periocular/ - contains folders for different sets of images
* /img_processed/ - contains all images stored by OSIRIS_4_1
* /osiris_4_1/		- contains the OSIRIS_4_1 source code program
* /osiris_conf/		- contains all configuration files for OSIRIS_4_1

Files & Executables
-------------------
dbGenerator.py		- After images has been processed, this will generate the matlab file with formatted lists of images
img_list.dev.txt 	- List containing all the images to be processed by OSIRIS, W/full paths
img_list.srv.txt 	- Same as previous
osiris_current_img.txt - Contains the filename of the current image to process with OSIRIS
osiris.exe 				-	OSIRIS_4_1 executable
osiris_gen.py			- Python script reading the image file list and processing the OSIRIS_4_1 with different config files
README.md					- This file
