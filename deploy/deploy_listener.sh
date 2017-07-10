set -eo pipefail

fab -H ${DEST_HOST} deploy:listener,${DEST_DIR},"python3 -m listen ${YAHOO_API_KEY}"
