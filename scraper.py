import logging
import sys
from argparse import ArgumentParser
from datetime import datetime, timezone
from json import dumps
from pathlib import Path
from random import randrange
from time import sleep, time

from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import RequestException

MAX_CONSECUTIVE_ERRORS = 3
REQUEST_TIMEOUT = 30
DUMP_FOLDER_NAME = "dumps"
BASE_URL = "https://crackmes.one/lasts"

logging.basicConfig(
    format="{asctime} - {levelname} - {message}",
    style="{",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

dump_folder = Path(DUMP_FOLDER_NAME)
dump_folder.mkdir(exist_ok=True)


def is_table_empty(html_str: str, url: str) -> bool:
    if isinstance(html_str, (str, bytes)):
        soup = BeautifulSoup(html_str, "lxml")
    else:
        soup = html_str

    table = soup.find("tbody", id="content-list")

    if not table:
        logger.info("No table found. (%s)", url)
        return True

    rows = table.find_all("tr")
    if len(rows) == 0:
        logger.info("The tbody is empty. (%s)", url)
        return True

    return False


def dump_htmls():
    start_time = time()

    page_num = 1
    consecutive_errors = 0

    while True:
        url = f"{BASE_URL}/{page_num}"
        output_file = dump_folder / f"page_{page_num:03d}.html"

        logger.info("%s: Downloading to %s", url, output_file)

        if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
            logger.error(
                "%s: Aborting due to %d consecutive failures.",
                url,
                MAX_CONSECUTIVE_ERRORS,
            )
            break

        if consecutive_errors > 0:
            logger.warning(
                "%s: Retry attempt %d/%d",
                url,
                consecutive_errors,
                MAX_CONSECUTIVE_ERRORS,
            )

        try:
            with get(url, timeout=REQUEST_TIMEOUT) as resp:
                resp.raise_for_status()
                if is_table_empty(resp.content, url):
                    break

                output_file.write_bytes(resp.content)

            page_num += 1
            consecutive_errors = 0
            logger.info("%s: Downloaded to %s", url, output_file)
        except RequestException as e:
            logger.error("%s: Error downloading %s", url, e)
            consecutive_errors += 1
        except Exception as e:
            logger.error("%s: Error Occured %s", url, e)
            consecutive_errors += 1
        finally:
            sleep_duration = randrange(8, 15)  # generous sleep time range ^__^
            logger.info("Waiting for %s seconds.", sleep_duration)
            sleep(sleep_duration)

    end_time = time()
    logger.info(
        "Downloaded %s pages (took %ss)", page_num, round(end_time - start_time, 2)
    )


def parse_datetime(datetime_str):
    try:
        dt = datetime.strptime(datetime_str, r"%I:%M %p %m/%d/%Y")
        utc_dt = dt.replace(tzinfo=timezone.utc)
        return utc_dt.isoformat()
    except (ValueError, TypeError):
        return None


def safe_float(value, default=-1.0) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value, default=-1) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def extract_link_data(td):
    link = td.find("a")
    return {
        "name": td.get_text(strip=True),
        "link": td.find("a")["href"] if link else None,
    }


def extract_chall_from_row(tr) -> dict | None:
    if not tr:
        return None

    tds = tr.find_all("td")
    if len(tds) < 10:
        logger.debug("Row has insufficient columns: %d", len(tds))
        return None

    try:
        return {
            "problem": extract_link_data(tds[0]),
            "author": tds[1].get_text(strip=True),
            "lang": tds[2].get_text(strip=True),
            "arch": tds[3].get_text(strip=True),
            "difficulty": safe_float(tds[4].get_text(strip=True)),
            "quality": safe_float(tds[5].get_text(strip=True)),
            "platform": tds[6].get_text(strip=True),
            "date": parse_datetime(tds[7].get_text(strip=True)),
            "writeups": safe_int(tds[8].get_text(strip=True)),
            "comments": safe_int(tds[9].get_text(strip=True)),
        }
    except Exception as e:
        logger.error("Unexpected error parsing row: %s", e)
        return None


def extract_challs_from_table(soup: BeautifulSoup, file_name: str) -> list | None:
    challs = []

    if is_table_empty(soup, file_name):
        return None

    table = soup.find("tbody", id="content-list")
    for row in table.find_all("tr"):
        chall = extract_chall_from_row(row)
        if chall:
            challs.append(chall)
        else:
            logger.info("%s: No crackme found in row.", file_name)

    return challs


def build_challs_json():
    data = {"challs": []}
    html_files = list(dump_folder.glob("*.html"))

    if len(html_files) == 0:
        logger.info("No html files found.")
        return

    logger.info("Started extracting crackmes from %d html files", len(html_files))

    for idx, file_name in enumerate(html_files, start=1):
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "lxml")

            challs = extract_challs_from_table(soup, file_name)
            if challs:
                data["challs"].extend(challs)
                logger.debug("%s: Processed %d challenges", file_name.name, len(challs))

        except Exception as e:
            logger.error("%s: Error processing %s", file_name, e)
            continue

    data["challs"] = sorted(data["challs"], key=lambda x: x['date'])
    data["last_updated"] = datetime.now(timezone.utc).isoformat()
    challs_json = dump_folder / "challs.min.json"
    with challs_json.open("w") as f:
        f.write(dumps(data, indent=2))

    logger.info(
        "Extracted %d challenges from %d html files and written challs.min.json",
        len(data["challs"]),
        idx,
    )


def main():
    parser = ArgumentParser()
    parser.add_argument("-d", "--dump-htmls", action="store_true")
    parser.add_argument("-e", "--extract-challs", action="store_true")

    args = parser.parse_args()

    if not (args.dump_htmls or args.extract_challs):
        print("Use --dump-html or --extract-challs")
        sys.exit(1)

    if args.dump_htmls:
        dump_htmls()

    if args.extract_challs:
        build_challs_json()


if __name__ == "__main__":
    main()
