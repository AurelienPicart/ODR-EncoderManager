# ODR-EncoderManager for ODR-Tools_Installer ( Supervisor config odr/odr port 8001 ) 
OpenDigitalRadio Encoder Manager is a tools to run and configure ODR Encoder easly with a WebGUI.

# Note about version V5.0.0
**Requirement**

  * ODR-AudioEnc v3.0.0
  * ODR-SourceCompanion v1.0.0
  * ODR-PadEnc v3.0.0

**New Feature / Change**

  * Add odr-padenc raw-slides option
  * Add additional supervisor option by encoder (only via editing config file at this time)
  * Display ODR tools version
  * ODR-padenc socket support
  * Change supervisor stderr logging
  * Communication between odr-audioenc/odr-sourcecompanion use socket instead fifo

**Bug fixes**

  * Solve issue with SNMP request on AVT with last firmware (ClockSource)


# INSTALLATION

  * wget https://github.com/DABodr/ODR-EncoderManager/blob/master/EncoderManager-install.sh
  * chmod +x ./EncoderManager-install.sh
  * ./EncoderManager-install.sh
  
  After installation:
  * Go to : `http://<ip_address>:8080`
  * Login with user `joe` and password `secret` 



# CONFIGURATION
  * You can edit global configuration, in particular path in this files :
    * config.json
    * supervisor-gui.conf
  * If you want to change supervisor XMLRPC login/password, you need to edit `/etc/supervisor/supervisord.conf` and `config.json` files


# How to set DLS / DL+ / SLS
**Set DLS / DL+ for all encoder**
To set a text metadata used for DLS, use http GET or POST on the Encoder Manager API from your automation software.
> http://{ip}:8080/api/setDLS?dls={artist}-{title}

As an alternative DLS+ tags are automatically activated if you use artist & title parameters:
> http://{ip}:8080/api/setDLS?artist={artist}&title={title}

Many radio automation software can send this information to Encoder Manager API by using a call of this type (for example)
> http://{ip}:8080/api/setDLS?dls=%%artist%% - %%title%%

%%artist%% - %%title%% should be replaced with the expression expected from your radio automation software.

At each events on your playlist (when a track start) the radio automation software will send via this url the appropriate metadata to Encoder Manager API. It will be reflected on the DAB signal.

**Set DLS / DL+ for specific encoder (from version V4.0.0)**
If you want to update DLS / DL+ for a specific encoder, you need to find the uniq_id on Encoder > Manage page under Information button
> http://{ip}:8080/api/setDLS?dls={artist}-{title}&uniq_id={00000000-0000-0000-0000-000000000000}

**Set SLS for all encoder**
To send slide used for SLS, use http POST on the Encoder Manager API.
> curl -X POST -F 'slide_file=@"live.jpg"' http://{ip}:8080/api/setSLS

**Set SLS for specific encoder**
If you want to update SLS for a specific encoder, you need to find the uniq_id on Encoder > Manage page under Information button
> curl -X POST -F 'uniq_id={00000000-0000-0000-0000-000000000000}' -F 'slide_file=@"{file.jpg}"' http://{ip}:8080/api/setSLS

# ADVANCED
  * To use the reboot api (/api/reboot), you need to allow odr user to run shutdown command by adding the line bellow at the end of /etc/sudoers file :
```
odr     ALL=(ALL) NOPASSWD: /sbin/shutdown
```

