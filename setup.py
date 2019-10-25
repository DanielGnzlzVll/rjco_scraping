from setuptools import setup, find_packages

def load_requirements(fname):
    with open(fname, 'r') as f:
        lines = f.readlines()
    return lines
def read_readme():
    with open('README.md', 'r') as f:
        return f.read()

setup(
    name='rjco_scraping',
    description='web scraping for "rama judicial colombiana"',
    long_description=read_readme(),
    url='https://github.com/DanielGnzlzVll/rjco_scraping',
    author='Daniel gonzalez',
    author_email='jodgonzalezvi@unal.edu.co',
    license='APACHE',
    version='0.0.5',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=load_requirements("requirements.txt"),
    entry_points='''
        [console_scripts]
        rjco_scraping=rjco_scraping.scraping:scraping_wraper
    ''',
)