# json2rss.py

## Introduction
This script reads JSON files from a specified directory, processes the data, and generates or updates an RSS feed in XML format. The RSS feed includes news items with titles, descriptions, publication dates, and other relevant metadata.

## Input/Output

### Input
- **Configuration File**: `config.yaml` which contains the maximum number of items (`max_items`) and the maximum age of items in days (`max_age_days`).
- **JSON Files**: JSON files located in the `rewritten` directory with the suffix `_rewritten.json`.

### Output
- **RSS Feed**: An updated `uglyfeed.xml` RSS feed in the `uglyfeeds` directory.

## Functionality

### Features
1. **Load Configuration**: Reads settings from a `config.yaml` file.
2. **Read and Process JSON Files**: Reads JSON files, extracts and filters data based on configuration settings.
3. **Create or Update RSS Feed**: Generates or updates an RSS feed with the processed data.
4. **Namespace Registration**: Registers the Atom namespace for the RSS feed.

## Code Structure

### Imports
```python
import json
import os
import urllib.parse
from datetime import datetime, timedelta
from xml.etree.ElementTree import Element, SubElement, ElementTree, parse, register_namespace
import yaml
```
- **json**: For reading JSON files.
- **os**: For file and directory operations.
- **urllib.parse**: For URL handling.
- **datetime**: For date and time operations.
- **xml.etree.ElementTree**: For creating and manipulating XML.
- **yaml**: For reading YAML configuration files.

### Namespace Registration
```python
register_namespace('atom', 'http://www.w3.org/2005/Atom')
```
Registers the Atom namespace for use in the RSS feed.

### Configuration Loading
```python
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
```
Loads configuration settings from `config.yaml`.

### JSON File Reading
```python
def read_json_files(directory):
    json_data = []
    for filename in os.listdir(directory):
        if filename.endswith('_rewritten.json'):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
                json_data.append(data)
    return json_data
```
Reads JSON files from the specified directory and returns the data.

### RSS Feed Creation
```python
def create_rss_feed(json_data, output_path):
    if os.path.exists(output_path):
        tree = parse(output_path)
        rss = tree.getroot()
        channel = rss.find('channel')
    else:
        rss = Element('rss')
        rss.set('version', '2.0')
        rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')
        channel = SubElement(rss, 'channel')

        title = SubElement(channel, 'title')
        title.text = "Feed di Notizie UglyCitizen"

        link = SubElement(channel, 'link')
        link.text = "https://github.com/fabriziosalmi/UglyFeed"

        description = SubElement(channel, 'description')
        description.text = "Feed di notizie aggregato e riscritto da UglyCitizen"

        language = SubElement(channel, 'language')
        language.text = "it"

        atom_link = SubElement(channel, 'atom:link')
        atom_link.set('href', 'https://github.com/fabriziosalmi/UglyFeed/uglyfeeds/uglyfeed.xml')
        atom_link.set('rel', 'self')
        atom_link.set('type', 'application/rss+xml')

    new_items = []
    cutoff_date = datetime.now() - timedelta(days=MAX_AGE_DAYS)
    for item in json_data:
        processed_at = datetime.strptime(item.get('processed_at', datetime.now().isoformat()), '%Y-%m-%d %H:%M:%S')
        if processed_at >= cutoff_date:
            item_element = Element('item')

            item_title = SubElement(item_element, 'title')
            item_title.text = item.get('title', 'Nessun Titolo')

            item_description = SubElement(item_element, 'description')
            content = item.get('content', 'Nessun Contenuto')

            if 'links' in item:
                content += "<br/><br/><small><b>Fonti</b></small><br/><ul>"
                for link in item['links']:
                    content += f'<li><small><a href="{link}" target="_blank">{link}</a></small></li>'
                content += "</ul>"

            api = item.get('api', 'Unknown API')
            model = item.get('model', 'Unknown Model')
            content += f'<br/><br/><small>Generated by <b>{model}</b> via <b>{api.capitalize()}</b></small>'

            item_description.text = content

            pubDate = SubElement(item_element, 'pubDate')
            pubDate.text = processed_at.strftime('%a, %d %b %Y %H:%M:%S GMT')

            guid = SubElement(item_element, 'guid')
            guid.text = "https://github.com/fabriziosalmi/UglyFeed/{}".format(urllib.parse.quote(item.get('title', 'Nessun Titolo')))

            new_items.append(item_element)

    existing_items = list(channel.findall('item'))
    all_items = existing_items + new_items
    all_items.sort(key=lambda x: datetime.strptime(x.find('pubDate').text, '%a, %d %b %Y %H:%M:%S GMT'), reverse=True)

    trimmed_items = all_items[:MAX_ITEMS]

    for item in channel.findall('item'):
        channel.remove(item)
    for item in trimmed_items:
        channel.append(item)

    tree = ElementTree(rss)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
```
Creates or updates the RSS feed with new items filtered by age and sorted by publication date.

### Main Function
```python
def main():
    rewritten_dir = 'rewritten'
    output_path = os.path.join('uglyfeeds', 'uglyfeed.xml')

    os.makedirs('uglyfeeds', exist_ok=True)

    json_data = read_json_files(rewritten_dir)

    if json_data:
        create_rss_feed(json_data, output_path)
        print(f'RSS feed successfully created at {output_path}')
    else:
        print('No JSON files found in the rewritten directory.')

if __name__ == '__main__':
    main()
```
- **main Function**: Sets up directories, reads JSON data, and creates the RSS feed.
- **Execution**: The script runs the main function if executed directly.

## Usage Example
1. Create a `config.yaml` file with the following content:
    ```yaml
    max_items: 50
    max_age_days: 30
    ```
2. Place the JSON files in the `rewritten` directory.
3. Run the script:
    ```bash
    python json2rss.py
    ```
4. The RSS feed will be created or updated at `uglyfeeds/uglyfeed.xml`.
