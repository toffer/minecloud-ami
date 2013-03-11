    class msm_backup_restore {

    file {'/usr/local/bin':
        owner   => root,
        group   => root,
        source  => 'puppet:///modules/msm_backup_restore/bin',
        recurse => true,
    }

    file {'/etc/cron.d':
        owner   => root,
        group   => root,
        mode    => 0644,
        source  => 'puppet:///modules/msm_backup_restore/cron.d',
        recurse => true,
    }

    file {'/etc/init.d/msm-s3-sync':
        owner   => root,
        group   => root,
        mode    => 0755,
        source  => 'puppet:///modules/msm_backup_restore/init.d/msm-s3-sync',
    }

    file {'/etc/init.d/msm-jar-update':
        owner   => root,
        group   => root,
        mode    => 0755,
        source  => 'puppet:///modules/msm_backup_restore/init.d/msm-jar-update',
    }

    file {'/etc/init.d/msm-log-rotate':
        owner   => root,
        group   => root,
        mode    => 0755,
        source  => 'puppet:///modules/msm_backup_restore/init.d/msm-log-rotate',
    }

    file {'/etc/init.d/msm-update-auth-lists':
        owner   => root,
        group   => root,
        mode    => 0755,
        source  => 'puppet:///modules/msm_backup_restore/init.d/msm-update-auth-lists',
    }

    file {'/etc/init.d/msm-update-instance-state':
        owner   => root,
        group   => root,
        mode    => 0755,
        source  => 'puppet:///modules/msm_backup_restore/init.d/msm-update-instance-state',
    }

    # Why exec update-rc.d commands manually, instead of using service?
    # So I can set sequence numbers (SS=96 and KK=04).
    # Puppet defaults to sequence number 20.
    exec {'update-rc.d -f msm-s3-sync remove':
        user    => root,
        path    => '/usr/sbin',
        require => File['/etc/init.d/msm-s3-sync'],
    }

    exec {'update-rc.d msm-s3-sync defaults 95 05':
        user    => root,
        path    => '/usr/sbin',
        require => Exec['update-rc.d -f msm-s3-sync remove'],
    }

    exec {'update-rc.d -f msm-jar-update remove':
        user    => root,
        path    => '/usr/sbin',
        require => File['/etc/init.d/msm-jar-update'],
    }

    exec {'update-rc.d msm-jar-update defaults 96 04':
        user    => root,
        path    => '/usr/sbin',
        require => Exec['update-rc.d -f msm-jar-update remove'],
    }

    exec {'update-rc.d -f msm-log-rotate remove':
        user    => root,
        path    => '/usr/sbin',
        require => File['/etc/init.d/msm-log-rotate'],
    }

    exec {'update-rc.d msm-log-rotate defaults 96 04':
        user    => root,
        path    => '/usr/sbin',
        require => Exec['update-rc.d -f msm-log-rotate remove'],
    }

    exec {'update-rc.d -f msm-update-auth-lists remove':
        user    => root,
        path    => '/usr/sbin',
        require => File['/etc/init.d/msm-update-auth-lists'],
    }

    exec {'update-rc.d msm-update-auth-lists defaults 96 04':
        user    => root,
        path    => '/usr/sbin',
        require => Exec['update-rc.d -f msm-update-auth-lists remove'],
    }

    exec {'update-rc.d -f msm-update-instance-state remove':
        user    => root,
        path    => '/usr/sbin',
        require => File['/etc/init.d/msm-update-instance-state'],
    }

    # update-instance-state should be last msm-* script run in both
    # startup and shutdown, hence the asymmetrical start and stop levels.
    exec {'update-rc.d msm-update-instance-state defaults 98 06':
        user    => root,
        path    => '/usr/sbin',
        require => Exec['update-rc.d -f msm-update-instance-state remove'],
    }

}
