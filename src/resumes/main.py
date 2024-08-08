import sys
import time
import logging
import os
from dotenv import load_dotenv

import headhunter
import storage

loaded_env = load_dotenv(".env")
if not loaded_env:
    exit(".env file not found!")

sys.setrecursionlimit(int(os.getenv("RECURSION_LIMIT")))

logging.basicConfig(filename="info.log", filemode='w', format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S', level=logging.DEBUG)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)


def main():
    start = time.perf_counter()
    logging.warning("Not all resumes are parsed, as some are only available to authorized users or employers")
    positions = storage.GetPositions()
    for profession in positions:
        logging.info(f"Searching for profession {profession.Id}: {profession.Title}")
        headhunter.find_profession(profession)
        
        logging.info(f"Profession parsed {profession.Id}: {profession.Title}")
        print(f"Profession parsed {profession.Id}: {profession.Title}")
        storage.set_parsed_to_profession(profession.Id)
    
    print(f"Time: {time.perf_counter() - start} seconds.")

        
if __name__ == "__main__":
    main()