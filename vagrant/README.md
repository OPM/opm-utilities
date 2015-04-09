Vagrant
=======

[Vagrant](www.vagrantup.com) is a tool for creating and configuring reproducible and
portable development environments. It essentially creates a (disposable) virtual machine 
for you that sets up OPM automatically. The files in this directory is everything you need
to create a Ubuntu 14.04 environment that checks out, compiles, and tests OPM modules.

It requires [VirtualBox](www.virtualbox.org) and Vagrant to be installed.
They are apt-gettable on recent Ubuntus and have relatively hassle-free installers
on Windows and OSX.


To use vagrant execute the following from the directory containting the ```VagrantFile```.
```
$ sudo apt-get install vagrant
$ vagrant up
```

The first time this is executed will take a significant amount of time, as the full Ubuntu 
image must be downloaded. Consequently, OPM will be downloaded (from github), compiled, 
and tests run. After this process has completed, you can log into the machine and try out
OPM.

Execute the following to log into the virtual machine as the vagrant user
```
$ vagrant ssh
```

From here you can build and execute tests in a reproducible environment. Everything you do 
in this environment can easily be discarded, and will only affect the virtual machine:
your own machine will remain unaffected by changes here.
