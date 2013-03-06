# Set up 3 run stages
stage {'first': before => Stage['second']}
stage {'second': before => Stage['main']}

# Apt update, upgrade and install packages
class {'apt': stage => 'first'}

# Install java
class {'oracle_java': stage => 'second'}
class {'virtualenv': stage => 'second'}

# Install Minecraft Service Manager    
class {'msm': stage => 'main'}
class {'msm_backup_restore': stage => 'main'}
