from setuptools import setup

setup(
    name='MkDocsAwesomeListPlugin',
    version='0.1.0',
    packages=['mkdocs_awesome_list_plugin'],
    url='https://github.com/carlosperate/mkdocs-awesome-list-plugin',
    license='MIT',
    author='Carlos Pereira Atencio',
    author_email='carlosperate@embeddedlog.com',
    description='Description.',
    install_requires=['mkdocs'],

    # The following rows are important to register your plugin.
    # The format is "(plugin name) = (plugin folder):(class name)"
    # Without them, mkdocs will not be able to recognize it.
    entry_points={
        'mkdocs.plugins': [
            'awesome-list = mkdocs_awesome_list_plugin.awesomelist:AwesomeList',
        ]
    },
)
