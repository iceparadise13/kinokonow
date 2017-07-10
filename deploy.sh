DEST_DIR=/home/pi/kinokonow
fab -H pi@192.168.0.14 copy_files:.fabfiles,${DEST_DIR}
