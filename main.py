import argparse
import os
from dataclasses import dataclass
from typing import Optional

import requests


@dataclass
class Image:
    name: str
    url: str


class RedditDownloader:
    def __init__(self, args) -> None:
        self.name = args.name
        self.type = args.type
        self.time: Optional[str] = args.time
        self.folder: str = args.folder or f"downloads/{self.name}"
        self.limit: Optional[int] = args.limit or 100
        self.url = f"https://www.reddit.com/r/{self.name}/{self.type}.json"
        self.amount: int = args.amount
        self.headers = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0"
        }

    def download(self, image: Image):
        r = requests.get(image.url)

        if r.ok:
            if not os.path.exists(self.folder):
                os.makedirs(self.folder)

            with open(f"{self.folder}/{image.name}.jpg", "wb") as f:
                f.write(r.content)
        else:
            raise TypeError(f"URL returned {r.status_code}, skipped.")

    def start(self):
        session = requests.Session()
        next_page = "blank"
        count = 0
        while True:
            r = session.get(
                url=self.url,
                headers=self.headers,
                params={"t": self.time, "limit": self.limit, "after": next_page},
            )
            json = r.json()
            data = json["data"]

            for child in data["children"]:
                cdata = child["data"]
                try:
                    self.download(
                        Image(
                            name=cdata["name"],
                            url=cdata["url_overridden_by_dest"],
                        )
                    )
                    count += 1
                    print(f"Downloaded: {cdata['name']}")
                except TypeError as e:
                    print(f"Failed to download {cdata['name']}: {e}")
                except KeyError:
                    print("no url_overridden_by_dest")

                if count == self.amount:
                    exit("Finished")

            next_page = data["after"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--name",
        "-n",
        help="The name of the subreddit.",
        required=True,
    )
    parser.add_argument(
        "--amount",
        "-a",
        help="The amount of files you wish you download.",
        required=False,
        default=25,
        type=int,
    )
    parser.add_argument(
        "--type",
        "-t",
        help="The type of feed. [controversial|best|hot|new|random|rising|top]",
        required=False,
        default="top",
    )
    parser.add_argument(
        "--time",
        "-tm",
        help="The time of when the posts where made. [today|now|week|month|year|all]",
        required=False,
        default="all",
    )
    parser.add_argument(
        "--folder",
        "-f",
        help="The folder to save images to.",
        required=False,
    )
    parser.add_argument(
        "--limit",
        "-l",
        help="The amount of results to get from the API",
        required=False,
    )
    ParsedArgs = parser.parse_args()
    client = RedditDownloader(ParsedArgs)
    client.start()
