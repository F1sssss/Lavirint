Example installation on Ubuntu 20.04 LTS
========================================

Install Ubuntu
--------------

Download and install Ubuntu from image available at:

http://old-releases.ubuntu.com/releases/20.04.2/ubuntu-20.04.2-live-server-amd64.iso

Install following packages:

.. code:: bash

    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get install make=4.2.1-1.2 
    sudo apt-get install mysql-server=8.0.32-0ubuntu0.20.04.2 
    sudo apt-get install apache2=2.4.41-4ubuntu3.13 
    sudo apt-get install python3-pip=20.0.2-5ubuntu1.8 
    sudo apt-get install wkhtmltopdf=0.12.5-1build1


.. note::
    
    Versions are hardcoded to match the versions on current production server.


Timezone and NTP service
------------------------

.. important:: 

    Not setting up timezone and NTP service properly can result in failed 
    fiscalization if time on server differs more than 30 minutes than time on
    tax office server.

Set timezone to Europe/Podgorica:

.. code:: bash

    timedatectl set-timezone Europe/Podgorica


Setup NTP service:

.. code:: bash

    sudo apt-get install systemd-timesyncd
    sudo systemctl unmask systemd-timesyncd.service
    sudo systemctl enable systemd-timesyncd.service
    sudo systemctl start systemd-timesyncd.service
    sudo timedatectl set-ntp on
    sudo apt install ntp

MySQL  
-----

Enter mysql command line interface:

.. code::

    sudo mysql

Create database and database user:

.. code:: mysql

    CREATE USER 'megas'@'localhost' IDENTIFIED BY 'megas';
    CREATE DATABASE IF NOT EXISTS megas CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
    GRANT ALL PRIVILEGES ON megas.* TO 'megas'@'localhost';

Apache2
-------

Enable proxy module:

.. code::

    sudo a2enmod proxy_http


Create configuration file `megas.conf`:

.. code::
    
    sudo vi /etc/apache2/sites-available/megas.conf


.. code:: apacheconf

    <VirtualHost *:80>
        DocumentRoot /var/www/megas
        
        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log

        ProxyPass /api http://127.0.0.1:9110/api
        ProxyPassReverse /api http://127.0.0.1:9110/api
    </VirtualHost>

Enable created configuration and restart service:

.. code:: bash

    sudo a2ensite megas
    sudo systemctl restart apache2


Backend setup
-------------

Create Linux user:

.. code:: bash

    sudo useradd megas

Create folder to host app:

.. code:: bash

    sudo mkdir /opt/megas
    sudo chown -R dev:megas /opt/megas
    sudo chmod -R 710 /opt/megas


Create folder to host app files:

.. code:: bash

    sudo mkdir /opt/megas_files
    sudo mkdir /opt/megas_files/certificates
    sudo mkdir /opt/megas_files/company
    sudo mkdir /opt/megas_files/efi
    sudo chown -R dev:megas /opt/megas_files
    sudo chmod -R 640 /opt/megas_files


Fetch the repository locally with git. Navigate to root of the project. Run the following command:


.. code:: bash

    cd client-backend
    make pack

This will create folder `pack` inside `client-backend` folder. Copy the contents of this folder to remote server inside
folder `/opt/megas`.

Create virtual environment and install dependencies:

.. code:: bash

    pip install virtualenv
    cd /opt/megas
    python3 -m virtualenv venv
    source /opt/megas/venv/bin/activate
    pip install -r requirements_for_test.txt

Create environment.sh file:

.. code:: bash
    
    sudo vi environment.sh

.. code:: sh
    
    export CLIENT_CERTIFICATE_STORE='/opt/megas_files/certificates'
    export COMPANY_FILESTORE_PATH='/opt/megas_files/company'
    export EFI_FILES_STORE_PATH='/opt/megas_files/efi'
    export OKRUZENJE=razvoj
    export PRINT_FONT_FILEPATH_LIGHT='/opt/megas/fonts/Inconsolata/static/Inconsolata_Condensed/Inconsolata_Condensed-ExtraLight.ttf'
    export PRINT_FONT_FILEPATH_REGULAR='/opt/megas/fonts/Inconsolata/static/Inconsolata/Inconsolata-Regular.ttf'
    export SERVER_BIND_ADDRESS=0.0.0.0
    export SERVER_PORT=9110
    export SQLALCHEMY_DATABASE_URI=mysql+pymysql://megas:megas@localhost/megas?charset=utf8mb4
    source /opt/megas/venv/bin/activate

Frontend setup
------------------

Copy frontend files to `/var/www/megas` folder. Change ownership of frontend directory to HTTP user and set permissions:

.. code:: bash

    sudo chown -R www-data:www-data /var/www/megas
    sudo chmod 755 -R /var/www/megas


User setup ``test``
----------

To setup DigitalMe user run:

.. code:: mysql

    UPDATE `organizaciona_jedinica` 
    SET `efi_kod`='nx690we691' 
    WHERE firma_id=241;

    UPDATE `naplatni_uredjaj` 
    SET `efi_kod`='op269xc030' 
    WHERE `organizaciona_jedinica_id`=(SELECT `id` FROM `organizaciona_jedinica` WHERE `firma_id`=241);

    UPDATE `operater` 
    SET `kodoperatera`='zh854mj949' 
    WHERE `firma_id`=241;

To setup Affinity Balkans user:


.. code:: mysql

    UPDATE `organizaciona_jedinica` 
    SET `efi_kod`='bs691xa645' 
    WHERE `firma_id`=355;

    UPDATE `naplatni_uredjaj` 
    SET `efi_kod`='xc344gq355' 
    WHERE `organizaciona_jedinica_id`=(SELECT `id` FROM `organizaciona_jedinica` WHERE `firma_id`=355);

    UPDATE `operater` 
    SET `kodoperatera`='ly379zr781' 
    WHERE `firma_id`=355;