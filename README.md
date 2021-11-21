# SP500 Screener
![GitHub all releases](https://img.shields.io/github/downloads/bordbe/sp500_screener/total)
![GitHub top language](https://img.shields.io/github/languages/top/bordbe/sp500_screener?color=yellow)
![Bitbucket open issues](https://img.shields.io/bitbucket/issues/bordbe/sp500_screener)
![GitHub forks](https://img.shields.io/github/forks/bordbe/sp500_screener?style=social)
![GitHub Repo stars](https://img.shields.io/github/stars/bordbe/sp500_screener?style=social)

Here is a script to screen the constituents of the SP500. The criteria used is to have `P/B ratio < 1.5` **and** `ROI above 10%`, then the securities passing this condition are sorting by ROE. 

## 🫖 About The Project

The constituents of the SP500 are retrieved from Wikipedia : https://en.wikipedia.org/wiki/List_of_S%26P_500_companies, while the financial information comes from FinViz : https://finviz.com/. For the record, FinViz offers a great built-in screeners construction, however this project opens broader possibilities.

## 🏁 Getting Started

To get a local copy up and running follow these simple steps.

### ✅ Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* Python : https://www.python.org/downloads/
* Git
```sh
sudo apt-get install git
```
* Spreadsheet software : Microsoft Excel, Google Sheets or Apple Numbers would do just fine to visualize the results

### 📥 Installation
 
1. Clone the repo
```sh
git clone https://github.com/NicolasBrondin/basic-readme-template
```
2. Install the required python libraries
```sh
pip install -r requirements.txt
```

## 🔎 Usage

To run the script just enter the following command in a terminal :
```sh
python ScreenerSP500.py
```
The code will return you a CSV file like below :

![Image](/img/example_res.png)

You will find it in the folder **screens**.

---
To make this screener fast I used Threading. Threads provide a way to improve a script performance through parallelism.

_For more examples, please refer to the [Documentation](https://docs.python.org/3/library/threading.html)_


## 🤝 Support

Contributions, issues, and feature requests are welcome!

Give a ⭐️ if you like this project!

