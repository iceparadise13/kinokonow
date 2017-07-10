set -eo pipefail

fab -H ${DEST_HOST} deploy:listener,"python -m listen"
