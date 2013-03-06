class msm {

    group {'minecraft':
        ensure => present,
        system => true,
    }
    
    user {'minecraft':
        ensure     => present,
        system     => true,
        gid        => 'minecraft',
        shell      => '/bin/sh',
        home       => '/home/minecraft',
        managehome => true,
        require    => Group['minecraft'],
    }

    $repo_url = 'git://github.com/marcuswhybrow/minecraft-server-manager.git'
    $repo_dir = '/home/minecraft/msm'
    exec {'git_clone_msm':
        user    => 'minecraft',
        path    => '/usr/bin',
        command => "git clone ${repo_url} ${repo_dir}",
        creates => $repo_dir,
        require => User['minecraft'],        
    }

    file {'/etc/msm.conf':
        owner   => 'root',
        group   => 'root',
        mode    => 0644,
        source  => "${repo_dir}/msm.conf",
        require => Exec['git_clone_msm'],
    }

    file {'/opt/msm':
        ensure  => directory,
        owner   => 'minecraft',
        group   => 'minecraft',
        mode    => 0775,
        require => User['minecraft'],
    }

    file {'/opt/msm/archives':
        ensure  => directory,
        owner   => 'minecraft',
        group   => 'minecraft',
        mode    => 0775,
        require => File['/opt/msm'],
    }

    file {'/opt/msm/archives/backups':
        ensure  => directory,
        owner   => 'minecraft',
        group   => 'minecraft',
        mode    => 0775,
        require => File['/opt/msm/archives'],
    }

    file {'/opt/msm/archives/worlds':
        ensure  => directory,
        owner   => 'minecraft',
        group   => 'minecraft',
        mode    => 0775,
        require => File['/opt/msm/archives'],
    }

    file {'/opt/msm/archives/logs':
        ensure  => directory,
        owner   => 'minecraft',
        group   => 'minecraft',
        mode    => 0775,
        require => File['/opt/msm/archives'],
    }

    file {'/dev/shm/msm':
        ensure  => directory,
        owner   => 'minecraft',
        group   => 'minecraft',
        mode    => 0775,
        require => User['minecraft'],
    }

    file {'/etc/init.d/msm':
        owner   => 'minecraft',
        group   => 'minecraft',
        mode    => 0775,
        source  => "${repo_dir}/init/msm",
        require => Exec['git_clone_msm'],
    }

    file {'/usr/local/bin/msm':
        ensure  => link,
        target  => '/etc/init.d/msm',
        require => File['/etc/init.d/msm'],
    }

    exec {'msm_update':
        user    => root,
        command => '/etc/init.d/msm update --noinput',
        # command => '/bin/echo pass',
        require => File['/etc/init.d/msm'],
    }

    $jar_url = 'https://s3.amazonaws.com/MinecraftDownload/launcher/minecraft_server.jar'
    exec {'msm_jargroup_create':
        user    => root,
        command => "/etc/init.d/msm jargroup create minecraft ${jar_url}",
        creates => '/opt/msm/jars/minecraft',
        require => Exec['msm_update'],
    }

    exec {'msm_server_create':
        user    => root,
        command => "/etc/init.d/msm server create default",
        creates => "/opt/msm/servers/default",
        require => Exec['msm_jargroup_create'],
    }

    file {'/opt/msm/servers/default/server.properties':
        owner   => 'minecraft',
        group   => 'minecraft',
        mode    => 0664,
        content => template('msm/server.properties.erb'),
        require => Exec['msm_server_create'],
    }

    exec {'msm_jar':
        user    => root,
        command => "/etc/init.d/msm default jar minecraft",
        creates => '/opt/msm/servers/default/server.jar',
        require => Exec['msm_server_create'],
    }

    file {'/opt/msm/servers/default/worldstorage/world':
        ensure  => directory,
        owner   => 'minecraft',
        group   => 'minecraft',
        mode    => 0775,
        require => Exec['msm_jar'],
    }

    file {'/opt/msm/servers/default/world':
        ensure  => link,
        owner   => 'minecraft',
        group   => 'minecraft',
        target  => '/opt/msm/servers/default/worldstorage/world',
        require => File['/opt/msm/servers/default/worldstorage/world'],
    }

    file {'/opt/msm/servers/default/active':
        ensure  => present,
        owner   => 'minecraft',
        group   => 'minecraft',
        mode    => 0664,
        require => Exec['msm_server_create'],
    }

    # I exec update-rc.d commands manually, so that I can set
    # sequence number.
    exec {'update-rc.d -f msm remove':
        user    => root,
        path    => '/usr/sbin',
        require => File['/etc/init.d/msm'],
    }

    exec {'update-rc.d msm defaults 97 03':
        user    => root,
        path    => '/usr/sbin',
        require => Exec['update-rc.d -f msm remove'],
    }

    service {'msm':
        ensure  => 'running',
        hasstatus => false,
        status => "ps -ef | grep -v grep | grep -i 'screen.*msm.*java.*Xms.*jar'",
        require => [File['/opt/msm/servers/default/server.properties',
                        '/opt/msm/servers/default/world',
                        '/opt/msm/servers/default/active'],
                    Exec['update-rc.d msm defaults 97 03']],
    }

}
