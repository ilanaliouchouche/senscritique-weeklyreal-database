from setuptools import setup, find_packages

setup(name="bddr-sc",
        version="0.1",
        description="senscrtique weekreal database",
        author="Ilan",
        packages=find_packages(),
        install_requires=[
            'beautifulsoup4==4.12.2',
            'pandas==2.1.4',
            'selenium==4.16.0',
            'tqdm==4.66.1',
            'requests==2.31.0',
            'psycopg2-binary==2.9.9',
            'python-dotenv==1.0.0',
            'webdriver-manager==4.0.1',
        ],
        python_requires='==3.11.5',
)