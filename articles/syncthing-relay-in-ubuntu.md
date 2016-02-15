Summary:

1. Setup the digital ocean VPS
    - create a key
    - users
    - firewall
    - folder permissions

root@syncthingrelay-512mb-tor1-01:~# adduser blake
Adding user `blake' ...
Adding new group `blake' (1000) ...
Adding new user `blake' (1000) with group `blake' ...
Creating home directory `/home/blake' ...
Copying files from `/etc/skel' ...
Enter new UNIX password: 
Retype new UNIX password: 
passwd: password updated successfully
Changing the user information for blake
Enter the new value, or press ENTER for the default
    Full Name []: Blake VandeMerwe
    Room Number []: 
    Work Phone []: 
    Home Phone []: 
    Other []: 
Is the information correct? [Y/n] 


root@syncthingrelay-512mb-tor1-01:~# nano /etc/ssh/sshd_config
    PermitRootLogin no

blake@syncthingrelay-512mb-tor1-01:/root$ sudo ufw default deny incoming
Default incoming policy changed to 'deny'
(be sure to update your rules accordingly)
blake@syncthingrelay-512mb-tor1-01:/root$ sudo ufw default allow outgoing
Default outgoing policy changed to 'allow'
(be sure to update your rules accordingly)
blake@syncthingrelay-512mb-tor1-01:/root$ sudo ufw allow 22/tcp
Rules updated
Rules updated (v6)
blake@syncthingrelay-512mb-tor1-01:/root$ sudo ufw enable
Command may disrupt existing ssh connections. Proceed with operation (y|n)? y
Firewall is active and enabled on system startup
blake@syncthingrelay-512mb-tor1-01:/root$ sudo systemctl restart ssh
blake@syncthingrelay-512mb-tor1-01:/root$ sudo systemctl restart sshd
blake@syncthingrelay-512mb-tor1-01:/root$ exit

2. Download the syncthing-relay build
    - download (wget)
    - extract (tar -xvzf)
    - move to /usr/local/bin

https://github.com/syncthing/relaysrv/releases
https://github.com/syncthing/relaysrv/releases/download/v0.12.18/relaysrv-linux-amd64.tar.gz

blake@syncthingrelay-512mb-tor1-01:~/downloads$ tar -xzvf relaysrv-linux-amd64.tar.gz 
relaysrv-linux-amd64/
relaysrv-linux-amd64/relaysrv
blake@syncthingrelay-512mb-tor1-01:~/downloads$ cd relaysrv-linux-amd64/
blake@syncthingrelay-512mb-tor1-01:~/downloads/relaysrv-linux-amd64$ sudo cp relaysrv /usr/local/bin
blake@syncthingrelay-512mb-tor1-01:~/downloads/relaysrv-linux-amd64$ cd
blake@syncthingrelay-512mb-tor1-01:~$ which relaysrv
/usr/local/bin/relaysrv


3. Create /opt/syncthing-relay-certs
    - chmod :syncthing
    - chown g+w

blake@syncthingrelay-512mb-tor1-01:/opt$ sudo chown :blake syncthing-relay-certs/
blake@syncthingrelay-512mb-tor1-01:/opt$ sudo chmod g+w syncthing-relay-certs/

4. Do a test run with `-debug` flag

relaysrv -global-rate 104857600 -keys /opt/syncthing-relay-certs -listen $PUB_IP2222 -per-session-rate 1048576 -ping-interval 30s -provided-by "https://sowingseasons.com - Blake VandeMerwe" -debug


^Cblake@syncthingrelay-512mb-tor1-01:~$ sudo ufw allow 22222
Rule added
Rule added (v6)
blake@syncthingrelay-512mb-tor1-01:~$ sudo ufw allow 22070/tcp
Rule added
Rule added (v6)
blake@syncthingrelay-512mb-tor1-01:~$ sudo ufw reload
Firewall reloaded



5. Create the systemd file
    - start
    - enable

[Unit]
Description=Syncthing-Relay Server
Documentation=https://github.com/syncthing/relaysrv
After=network.target

[Service]
ExecStart=/usr/local/bin/relaysrv -global-rate 104857600 -keys /opt/syncthing-certs -listen <PUPLIC IP ADDRESS>:22222 -per-session-rate 1048576 -ping-interval 20s -provided-by "https://sowingseasons.com - Blake VandeMerwe"
Restart=on-failure
SuccessExitStatus=3 4
RestartForceExitStatus=3 4

[Install]
WantedBy=default.target


    1  sudo apt-get update
    2  sudo apt-get upgrade -y
    3  sudo ufw default deny incoming
    4  sudo ufw default allow outgoing
    5  sudo ufw allow 22/tcp
    6  sudo ufw enable
    7  sudo systemctl restart ssh
    8  sudo systemctl restart sshd
    9  exit
   10  sudo mkdir /opt/syncthing-relay-certs
   11  cd /opt
   12  sudo chmod :blake syncthing-relay-certs/
   13  sudo chown :blake syncthing-relay-certs/
   14  sudo chmod g+w syncthing-relay-certs/
   15  cd
   16  mkdir downloads
   17  cd downloads/
   18  wget https://github.com/syncthing/relaysrv/releases/download/v0.12.18/relaysrv-linux-amd64.tar.gz
   19  tar -xzvf relaysrv-linux-amd64.tar.gz 
   20  cd relaysrv-linux-amd64/
   21  sudo cp relaysrv /usr/local/bin
   22  cd
   23  which relaysrv
   24  ifconfig
   25  export $PUB_IP=159.203.21.244
   26  export PUB_IP=159.203.21.244
   27  sudo nano /etc/profile
   28  echo $PUB_IP
   29  relaysrv -global-rate 104857600 -keys /opt/syncthing-relay-certs -listen $PUB_IP:22222 -per-session-rate 1048576 -ping-interval 30s -provided-by "https://sowingseasons.com - Blake VandeMerwe" -debug
   30  sudo ufw allow 22222
   31  sudo ufw allow 22070/tcp
   32  sudo ufw reload
   33  relaysrv -global-rate 104857600 -keys /opt/syncthing-relay-certs -listen $PUB_IP:22222 -per-session-rate 1048576 -ping-interval 30s -provided-by "https://sowingseasons.com - Blake VandeMerwe" -debug
   34  sudo nano /etc/systemd/system/syncthing-relay.service
   35  sudo systemctl enable syncthing-relay.service 
   36  sudo systemctl start syncthing-relay.service 
   37  history
