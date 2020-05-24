import argparse
import csv
import sched
from pathlib import Path

from requests.auth import HTTPBasicAuth
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


parser = argparse.ArgumentParser(description="")
parser.add_argument("--user", type=str)
parser.add_argument("--token", type=str)
parser.add_argument('--repo', type=str)
parser.add_argument('--owner', type=str)

args = parser.parse_args()


output_csv = Path('.') / 'output.csv'


github_transport = RequestsHTTPTransport(
    url='https://api.github.com/graphql',
    headers={'Authorization': 'token'},
    auth=HTTPBasicAuth(args.user, args.token)
)

cycle = {
    "hourly": 60 * 60,
    "daily": 60 * 60 * 24
}


def stargazer_count(owner: str, repo_name: str) -> int:
    client = Client(transport=github_transport, fetch_schema_from_transport=True)
    query = gql('''
        query {{ 
        repository(name: "{repo}", owner: "{owner}") {{
        stargazers {{
          totalCount
        }}
      }}
    }}
    '''.format(repo=repo_name, owner=owner))
    return client.execute(query)['repository']['stargazers']['totalCount']


def write_new_stargazer_entry():
    with output_csv.open('w') as csv_file:
        pass


print(stargazer_count(args.owner, args.repo))
