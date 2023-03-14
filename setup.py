from setuptools import setup


setup(

    entry_points={
        'console_scripts': [
            # This is the primary entry point
            'sammvir = sammvir.run:run',
            'sammvir-stats = sammvir.stats_and_graphs:run_stats'
        ]
    }
)
