set -eo pipefail

fab -H ${DEST_HOST} deploy:listener,${DEST_DIR},"celery -A tasks.celery -l INFO"
