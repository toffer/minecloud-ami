class oracle_java {

    user {'oab':
        ensure     => present,
        home       => '/home/oab',
        managehome => true,
    }

    exec {'git_clone_oab':
        user    => oab,
        path    => '/usr/bin',
        command => 'git clone git://github.com/flexiondotorg/oab-java6.git /home/oab/oab-java',
        creates => '/home/oab/oab-java',
        require => User['oab'],
    }

    exec {'build_java':
        user    => root,
        timeout => 0,
        command => '/home/oab/oab-java/oab-java.sh -7s',
        require => Exec['git_clone_oab'],
    }

    package{ 'oracle-java7-jre':
        ensure  => present,
        require => Exec['build_java'],
    }

}