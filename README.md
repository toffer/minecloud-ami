Minecloud-AMI
=============
*Build an on-demand Minecraft server on Amazon EC2.*

Minecloud-AMI installs and configures the Minecraft server and various management scripts to build a custom EC2 AMI--one that's designed to back up Minecraft world data to and restore world data from Amazon's S3 service upon server startup and shutdown.


Description
-----------
An effective, on-demand, Minecraft server needs more than just Java and the Minecraft server installed.

Ideally, an on-demand server should do the following:

* **Restore** your Minecraft world data from S3 backup upon server startup.
* **Save** your Minecraft world data to S3 periodically while it is running, and upon server shutdown.
* **Update** the Minecraft server when a new version becomes available.

Minecloud-AMI is designed to create a Minecraft EC2 AMI that does all of the above, using a set of Puppet manifests to build, install and configure the necessary software.

Despite using Puppet, you don't need to know anything about Puppet to create the AMI, since a `build-ami.py` script is included. It launches a stock Ubuntu cloud image on EC2, applies the Puppet manifests, and creates an AMI image for you. (No need to set up a Puppet Master server.)


Setup
-----
Setup is a bit involved for building your first AMI, and requires familiarity with Amazon Web Services (AWS) and the Unix (or Mac) command line. The first set of steps involves setting up and configuring your AWS account. The second set is focused on creating a Python virtualenv so that you can run the `build-ami.py` script.


### AWS Account ###

1. **Set up an [Amazon AWS account](https://aws.amazon.com/) for EC2 and S3.**

2. **Import a Key Pair using the [AWS Web console](https://console.aws.amazon.com/).**

	On the local command line generate an SSH key called `MinecraftEC2`.
	
	    $ ssh-keygen
	
    Upload the public key `MinecraftEC2.pub` to AWS. The `build-ami.py` script will expect the private key `MinecraftEC2` to be located in your `$HOME/.ssh` directory.

3. **Create a Security Group using the [AWS Web console](https://console.aws.amazon.com/).**

    It should be called `Minecraft` and should allow inbound traffic on two ports: 22 (SSH), and 25565 (Minecraft).

4. **Create an S3 bucket.**

    Use the AWS Web interface to create an S3 bucket in which to back up your Minecraft world data files.

5. **Set environment variables.**

    For AWS access:

        $ export AWS_ACCESS_KEY_ID=...
        $ export AWS_SECRET_ACCESS_KEY=...

    Name of S3 bucket to store Minecraft world data files.

        $ export MSM_S3_BUCKET=...


### Virtualenv ###

1. **Set up a virtualenv and activate it.**

    I think this is easiest to do with [virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/):

        $ mkvirtualenv minecloud
        $ workon minecloud

2. **Clone repository.**

        (minecloud)$ git clone https://github.com/toffer/minecloud-ami
        (minecloud)$ cd minecloud-ami

3. **Install requirements.**

        (minecloud)$ pip install -r requirements.txt


Usage
-----
By default, the `build-ami.py` script will create the custom AMI in the `us-west-2` region (Oregon). If you want to use a different EC2 region, edit the `env.ec2_region` and `env.ec2_amis` variables near the top of the script.

* **Build the AMI.**

        (minecloud)$ ./build-ami.py

The script takes about 30 minutes to complete. When it finishes, it will output the AMI ID.


Credits
-------
Many projects and companies have been instrumental in making this one possible. In addition to the more obvious choices (Thanks, [Amazon](https://aws.amazon.com/)! Thanks, [Puppet Labs](https://puppetlabs.com/)! Thanks, [Mojang](http://minecraft.net/)!), several other projects deserve special mention:

* [OAB-Java](https://github.com/flexiondotorg/oab-java6) by [Martin Wimpress](https://github.com/flexiondotorg).
* [Minecraft Server Manager](https://github.com/marcuswhybrow/minecraft-server-manager) by [Marcus Whybrow](https://github.com/marcuswhybrow).


License
-------
MIT License. Copyright (c) 2013 Tom Offermann.
