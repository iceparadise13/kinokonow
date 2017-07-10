set -eo pipefail

fab -H ${DEST_HOST} sync_requirements:requirements.txt
fab -H ${DEST_HOST} copy_files:.fabfiles,${DEST_DIR}
