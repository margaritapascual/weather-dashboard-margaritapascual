# setup.py
from setuptools import setup, find_packages

setup(
    name="WeatherDashboard",
    version="1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests>=2.25.1',
        'Pillow>=8.1.0',
        'matplotlib>=3.3.4',
        'python-dotenv>=0.15.0',
    ],
    entry_points={
        'console_scripts': [
            'weather-dashboard=main:main',
        ],
    },
    package_data={
        'features': ['icons/*.png'],
    },
    python_requires='>=3.8',
)