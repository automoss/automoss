FROM ubuntu

WORKDIR /app
COPY . .


RUN apt-get -y update && apt-get -y install make sudo python3-pip
RUN apt-get -y install redis mysql-server libmysqlclient-dev


RUN service mysql start && mysql mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY '';FLUSH PRIVILEGES;"
RUN make install

RUN chmod +x start.sh

CMD "./start.sh"

# Usage:
# docker build . -t automoss
# docker run -p 8000:8000 --rm -it automoss
