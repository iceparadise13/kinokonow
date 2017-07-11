docker-machine ssh kinokonow mkdir -p /usr/share/kinokonow
docker-machine scp secrets/yahoo_api_key kinokonow:/usr/share/kinokonow/yahoo_api_key
docker-machine scp secrets/twitter.yml kinokonow:/usr/share/kinokonow/twitter.yml
docker-machine scp follow.txt kinokonow:/usr/share/kinokonow/follow.txt