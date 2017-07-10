set -eo pipefail

fab -H ${DEST_HOST} deploy:listener,${DEST_PATH},"python3 -m listen"
