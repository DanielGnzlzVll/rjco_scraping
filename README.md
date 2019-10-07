# rjco_scraping (RAMA JUDICIAL COLOMBIANA)
This package allows you to do web scraping on the website of 'Rama Judicial Colombiana'.

## Install
```bash
git clone https://github.com/DanielGnzlzVll/rjco_scraping.git
cd rjco_scraping
```
### new virtualenv
```bash
virtualenv rjco
source rjco/bin/activate
```
```bash
pip install .
```
or 
```bash
python setup install
```
## Usage

### from bash

```bash
python -m rjco_scraping
```

```bash
rjco_scraping
```

### Import from python

```python
import rjco_scraping
results = rjco_scraping.scraping(text2search="sura")
#or 
rjco_scraping.scraping(text2search="sura"), output_file="result.xlsx")
```

## Windows
You can download the latest release from [here](DanielGnzlzVll/rjco_scraping/releases/latest/download/rjco_scraping.exe) then open the .exe file




