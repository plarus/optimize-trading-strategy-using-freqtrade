#!/bin/bash

read -p "Remove the previous configuration? " -n 1 -r

if [[ $REPLY =~ ^[YyOo]$ ]]
then
  sudo rm -rf ./ft_userdata/
  sudo rmdir ./ft_userdata/
  #rm user_data/tradesv3.sqlite
fi

mkdir ft_userdata
cd ft_userdata/

# Download the dc file from the repository
curl https://raw.githubusercontent.com/freqtrade/freqtrade/stable/docker-compose.yml -o docker-compose.yml

# Pull the freqtrade image
sudo docker-compose pull

# Create user directory structure
sudo docker-compose run --rm freqtrade create-userdir --userdir user_data

# Create configuration - Requires answering interactive questions
sudo docker-compose run --rm freqtrade new-config --config user_data/config.json

# Patch if unlimited conf is used
sed -i "s/: unlimited,/: "\""unlimited"\"",/g" ./user_data/config.json

