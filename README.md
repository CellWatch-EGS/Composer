docker build -t registry.deti/cellwatch/composer_app:v1 . 
docker push registry.deti/cellwatch/composer_app:v1
docker run -p 5000:5000 registry.deti/cellwatch/composer_app:v1

docker container ls
docker rm -f <container_name> 