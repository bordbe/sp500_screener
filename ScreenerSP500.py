import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
from queue import Queue
from threading import Thread
import logging
import os
from datetime import datetime
import numpy as np


def configure_logger(directory):
    # configure logger
    path_log = os.path.join(directory, "what_happens.log")
    if os.path.exists(path_log):
        os.remove(path_log)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    f_handler = logging.FileHandler(path_log)
    f_handler.setLevel(logging.DEBUG)
    f_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    f_handler.setFormatter(f_format)
    logger.addHandler(f_handler)
    return logger


def get_sp500_tickers():
    """retrieve the constituents of the SP500 from wikipedia"""
    resp = requests.get("http://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    soup = bs(resp.text, "lxml")
    table = soup.find("table", {"class": "wikitable sortable"})
    tickers = []
    # parse the tab containing the constituents
    for row in table.findAll("tr")[1:]:
        ticker = row.findAll("td")[0].text
        tickers.append(ticker)
    logger.info(f"SP500 composed of {len(tickers)} securities")
    return tickers


def crawl_finviz(q, result):
    """scrape data from FinViz"""
    # threaded function for queue processing
    while not q.empty():
        try:
            work = q.get()  # fetch new work from the Queue
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
                "Upgrade-Insecure-Requests": "1",
                "Cookie": "v2=1495343816.182.19.234.142",
                "Accept-Encoding": "gzip, deflate, sdch",
                "Referer": "http://finviz.com/quote.ashx?t=",
            }
            resp = requests.get(work[1], headers=headers)
            soup = bs(resp.content, "html.parser")
            table = soup.find("table", {"class": "snapshot-table2"})
            # dataframe containing the metrics for the ticker
            df = pd.DataFrame(columns=metric)
            for m in df.columns:
                # fill the dataframe with the value from finviz tab
                if m == "Ticker":
                    df.loc[work[0], m] = soup.find("table", {"class": "fullview-title"}).find_all("tr")[1].text
                else:
                    df.loc[work[0], m] = table.find(text=m).find_next(class_="snapshot-td2").text
            result.append(df)

        except Exception as e:
            logger.error(e)
            logger.error(work[0], "not found")
        # signal to the queue that task has been processed
        q.task_done()

    return True


def main(dict_tick_url):
    """run screener

    Args:
        dict_tick_url (dict): contains tickers as keys, and urls associated as values

    Returns:
        [df]: screener
    """
    # set up the queue to hold all the urls
    q = Queue(maxsize=0)
    urls = list(dict_tick_url.values())
    num_theads = min(50, len(urls))
    results = []  # list to store the results that will be shared accross the threads
    # load up the queue with the urls to fetch and the index for each job (as a tuple):
    for ticker, url in dict_tick_url.items():
        # populating Queue with tasks
        q.put((ticker, url))

    # starting worker threads on queue processing
    for _ in range(num_theads):
        worker = Thread(target=crawl_finviz, args=(q, results))
        worker.setDaemon(True)
        # setting threads as "daemon" allows main program to exit eventually even if these dont finish correctly.
        worker.start()
    # now we wait until the queue has been processed
    q.join()
    logger.info("All threads closed : data scraping ended")
    return pd.concat(results)


if __name__ == "__main__":
    directory = os.path.dirname(os.path.abspath(__file__))
    logger = configure_logger(directory)
    logger.info("====================== SCREENER SP500 ======================")
    # get tickers
    logger.info("Retrieving SP500 constituents")
    tickers = get_sp500_tickers()
    tickers = list(map(lambda ticker: ticker.replace(".", "-"), tickers))  # "." on Wiki but "-" on FinViz
    # create urls
    urls = ((len(tickers) * "http://finviz.com/quote.ashx?t={}").format(*tickers)).split("\n")
    urls = urls[:-1]  # last item is None because of "\n"
    # format tickers
    tickers = list(map(lambda ticker: ticker.replace("\n", ""), tickers))
    # create dict
    dict_tick_url = dict(zip(tickers, urls))
    # metrics retrieved
    metric = ["Ticker", "Market Cap", "Price", "P/E", "PEG", "P/B", "Quick Ratio", "Debt/Eq", "ROI", "ROE", "EPS Q/Q", "Insider Own", "Dividend %"]
    # get the screener
    logger.info("Running screener, starting threads")
    df_screen = main(dict_tick_url)
    # format to allow filtering
    df_screen["Market Cap"] = df_screen["Market Cap"].str.replace("B", "")
    df_screen[["ROI", "ROE", "EPS Q/Q", "Insider Own", "Dividend %"]] = df_screen[["ROI", "ROE", "EPS Q/Q", "Insider Own", "Dividend %"]].apply(lambda c: c.str.replace("%", ""))
    df_screen = df_screen.replace("-", np.nan)

    # TODO: chose other criteria for filtering if you want
    criteria = (df_screen["P/B"].astype(float) < 1.5) & (df_screen["ROI"].astype(float) > 0.1)
    df_screen = df_screen[criteria]

    # sort
    df_screen.iloc[:, 1:] = df_screen.iloc[:, 1:].astype(float)
    df_screen = df_screen.sort_values(by="ROE", ascending=False)

    # extraction
    today = datetime.today().strftime("%Y%m%d")
    df_screen.to_csv(os.path.join(directory, "screens", f"screener_sp500_{today}.csv"), header=True, index=False)
    logger.info(f"The screen found {len(df_screen)} answering to the criterias")
