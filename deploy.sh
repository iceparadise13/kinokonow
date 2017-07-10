DEST_DIR=/home/pi/kinokonow
while read line; do
  echo deploying $line
  fab -H pi@192.168.0.14 copy_files:$line,${DEST_DIR}/$line
done < .fabfiles
