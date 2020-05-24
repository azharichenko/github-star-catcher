import argparse
import csv
import sched
from datetime import datetime, timedelta
from pathlib import Path

from requests.auth import HTTPBasicAuth
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

parser = argparse.ArgumentParser(description="")
parser.add_argument("--user", type=str)
parser.add_argument("--token", type=str)
parser.add_argument("--repo", type=str)
parser.add_argument("--owner", type=str)

args = parser.parse_args()

hour = timedelta(hours=1)

output_csv = Path(".") / "output.csv"

github_transport = RequestsHTTPTransport(
    url="https://api.github.com/graphql",
    headers={"Authorization": "token"},
    auth=HTTPBasicAuth(args.user, args.token),
)

s = sched.scheduler()


def stargazer_count(owner: str, repo_name: str) -> int:
    client = Client(transport=github_transport, fetch_schema_from_transport=True)
    query = gql(
        """
        query {{ 
        repository(name: "{repo}", owner: "{owner}") {{
        stargazers {{
          totalCount
        }}
      }}
    }}
    """.format(
            repo=repo_name, owner=owner
        )
    )
    return client.execute(query)["repository"]["stargazers"]["totalCount"]


def initalize_csv():
    with output_csv.open("w", newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['datetime', 'stargazers'])


def write_new_stargazer_entry(data):
    with output_csv.open("a", newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(data)


def calculate_next_hour():
    next_hour = datetime.today() + hour
    next_hour = next_hour - timedelta(
        microseconds=next_hour.microsecond,
        seconds=next_hour.second,
        minutes=next_hour.minute,
    )
    delta = next_hour - datetime.today()
    return delta.seconds


def main():
    data = [datetime.today().isoformat(), stargazer_count(args.owner, args.repo)]
    write_new_stargazer_entry(data)
    s.enter(calculate_next_hour(), 1, main)



if not output_csv.exists():
    initalize_csv()
s.enter(0, 1, main)
s.run()
