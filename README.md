# Purpose

This is a lightweight trading application built for Coinbase Prime using Dash, an open source framework for building Python data apps.  

All scripts are written in Python3 and have been tested with versions that are not end of life.

## Installation

Simply clone the repo to run scripts from your command line.

```bash
git clone https://github.com/jc-cb/insto-trading-app-py
```

In order to run this, you will need to be running at least Python 3.8 so that you can install some key dependencies. To install dependencies, run the following: 
```
pip install -r requirements.txt
```
You will also need API key credentials within a valid Coinbase Prime portfolio in order to use this application.

After adding your keys to ``keys_example.py``, rename this file to ``keys.py``. 

You can now run the program with: 

```
python app.py
```

For information around Dash, please visit their [documentation](https://dash.plotly.com/introduction). 