class apt {

    exec {'apt-update':
        schedule => 'daily',
        path     => '/usr/bin',
        command  => 'apt-get update -y',
    }

    exec {'hold_grub':
        user    => root,
        path    => ['/usr/bin', '/bin'],
        command => 'echo grub-pc hold | dpkg --set-selections',  
        before  => Exec['apt-upgrade'],
    }

    exec{'apt-upgrade':
        user    => root,
        timeout => 0,
        path    => ["/bin", "/sbin" , "/usr/bin", "/usr/sbin"],
        command => 'apt-get -y upgrade',
        require => Exec['apt-update'],
    }

    $packages = [
        'rsync', 'screen', 'zip', 'git', 'libpq-dev', 'tree',
        'devscripts', 'debhelper', 'libasound2', 'unixodbc',
        'libxi6', 'libxt6', 'libxtst6', 'libxrender1', 'rng-tools'
    ]
    package {$packages:
        ensure  => present,
        require => Exec['apt-upgrade'],
    }

}
