import json
import os
import urllib.parse
from datetime import datetime, timedelta
from xml.etree.ElementTree import Element, SubElement, ElementTree, parse, register_namespace
import yaml

# Register the atom namespace
register_namespace('atom', 'http://www.w3.org/2005/Atom')

# Load configuration
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

MAX_ITEMS = config.get('max_items', 50)
MAX_AGE_DAYS = config.get('max_age_days', 30)


def read_json_files(directory):
    """Read and load JSON files from the specified directory."""
    json_data = []
    for filename in os.listdir(directory):
        if filename.endswith('_rewritten.json'):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as file:
                data = json.load(file)
                json_data.append(data)
    return json_data


def create_rss_feed(json_data, output_path):
    """Create or update an RSS feed based on provided JSON data."""
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
        description.text = "UglyFeed"

        language = SubElement(channel, 'language')
        language.text = "it"

        atom_link = SubElement(channel, 'atom:link')
        atom_link.set('href', 'https://raw.githubusercontent.com/fabriziosalmi/UglyFeed/main/examples/uglyfeed-source-1.xml')
        atom_link.set('rel', 'self')
        atom_link.set('type', 'application/rss+xml')

    new_items = []
    cutoff_date = datetime.now() - timedelta(days=MAX_AGE_DAYS)
    for item in json_data:
        processed_at = datetime.strptime(
            item.get('processed_at', datetime.now().isoformat()),
            '%Y-%m-%d %H:%M:%S'
        )
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

            pub_date = SubElement(item_element, 'pubDate')
            pub_date.text = processed_at.strftime('%a, %d %b %Y %H:%M:%S GMT')

            guid = SubElement(item_element, 'guid')
            guid.text = (
                "https://github.com/fabriziosalmi/UglyFeed/"
                f"{urllib.parse.quote(item.get('title', 'Nessun Titolo'))}"
            )

            new_items.append(item_element)

    existing_items = list(channel.findall('item'))
    all_items = existing_items + new_items
    all_items.sort(
        key=lambda x: datetime.strptime(x.find('pubDate').text, '%a, %d %b %Y %H:%M:%S GMT'),
        reverse=True
    )

    trimmed_items = all_items[:MAX_ITEMS]

    for item in channel.findall('item'):
        channel.remove(item)
    for item in trimmed_items:
        channel.append(item)

    tree = ElementTree(rss)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)


def main():
    """Main function to read JSON files and create/update the RSS feed."""
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
