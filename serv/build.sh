echo "*****"
echo "Installing Docker ... "

sudo yum check-update
sudo yum install -y yum-utils device-mapper-persistent-data lvm2
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker

echo "*****"
echo "Start docker"

sudo systemctl start docker
sudo systemctl enable docker


echo "*****"
echo "Install Docker Compose"


sudo curl -L "https://github.com/docker/compose/releases/download/1.25.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose


echo "*****"
echo "Build Container"

docker-compose up -d --build
docker-compose exec django python manage.py migrate

