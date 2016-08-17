from setuptools import setup, find_packages

setup(
    name='pybot-youpi2-shell',
    setup_requires=['setuptools_scm'],
    use_scm_version={
        'write_to': 'src/pybot/youpi2/shell/__version__.py'
    },
    namespace_packages=['pybot', 'pybot.youpi2'],
    packages=find_packages("src"),
    package_dir={'': 'src'},
    url='',
    license='',
    author='Eric Pascual',
    author_email='eric@pobot.org',
    install_requires=['pybot-youpi2', 'pybot-lcd-fuse>=0.20.1'],
    download_url='https://github.com/Pobot/PyBot',
    description='Youpi2 arm runtime shell',
    entry_points={
        'console_scripts': [
            'youpi2-shell = pybot.youpi2.shell.toplevel:main',
        ]
    }
)
