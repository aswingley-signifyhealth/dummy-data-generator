from setuptools import setup, find_packages

setup(
    name='dummy_data_generator',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'PyYAML==6.0.0',
        'pytest==7.4.2',
        'jsonschema==4.19.1',
        'mock==5.1.0',
        'setuptools~=68.2.0',
        'pandas',
        'faker'
    ],
    entry_points={
        'console_scripts': [
            'generate_dummy_data=generate_dummy_data:main',
        ],
    },
    author='Ariel Swingley',
    author_email='aswingley@signifyhealth.com',
    description='A package to generate dummy data using Faker and YAML configuration',
    url='https://github.com/aswingley-signifyhealth/dummy_data_generator',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)