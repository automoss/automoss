FROM ubuntu


ENV DEBIAN_FRONTEND="noninteractive" TZ="Europe/Vienna"

# Install necessary dependencies for starting mysql
WORKDIR /app
RUN apt-get -y update && apt-get -y install make sudo libmysqlclient-dev redis python3-pip

COPY requirements_dev.txt requirements_dev.txt
RUN pip3 install -r requirements_dev.txt --upgrade
EXPOSE 80

COPY . .


# Make start script executable
RUN chmod +x start.sh

# Start MySQL and run server
CMD ["/bin/bash", "/app/start.sh"]
