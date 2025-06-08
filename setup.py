from setuptools import setup, find_packages

setup(
    name='mesh-map',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'boto3',
        'folium',
        'geopy',
        'h5py',
        'matplotlib',
        'netCDF4',
        'numpy',
        'Pillow',
        'rasterio',
        'python-docx',
    ],
    entry_points={
        'console_scripts': [
            'mesh-app=run_app:main',
            'mesh-cli=mesh_cli:main',
            'mesh-watch=realtime:main',
        ]
    },
)

