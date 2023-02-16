from setuptools import setup

setup(
    name='media_list',
    packages=['media_list'],
    include_package_data=True,
    install_requires=[
        'flask',
        'prettytable'
    ],
    devtool='inline-source-map',
)
