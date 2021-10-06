FROM ubuntu

WORKDIR /app
COPY . .

# Install necessary dependencies for starting mysql
RUN apt-get -y update && apt-get -y install make sudo mysql-server libmysqlclient-dev
RUN service mysql start && mysql mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY '';FLUSH PRIVILEGES;"

# Install remaining dependencies
RUN make install

# Make start script executable
RUN chmod +x start.sh

CMD ["/bin/bash", "/app/start.sh"]

# Usage:
# docker build . -t automoss
# docker run -p 8000:8000 --rm -it automoss
# docker run -p 8000:8000 --rm -it automoss /bin/bash
# 
# docker build . -t automoss && docker run -p 8000:8000 --rm -it automoss
# docker build . -t automoss && docker run --rm -it automoss
