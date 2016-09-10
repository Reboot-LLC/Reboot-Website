import requests
import json


def fetch_github(url, path):
    response = requests.get(url)
    content = response.json()
    with open(path, 'w') as outfile:
        json.dump(content, outfile)
    outfile.close()

# REPLACE WITH OUR USERNAME */
fetch_github('https://api.github.com/users/vc1492a/repos', 'static/data/full_github.json')


def prep_github(source, path):
    with open(source, 'r') as readfile:
        json_file = json.load(readfile)
        content_array = []
        for entry in json_file:
            content = {}
            entry_language = entry['language']
            if entry_language is not None:
                content['language'] = entry['language']
                content['last_commit'] = entry['pushed_at']
                content['url'] = entry['html_url']
                content['stars'] = entry['stargazers_count']
                content['watchers'] = entry['watchers_count']
                content['name'] = entry['name']
                content['description'] = entry['description'].strip()
                content_array.append(content)
    readfile.close()
    with open(path, 'w') as outfile:
        outfile.write("github = ")
        json.dump(content_array, outfile)
    outfile.close()

prep_github('static/data/full_github.json', 'static/data/display_github.json')
