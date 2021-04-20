FROM python:3

RUN apt-get update -y \
    && apt-get install -y apache2 \
    && apt-get clean -y \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*    

RUN pip install lxml wand

# Copy over the apache configuration file and enable the site
RUN a2enmod headers rewrite cgi

COPY ./conf/apache/edrefcard.conf /etc/apache2/sites-available/edrefcard.conf
COPY ./www/ /var/www/html

RUN mkdir /var/www/html/configs \
    && chmod uga+rw /var/www/html/configs 

RUN echo "SetEnv PYTHONIOENCODING utf-8" >> /etc/apache2/apache2.conf

RUN a2dissite 000-default.conf
RUN a2ensite edrefcard.conf

EXPOSE 80

WORKDIR /var/www/html

CMD  /usr/sbin/apache2ctl -D FOREGROUND

