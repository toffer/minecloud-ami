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

    file {"/usr/local/venv/requirements.txt":
        owner       => root,
        group       => root,
        mode        => 0644,
        source      => 'puppet:///modules/virtualenv/requirements.txt',
        require     => Exec['install-virtualenv'],
    }

    # Temporary hack to get around pip 1.4 error.
    # See https://github.com/toffer/minecloud-ami/issues/8
    file { '/usr/venv':
        ensure      => 'link',
        target      => '/usr/local/venv',
        require     => Exec['install-virtualenv'],
    }

    $pip = '/usr/local/venv/bin/pip'
    $requirements = '/usr/local/venv/requirements.txt'
    exec {'pip-install-requirements':
        command     => "$pip install -r $requirements",
        require     => [Exec['install-virtualenv'],
                        File['/usr/venv'],
                        File['/usr/local/venv/requirements.txt'],
                        Package['python-dev']],
    }

}
