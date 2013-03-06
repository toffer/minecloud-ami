class virtualenv {

    package {['python-setuptools', 'python-dev']:
        ensure     => present,
    }
    
    exec {'easy_install pip':
        user       => root,
        path       => '/usr/bin',
        command    => 'easy_install pip',
        creates    => '/usr/local/bin/pip',
        require    => Package['python-setuptools'],
    }
    
    package {'virtualenv':
        ensure     => present,
        provider   => pip,
        require    => Exec['easy_install pip'],
    }

    exec {"install-virtualenv":
        path        => '/usr/local/bin',
        command     => "virtualenv --distribute /usr/local/venv",
        creates     => "/usr/local/venv",
        require     => Package['virtualenv'],
    }

    $pip_packages = 'psutil boto-rsync pygtail requests psycopg2 sqlalchemy'
    exec {'pip-install-requirements':
        command     => "/usr/local/venv/bin/pip install ${pip_packages}",
        require     => [Exec['install-virtualenv'],
                        Package['python-dev']],
    }

}
