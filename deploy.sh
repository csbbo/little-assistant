docker-compose -f docker-compose.yml down
docker image rm la_server

docker build . -t la_server
docker-compose -f docker-compose.yml up -d
