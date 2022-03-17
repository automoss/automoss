FROM ubuntu

WORKDIR /app
COPY . .

ENV DEBIAN_FRONTEND="noninteractive" TZ="Africa/Johannesburg"

# Install necessary dependencies for starting mysql
RUN apt-get -y update && apt-get -y install make sudo mysql-server libmysqlclient-dev
RUN service mysql start && mysql mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY '';FLUSH PRIVILEGES;"

# Install remaining dependencies
RUN make install

# Make start script executable
RUN chmod +x start.sh

# Start MySQL and run server
CMD ["/bin/bash", "/app/start.sh"]
