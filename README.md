#Welcome to use autoconfig!

#Introduction
autoconfig will help to do config with config file you want to config.

#Structure

    autoconfig

    -backup

    -new_config

     -__init__.py

     -autoconfig.json

#how to do

1. put your config file in new_config folder, for example


          -new_config
          --nova.json
          --cinder-volume.conf
          --nova.conf.sample


       
2. config autoconfig.json, write your config file/system config file mapping in autoconfig.json. for example:
 
        {
          "json":{
                    "nova.json": "/etc/nova/nova.json"},
          "ini":{
                    "cinder-volume.conf": "/etc/cinder/cinder-volume.conf"},
          "sample":{
                    "nova.conf.sample": "/etc/nova/nova.conf.sample"}
        }

3.Run following command:

        python __init__.py

#What it do when run autpconfig

Firstly, it backup all config files which your write in your autoconfig.json to backup folder.
Secondly, it read all your new_config files, and write the values of your options to it mapping system config files(which your config mapping in autoconfig.json).

