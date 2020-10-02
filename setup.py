# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in tg_steel/__init__.py
from tg_steel import __version__ as version

setup(
	name='tg_steel',
	version=version,
	description='Tg Steel',
	author='Atrina Technologies Pvt. Ltd.',
	author_email='developers@atritechnocrat.in',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
