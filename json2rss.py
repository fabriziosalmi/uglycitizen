import json
import os
import urllib.parse
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree, register_namespace

# Register the atom namespace
register_namespace('atom', 'http://www.w3.org/2005/Atom')

def read_json_files(directory):
    json_data = []
    for filename in os.listdir(directory):
        if filename.endswith('_rewritten.json'):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
                json_data.append(data)
    return json_data

def create_rss_feed(json_data, output_path):
    rss = Element('rss')
    rss.set('version', '2.0')
    rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')  # Correct namespace declaration

    channel = SubElement(rss, 'channel')

    title = SubElement(channel, 'title')
    title.text = "Feed di Notizie UglyCitizen"

    link = SubElement(channel, 'link')
    link.text = "https://github.com/fabriziosalmi/UglyFeed"

    description = SubElement(channel, 'description')
    description.text = "Feed di notizie aggregato e riscritto da UglyCitizen"

    language = SubElement(channel, 'language')
    language.text = "it"

    # Add the atom:link element
    atom_link = SubElement(channel, 'atom:link')
    atom_link.set('href', 'https://github.com/fabriziosalmi/UglyFeed/uglyfeeds/uglyfeed.xml')
    atom_link.set('rel', 'self')
    atom_link.set('type', 'application/rss+xml')

    for item in json_data:
        item_element = SubElement(channel, 'item')

        item_title = SubElement(item_element, 'title')
        item_title.text = item.get('title', 'Nessun Titolo')

        item_description = SubElement(item_element, 'description')
        content = item.get('content', 'Nessun Contenuto')
        
        # Append source links to the description
        if 'links' in item:
            content += "<br/><br/><small>Fonti:</small><br/>"
            for link in item['links']:
                content += f'<small><a href="{link}" target="_blank">{link}</a></small><br/>'
        
        item_description.text = content

        pubDate = SubElement(item_element, 'pubDate')
        processed_at = item.get('processed_at', datetime.now().isoformat())
        pubDate.text = datetime.strptime(processed_at, '%Y-%m-%d %H:%M:%S').strftime('%a, %d %b %Y %H:%M:%S GMT')

        # Add guid element
        guid = SubElement(item_element, 'guid')
        guid.text = "https://github.com/fabriziosalmi/UglyFeed/{}".format(urllib.parse.quote(item.get('title', 'Nessun Titolo')))

    tree = ElementTree(rss)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)

def main():
    rewritten_dir = 'rewritten'
    output_path = os.path.join('uglyfeeds', 'uglyfeed.xml')

    os.makedirs('uglyfeeds', exist_ok=True)

    json_data = read_json_files(rewritten_dir)

    if json_data:
        create_rss_feed(json_data, output_path)
        print(f'RSS feed successfully created at {output_path}')
    else:
        print('Nessun file JSON trovato nella directory riscritta.')

if __name__ == '__main__':
    main()
