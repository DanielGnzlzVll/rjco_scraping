# rjco_scraping (RAMA JUDICIAL COLOMBIANA)
This package allows you to do web scraping on the website of 'Rama Judicial Colombiana'.

## Requirements
The major requirement is the web browser Google Chrome,
this program *ONLY* work properly with Chrome

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

### from console

```bash
python -m rjco_scraping 
## search by ´´´numero de radicado´´
python -m rjco_scraping --code
```

```bash
rjco_scraping
```

### Import from python

```python
import rjco_scraping
results = rjco_scraping.scraping_by_text(text2search="sura")
# or 
rjco_scraping.scraping_by_text(text2search="sura", output_file="result.xlsx")

# search by ´´numero de radiacion´´
rjco_scraping.scraping_by_number(code="05088310300120150079003",
    output_file="result.json"
)

```

## Windows
You can download the latest release from [here](https://github.com/DanielGnzlzVll/rjco_scraping/releases/latest/download/rjco_scraping.exe) then open the .exe file.




