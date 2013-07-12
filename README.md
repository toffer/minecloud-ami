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

    Make a note of your AWS security credentials: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.

2. **Import a Key Pair using the [AWS Web console](https://console.aws.amazon.com/).**

	Generate a new SSH key on your local machine called `MinecraftEC2`.

        $ ssh-keygen -f ~/.ssh/MinecraftEC2
	
    Upload the public key `MinecraftEC2.pub` to AWS. The `build-ami.py` script will expect the private key `MinecraftEC2` to be located in your `$HOME/.ssh` directory.

3. **Create a Security Group using the [AWS Web console](https://console.aws.amazon.com/).**

    It should be called `minecraft` and should allow inbound traffic on two ports: 22 (SSH), and 25565 (Minecraft).

4. **Create an S3 bucket.**

    Use the AWS Web interface to create an S3 bucket in which to back up your Minecraft world data files.

5. **Set local environment variables.**

    AWS security credentials from Step #1:

        $ export AWS_ACCESS_KEY_ID=...
        $ export AWS_SECRET_ACCESS_KEY=...

    Name of S3 bucket (created in the previous step) to store Minecraft world data files.

        $ export MSM_S3_BUCKET=...


### Virtualenv ###

1. **Set up a virtualenv and activate it.**

    * Install 'pip' command. This installs pip in the global site-packages location.

            $ sudo easy_install pip

	* Install 'virtualenv'. Again, this tool will also be globally available.

            $ sudo pip install virtualenv

	* Create a directory for the minecloud project. This is where you will create a virtualenv and clone the minecloud git repository. 

            $ mkdir ~/minecloud-project

	* Change directory.

            $ cd ~/minecloud-project

	* Create a virtualenv called 'venv'.

            $ virtualenv venv

	* Activate the virtualenv.

            $ source venv/bin/activate

2. **Clone repository.**

        (venv)$ git clone https://github.com/toffer/minecloud-ami
        (venv)$ cd minecloud-ami

3. **Install requirements.**

        (venv)$ pip install -r requirements.txt


Usage
-----
The `build-ami.py` takes a base Ubuntu 12.04 (Precise Pangolin) AMI and customizes it to create a Mincloud AMI.

By default, the `build-ami.py` script will create the custom AMI in the `us-west-2` region (Oregon). If you want to create an AMI for use in a different EC2 region, edit the `env.ec2_region` near the top of the script. A list of regions and their associated codes can be found [here](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html).

If you select a region different than the default `us-west-2` region, you will also need to change the `env.ec2_amis` variable, since AMI Ids are specific to regions. To find the official Ubuntu 12.04 AMI for your region in the AWS console, use the search string `099720109477 ubuntu-precise-12.04-amd64-server` on the public AMIs list. Alternatively, use Canonical's [Amazon EC2 AMI Locator](http://cloud-images.ubuntu.com/locator/ec2/).

*Note: Be sure to import the key pair and create the security group in the same region specified in the script.*

* **Build the AMI.**

        (venv)$ ./build-ami.py

The script takes about 20 minutes to complete. When it finishes, it will output the AMI ID.


Credits
-------
Many projects and companies have been instrumental in making this one possible. In addition to the more obvious choices (Thanks, [Amazon](https://aws.amazon.com/)! Thanks, [Puppet Labs](https://puppetlabs.com/)! Thanks, [Mojang](http://minecraft.net/)!), several other projects deserve special mention:

* [OAB-Java](https://github.com/flexiondotorg/oab-java6) by [Martin Wimpress](https://github.com/flexiondotorg).
* [Minecraft Server Manager](https://github.com/marcuswhybrow/minecraft-server-manager) by [Marcus Whybrow](https://github.com/marcuswhybrow).


License
-------
MIT License. Copyright (c) 2013 Tom Offermann.
