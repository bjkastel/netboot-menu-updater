#!/usr/bin/python
import os.path
import ConfigParser
import urllib
import shutil
import airspeed
import re

##########################
# Class Definitions

class Category:
    def __init__(self, name, label):
        self.name = name
        self.label = label
    
    def __str__(self):
        return str(self.name);
    
    def __cmp__ (self, other):
        return self.name.__cmp__(other.name)
        
    def __eq__ (self, other):
        return self.name.__eq__(other.name)
        
    def __hash__ (self):
        return self.name.__hash__();
    
class Distribution:
    def __init__(self, index, name, label, arch):
        self.index = index
        self.name = name
        self.label = label
        self.arch = arch
        
    def __str__(self):
        return str(self.name);

##########################
# Template Definitions

defaultMenuTemplate = airspeed.Template('''
default pxelinux-menu.c32
prompt 0
implicit 1
allowoptions 1
noescape 1
menu title NetBootServer

#foreach($category in $categories)
label ${category.name}
    menu label ${category.label}
    kernel pxelinux-menu.c32
    append pxelinux.cfg/${category.name}
#end

label -
    menu label ----

label hddboot
    menu label Boot from Disk
    localboot 0x80

''')

categoryMenuTemplate = airspeed.Template('''
default pxelinux-menu.c32
prompt 0
implicit 1
allowoptions 1
noescape 1
menu title ${category.label}

#foreach($distribution in $distributions)
label ${distribution.name}
    menu label ^${distribution.index}: ${distribution.label} ${distribution.arch} installieren
    kernel linux/${distribution.name}-kernel
    append vga=normal initrd=linux/${distribution.name}-initrd.gz
#end

label -
    menu label ----

label return
    menu label ^r: Return
    kernel pxelinux-menu.c32
    append pxelinux.cfg/default
''')

displayDistributionInformationTemplate = airspeed.Template('''
---------
${category.label}

 Index : ${distribution.index}
 Name  : ${distribution.name}
 Label : ${distribution.label}
 Arch  : ${distribution.arch}
''')

##########################
# Read configurations
config = ConfigParser.ConfigParser()
config.read(['/etc/netboot-menu-updater.cfg', '~/.netboot-menu-updater.cfg', './netboot-menu-updater.cfg'])

##########################
# Set default configurations

targetDir = config.get('DEFAULT', 'targetDir')
tftpdIP = config.get('DEFAULT', 'tftpdIP')
pxelinux = config.get('DEFAULT', 'pxelinux')
menu = config.get('DEFAULT', 'menu')

print "%s %s" % ("Target directory:", targetDir)

##########################
# Check for missing folders, clean and create them
if not os.path.exists(targetDir):
    os.mkdir(targetDir)

if os.path.exists("%s/pxelinux.cfg" % (targetDir)):
    shutil.rmtree("%s/pxelinux.cfg" % (targetDir))

if not os.path.exists("%s/pxelinux.cfg" % (targetDir)):
    os.mkdir("%s/pxelinux.cfg" % (targetDir))

if os.path.exists("%s/linux" % (targetDir)):
    shutil.rmtree("%s/linux" % (targetDir))

if not os.path.exists("%s/linux" % (targetDir)):
    os.mkdir("%s/linux" % (targetDir))

##########################

distributions = config.sections();
distributions.sort();
categories = {};
i = {}
for distribution in distributions:  
    name = distribution
    category = Category(re.sub(r'\s', '', config.get(distribution, 'category')), config.get(distribution, 'category'))
    label = config.get(distribution, 'name')
    arch = config.get(distribution, 'arch')
    mirror = config.get(distribution, 'mirror')
    kernel = config.get(distribution, 'kernel')
    initrd = config.get(distribution, 'initrd')
    kernelUrl = "%s/%s" % (mirror, kernel)
    initrdUrl = "%s/%s" % (mirror, initrd)
    
    i[category] = i.get(category, 0) + 1
    entry = [Distribution(str(i[category]), name, label, arch)]

    categories[category] = categories.get(category, []) + entry
    
    print displayDistributionInformationTemplate.merge({'category': category, 'distribution': entry[0]});

    print "%s %s %s %s" % ("Download", category.label, label, "Kernel") 

    remoteFile = urllib.urlopen(kernelUrl)
    localFile  = open("%s/%s/%s-%s" % (targetDir, "linux", distribution, "kernel"), 'w')
    localFile.write(remoteFile.read())
    remoteFile.close()
    localFile.close()
    print "Done"
    print 
    print "%s %s %s %s" % ("Download", category.label, label, "Initrd") 
    remoteFile = urllib.urlopen(initrdUrl)
    localFile  = open("%s/%s/%s-%s" % (targetDir, "linux", distribution, "initrd.gz"), 'w')
    localFile.write(remoteFile.read())
    remoteFile.close()
    localFile.close()
    print "Done"

pxeconfig = open("%s/%s" % (targetDir, "pxelinux.cfg/default"), 'w')
pxeconfig.write(defaultMenuTemplate.merge({'categories': categories.keys(), 'tftpdIP': tftpdIP}));
pxeconfig.close();

for category, distributions in categories.iteritems():
    pxeconfig = open("%s/%s" % (targetDir, "pxelinux.cfg/%s" % category.name), 'w')
    pxeconfig.write(categoryMenuTemplate.merge({'category': category, 'distributions': distributions}));
    pxeconfig.close();

##########################
print "%s" % ("Download PXE Linux loader")

remoteFile = urllib.urlopen(pxelinux)
localFile  = open("%s/%s" % (targetDir, "pxelinux.0"), 'w')
localFile.write(remoteFile.read())
remoteFile.close()
localFile.close()
print "Done"

##########################
print "%s" % ("Download boot menu renderer")

remoteFile = urllib.urlopen(menu)
localFile  = open("%s/%s" % (targetDir, "pxelinux-menu.c32"), 'w')
localFile.write(remoteFile.read())
remoteFile.close()
localFile.close()
print "Done"

##########################
# Update Config
print ""
print "Finished"
