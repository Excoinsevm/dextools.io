import logging
import threading
from scan import LiquidityPoolExtractor
from liquidity import LiquidityInfoRetriever
from market import MarketDataFetcher
from info import InfoDataFetcher
import config

# Setup logging
logging.basicConfig(filename='error.log', level=logging.ERROR)
delay_module = config.delay_module

def run_extractor(chains):
    while True:
        try:
            extractor = LiquidityPoolExtractor(chains, delay_seconds=5*delay_module)
            extractor.run_extraction_loop()
        except Exception as e:
            logging.error(f"Error in LiquidityPoolExtractor: {str(e)}")

def run_retriever():
    while True:
        try:
            liquidity_retriever = LiquidityInfoRetriever(delay=delay_module)  # Set delay to x seconds)
            liquidity_retriever.run()
        except Exception as e:
            logging.error(f"Error in LiquidityInfoRetriever: {str(e)}")

def run_fetcher():
    while True:
        try:
            price_fetcher = MarketDataFetcher(delay=delay_module)  # Set delay to x seconds
            price_fetcher.run()
        except Exception as e:
            logging.error(f"Error in MarketDataFetcher: {str(e)}")

def run_infodata():
    while True:
        try:
            info_fetcher = InfoDataFetcher(delay=delay_module)  # Set delay to x seconds
            info_fetcher.run()
        except Exception as e:
            logging.error(f"Error in InfoDataFetcher: {str(e)}")

if __name__ == "__main__":
    # read list of chains from file
    with open('chains.txt', 'r') as f:
        chains = f.read().split('\n')
    # Create threads for each class 
    extractor_thread = threading.Thread(target=run_extractor, args=(chains,))
    retriever_thread = threading.Thread(target=run_retriever)
    fetcher_thread = threading.Thread(target=run_fetcher)
    info_thread = threading.Thread(target=run_infodata)
    #start threads
    extractor_thread.start()
    retriever_thread.start()
    fetcher_thread.start()
    info_thread.start()

    print("All tasks started.")

    # Wait for keyboard interrupt to stop the tasks
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Stopping all tasks.")
        extractor_thread.join()
        retriever_thread.join()
        fetcher_thread.join()
        info_thread.join()
    print("All tasks stopped.")
