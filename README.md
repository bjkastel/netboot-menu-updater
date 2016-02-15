# NetBoot Menu Updater

Requirements on Ubuntu Linux (test):
* Python 2.7
* Airspeed (https://github.com/purcell/airspeed)
    * sudo pip install pip
    * sudo pip install airspeed==0.5.4dev-20150515

Update Configuration ('netboot-menu-updater.cfg')

    [DEFAULT]
    
    targetDir=/tmp/pxe
    tftpdIP=192.168.0.1
    ...

Set 'targetDir' and 'tftpdIP' as required and run 'python netboot-menu-updater.py'
