#!/bin/bash

RED="\e[91m"
GREEN="\e[92m"
NORMAL="\e[0m"
ccl="\e[1;49;93m"

# Install required packages
sudo apt install python3-cherrypy3 python3-jinja2 python3-serial python3-yaml supervisor python3-pysnmp4 -y

# Check if the odr user exists, and if not, create it and add it to the dialout and audio groups
if ! id -u odr > /dev/null 2>&1; then
  sudo adduser odr
  sudo usermod -a -G dialout odr
  sudo usermod -a -G audio odr
fi

# Give the odr user sudo privileges
echo "odr     ALL=(ALL:ALL) ALL" | sudo tee /etc/sudoers.d/odr

# Ensure the odr user has proper permissions on their home directory
sudo chown -R odr:odr /home/odr

# Run the following commands as the odr user
sudo runuser -u odr -- bash -c "
cd /home/odr/
git clone https://github.com/DABodr/ODR-EncoderManager.git
mv /home/odr/ODR-EncoderManager/config.json.sample /home/odr/ODR-EncoderManager/config.json
"

# Create symlinks for supervisor configuration if they don't exist
if [ ! -L /etc/supervisor/conf.d/odr-encoder.conf ]; then
  sudo ln -s /home/odr/ODR-EncoderManager/supervisor-encoder.conf /etc/supervisor/conf.d/odr-encoder.conf
fi

if [ ! -L /etc/supervisor/conf.d/odr-gui.conf ]; then
  sudo ln -s /home/odr/ODR-EncoderManager/supervisor-gui.conf /etc/supervisor/conf.d/odr-gui.conf
fi

# Restart supervisor and start the ODR-encoderManager web server
sudo /etc/init.d/supervisor restart
sudo supervisorctl reread
sudo supervisorctl update ODR-encoderManager

# Print instructions for accessing the web server
echo -e "$GREEN Updating ld cache $NORMAL"
echo -e "$GREEN Go to : http://<ip_address>:8080 $NORMAL"
echo -e "$GREEN Login with user joe and password secret $NORMAL"

# Wait for 10 seconds before opening the browser
echo -e "$ccl Opening your internet browser in 10 seconds"
echo -e "( http://localhost:8080 )"
echo
echo -e " User: $RED joe $ccl pass: $RED secret $ccl" 
echo 
echo " ctrl+c to exit"
echo
echo -e "$GREEN Remember to add this page to your favorites ! $NORMAL"
sleep 10
sensible-browser http://localhost:8080 &
