DEST_HOST=pi@192.168.0.14
DEST_DIR=/home/pi/kinokonow
fab -H ${DEST_HOST} copy_files:.fabfiles,${DEST_DIR}
