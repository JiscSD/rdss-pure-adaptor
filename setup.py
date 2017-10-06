from setuptools import setup

setup(
    name='pure_adaptor',
    version='0.1.0',
    description='Adaptor between PURE APIs and the RDSS',
    install_requires=[
        'boto3',
        'requests',
    ],
    tests_require=[
        'pytest',
    ],
    author='Finlay McCourt',
    packages=['pure_adaptor'],
    entry_points={
        'console_scripts': [
            'pure_adaptor = pure_adaptor.pure_adaptor:main',
        ],
    },
    include_package_data=True,
)
