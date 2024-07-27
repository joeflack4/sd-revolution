"""Working with the civit API

todo: command just for chars
"""
import os
import sys
from typing import List, Dict, Union

import click
# TODO: Add this to the click CLI
import requests

BASE_URL = "https://civitai.com/api/v1/"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}
DOWNLOAD_DIR = 'data/models/'


@click.group()
def cli():
    """todo"""
    pass


# todo: auto-handle pagination
def req(path, **kwargs) -> Union[List, Dict]:
    """Make a request"""
    # todo: proper joining using urllib or w/e
    endpoint = BASE_URL + path
    url = endpoint
    # noinspection PyUnusedLocal
    base_model = kwargs.pop('base_model', None)  # todo: figure out what to do with this if anything here
    query_params = {k: v for k, v in kwargs.items() if v}
    if query_params:
        url += '?'
        url += '&'.join([f'{k}={v}' for k, v in query_params.items()])
    response1 = requests.get(url, headers=HEADERS)
    data1 = response1.json()
    models = data1['items']
    if response1.status_code >= 300:
        print(f"Request failed with status code: {response1.status_code}", file=sys.stderr)
        raise RuntimeError(response1.text)
    if 'nextPage' in data1['metadata'] and data1['metadata']['nextPage']:
        while True:
            response_i = requests.get(data1['metadata']['nextPage'], headers=HEADERS)
            data_i = response_i.json()
            models.extend(data_i['items'])
            if 'nextPage' not in data_i['metadata'] or not data_i['metadata']['nextPage']:
                break
    return models


def download_models():
    """todo"""
    pass
    # todo: modelVersions.files[].downloadUrl (where modelVersions.files[].primary = true)


# todo match CLI for dl_qry()
@cli.command()
# Todo: figure out how to get "sailor moon" instead of just sailor moon. need to query exact match
@click.option('-q', '--query', help='Search query')
# todo: is 'character' tag reliable?
# todo: how to use:
@click.option('-t', '--tags', multiple=True, help='The tags associated with the model')
# todo: redundant? correct?; also change default to None
@click.option('-m', '--base-model', multiple=True, default=['Pony'],
    help='Base model / checkpoint, e.g. Pony')
@click.option('-s', '--sort', default='Highest Rated', type=click.Choice(['Highest Rated',
   'Most Downloaded', 'Newest']),  help='Search query')
def qry(query, tags, base_model, sort, nsfw=True):
    """todo: find_models_matching_query"""
    # query = f'"{query}"'  # todo not working with " or '
    models: List[Dict] = req('models', query=query, tags=tags, base_model=base_model, sort=sort, nsfw=nsfw)
    # todo: response query. filter char
    # todo: tags	string[]	The tags associated with the model
    # todo: filter base model?
    # todo: manually filter exact match from title or elsewhere, if API doesn't support it

    # todo: check that tags "character" is reliable. it showed up as tags=('character',). how did this show up in
    #  query params?
    #  do a filter on the tags in the response. do all of them say character?
    print()


# todo: match CLI for qry()
@cli.command()
@click.option('-o', '--output-dir', type=click.Path(writable=True), default=DOWNLOAD_DIR,
    help='Output dir')
@click.option('-q', '--query', help='Search query to filter models by name')
def dl_qry():
    """todo: download_models_matching_query
    todo: more options:
    https://github.com/civitai/civitai/wiki/REST-API-Reference#get-apiv1models
    """
    url = "https://civitai.com/api/v1/models"


if __name__ == "__main__":
    cli()
    # TODO: run a test
    # qry -q XXX
