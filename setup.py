from setuptools import setup


setup(

    entry_points={
        'console_scripts': [
            # This is the primary entry point
            'sammvir = sammvir.run:run',
        ]
    }
)
