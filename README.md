# README

This application is one for The Enterprise Gym at The University of Dundee.
However, you can modify it to use for your own website reasonably easily.

This application allows the creation of static pages, pages with feeds, registering, logging in, and administration panel.
Non-administrator users are allowed to attend events and complete quizzes for which they earn points and awards.
Administrators can oversee everything, making changes where necessary, and mark users as attended or un-attended to events manually.

# Install Instructions

## Python and Nginx

### Python3.3 or newer is required. This is a guide on how to install Python3.3 in CentOS 6: http://toomuchdata.com/2014/02/16/how-to-install-python-on-centos/.

```
sudo yum groupinstall "Development tools"
sudo yum install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel
wget http://python.org/ftp/python/3.5.0/Python-3.5.0.tar.xz
tar xf Python-3.5.0.tar.xz
cd Python-3.5.0
sudo ./configure --prefix=/usr/local --enable-unicode=ucs4 --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib"
sudo make && sudo make altinstall

cd ..

export PATH="/usr/local/bin:$PATH"

```

### Then we must install Setuptools and pip:

```
# First get the setup script for Setuptools:

wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py

# We are going to need necessary permissions in the local account to change stuff around

sudo chmod 777 -R /usr/local/bin
sudo chmod 777 -R /usr/local/lib

# Then install it for Python 3.5:

python3.5 ez_setup.py

# Now install pip using the newly installed setuptools:

easy_install-3.5 pip

# Then install virtualenv, since we will need them for the dashboard

pip3.5 install virtualenv
```

### Then we must install nginx:

```
sudo yum install epel-release
sudo yum install nginx
sudo chkconfig --levels 235 nginx on
```

### Then we must add the appropriate nginx config at `/etc/nginx/conf.d/default.conf`

```
server {
    listen       80;
    real_ip_header X-Forwarded-For;
    set_real_ip_from 127.0.0.1;
    server_name  localhost;

    #charset koi8-r;

    #access_log  logs/host.access.log  main;

    # Load configuration files for the default server block.
    include /etc/nginx/default.d/*.conf;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:/var/www/html/ac41004/socket.sock;
        include uwsgi_params;
        uwsgi_modifier1 30;
     }

    error_page  404              /404.html;
    location = /404.html {
        root   /usr/share/nginx/html;
    }

    # redirect server error pages to the static page /50x.html
    #
    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /usr/share/nginx/html;
    }
}
```

Then modify the `/etc/nginx/nginx.conf` file.

Change the line that says `worker_processes 1;` to say `worker_processes 8;`.

### Then we must add the nginx user to the student group

```
sudo usermod -a -G student nginx
```

### Then we must create the necessary directories

```
sudo mkdir /var/www && sudo mkdir /var/www/html && sudo mkdir /var/www/html/ac41004
sudo chown student:student /var/www/html/ac41004/
```

### Then we must create the appropriate symlinks

```
sudo ln -s /var/www/html /home/student/html
```

## Installing the application

Navigate to the `/var/www/html/ac41004` folder and clone the git repository (you may need to make a fork beforehand).

```
cd /var/www/html/ac41004/
git clone https://github.com/jslvtr/AC41004-Team-2.git .
```

## Running the application

The only thing that should be necessary are the following:

```
sudo service nginx restart
sudo start uwsgi_ac41004
```

## Installing MongoDB (if wanting to run MongoDB locally alongside the application)

1. Create a `/etc/yum.repos.d/mongodb-org-3.0.repo` file.
2. In this file, put the appropriate code:

```
[mongodb-org-3.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/3.0/x86_64/
gpgcheck=0
enabled=1
```

3. Install MongoDB using the command `sudo yum install mongodb-org`.
4. Run MongoDB by using the command `sudo service mongod start`.
5. Make sure MongoDB runs on reboot by using `sudo chkconfig mongod on`.

## Creating the uWSGI config file

1. Create a file `/etc/init/uwsgi_ac41004.conf`.
2. In this file, put the appropriate code, remembering to use the appropriate service environment variables:

```
description "uWSGI_ac41004"
start on runlevel [2345]
stop on runlevel [06]
respawn

env MONGODB_USER=<>
env MONGODB_DATABASE=<>
env MONGODB_PASSWORD=<>
env MONGODB_URL=<>
env MONGODB_PORT=<>
env UWSGI_ALIVE=/var/www/html/ac41004/venv/bin/uwsgi
env LOGTO_ALIVE=/var/www/html/ac41004/log/emperor.log

exec $UWSGI_ALIVE --master --emperor /var/www/html/ac41004/uwsgi.ini --die-on-term --uid student --gid student --logto $LOGTO_ALIVE
```

3. You can then start the uWSGI service by using `sudo start uwsgi_ac41004`.
4. You can also stop the uWSGI service by using `sudo stop uwsgi_ac41004`.

## Creating the uwsgi socket config file

In the `/var/www/html/ac41004/` folder modify the `uwsgi.ini` file.

```
vi /var/www/html/ac41004/uwsgi.ini
```

Then write the following file contents:

```
[uwsgi]
#application's base folder
base = /var/www/html/ac41004

#python module to import
app = src.app
module = %(app)

home = %(base)/venv
pythonpath = %(base)

#socket file's location
socket = /var/www/html/ac41004/socket.sock

#permissions for the socket file
chmod-socket = 777

#add more processes
processes = 8

#add more threads
threads = 8

#kill worker if timeout > 15 seconds
harakiri = 15

#the variable that holds a flask application inside the module imported at line #6
callable = app

#location of log files
logto = /var/www/html/ac41004/log/%n.log
```

## Modifying SELinux permissions (if SELinux installed, which it usually is)

In order to modify SELinux permissions, we first need to have some invalid permissions in the audit log.
In order to get these, you need to disable SELinux, deploy the URL Service, run the URL Service, then add the modified SELinux permissions, and finally re-enable SELinux.

### Disable SELinux

```
sudo setenforce 0
```

### Deploy and run the application

Deploy as normal and run the app (it should work!).
If the app does not work, check nginx is running (`sudo service nginx restart`).

### Add the SELinux permissions

```
sudo yum install -y policycoreutils-{python,devel}
sudo grep nginx /var/log/audit/audit.log | audit2allow -M nginx
sudo semodule -i nginx.pp
```

### Re-enable SELinux

```
sudo setenforce 1
```

## MongoDB Replication

If you have more than one server for the service and wish to activate MongoDB database replication, then follow the MongoDB documentation on deploying a replica set with authentication.

http://docs.mongodb.org/manual/tutorial/deploy-replica-set-with-auth/

You will also need to make the MongoDB instances accessible externally (so the other instances can connect), hence why authentication is important for security.
