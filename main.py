import logging
import threading
from scan import LiquidityPoolExtractor
from liquidity import LiquidityInfoRetriever
from market import MarketDataFetcher

# Setup logging
logging.basicConfig(filename='error.log', level=logging.ERROR)

def run_extractor(chains):
    while True:
        try:
            delay_seconds = 10  # Set delay to x seconds
            extractor = LiquidityPoolExtractor(chains, delay_seconds=delay_seconds)
            extractor.run_extraction_loop()
        except Exception as e:
            logging.error(f"Error in LiquidityPoolExtractor: {str(e)}")

def run_retriever():
    while True:
        try:
            liquidity_retriever = LiquidityInfoRetriever(delay=10)  # Set delay to x seconds)
            liquidity_retriever.run()
        except Exception as e:
            logging.error(f"Error in LiquidityInfoRetriever: {str(e)}")

def run_fetcher():
    while True:
        try:
            price_fetcher = MarketDataFetcher(delay=10)  # Set delay to x seconds
            price_fetcher.run()
        except Exception as e:
            logging.error(f"Error in MarketDataFetcher: {str(e)}")

if __name__ == "__main__":
    chains = ['ether']

    # Create threads for each class and start them
    extractor_thread = threading.Thread(target=run_extractor, args=(chains,))
    retriever_thread = threading.Thread(target=run_retriever)
    fetcher_thread = threading.Thread(target=run_fetcher)

    extractor_thread.start()
    retriever_thread.start()
    fetcher_thread.start()

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

    print("All tasks stopped.")
