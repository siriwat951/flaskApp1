#!/bin/sh
app="docker.flaskapp0"
registry_server="10.4.29.209:30500"


# Stop and remove existing container
docker stop ${app} 2>/dev/null
docker rm ${app} 2>/dev/null


# Pull the prebuilt image from k3s registry
echo "Pulling ${app} from registry ${registry_server}..."
docker pull ${registry_server}/${app}:latest


# Tag it locally for convenience
docker tag ${registry_server}/${app}:latest ${app}:latest


# Run the container with same parameters as before
docker run -p 56733:8000 -d \
 --name=${app} \
 -v "$PWD":/flask_app ${app}:latest

