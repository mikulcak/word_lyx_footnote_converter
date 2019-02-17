import sys
from lxml import etree

from termcolor import colored

import re

import json

from pyzotero import zotero
from pyzotero import zotero_errors

if len(sys.argv) < 5:
    sys.exit()

output_lyx = True

main_document_xml = sys.argv[1]
footnote_xml = sys.argv[2]
zotero_library_id = sys.argv[3]
zotero_api_key = sys.argv[4]

nsmap = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

# local_zotero_cache = {}


# def load_local_zotero_cache():
    # with open('data.txt') as json_file:
        # local_zotero_cache = json.load(json_file)



def create_citation_command_from_footnote_list(footnote_list):
    print("Getting information for footnote with information " + str(footnote_list))
    result = "EMPTY-CITATION-FIX-ME"
    if footnote_list is not None:
        result = "\\autocites"
        for entry in footnote_list:
            if 'prefix' in entry.keys():
                result += ("[" + entry['prefix'] + "]")
            else:
                result += "[]"
            if 'locator' in entry.keys():
                result += ("[" + entry['locator'] + "]")
            else:
                result += "[]"
            if 'uri' in entry.keys():
                result += ("{" + get_biblatex_cite_key_from_zotero_api(entry['uri']) + "}")
                # result.append(entry['uri'])
    return result


def parse_citation_key(extra_field):
    # return extra_field.lstrip("Citation Key: ")
    # return extra_field.replace()
    # re.sub()
    return re.sub(r'.*\W*(citation key:)\W*', '', extra_field, flags=re.IGNORECASE)


def get_zotero_item_key_from_uri(uri):
    return uri.split('/')[-1]


def get_biblatex_cite_key_from_zotero_api(citation_uri):
    # items = zot.top(limit=5)
    # print(get_zotero_item_key_from_uri(citation_uri))
    item_key = str(get_zotero_item_key_from_uri(citation_uri))
    # if local_zotero_cache[item_key] is not None:

    with open('data.txt') as json_file:
        local_zotero_cache = json.load(json_file)

    print(colored(str(local_zotero_cache.keys()), 'green'))
    if item_key not in local_zotero_cache.keys():
        print("Item not in cache, querying Zotero API")
        try:
            zot = zotero.Zotero(zotero_library_id, 'user', zotero_api_key)
            item = zot.item(item_key)
            local_zotero_cache[item_key] = item
            with open('data.txt', 'w') as outfile:
                json.dump(local_zotero_cache, outfile)
        except zotero_errors.ResourceNotFound:
            return "INFORMATION-FOR-URI-" + citation_uri + "-NOT-FOUND-FIX-ME"
    else:
        print("Found item in local cache")
        item = local_zotero_cache[item_key]
    return parse_citation_key(item['data']['extra'])


def extract_csl_data_from_footnote(csl_data):
    # print(csl_data)
    json_data = json.loads(csl_data.lstrip('ADDIN ZOTERO_ITEM CSL_CITATION'))
    # print(json_data.dumps())
    # print(json.dumps(json_data, indent=4))
    # bib_source = CiteProcJSON(json_data)
    # print(json_data['citationItems'])
    result = []
    for citation_item in json_data['citationItems']:
        new_dict = {}
        # result.append({})
        # print(citation_item['uri'])
        new_dict['uri'] = citation_item['uri'][0]
        if 'prefix' in citation_item.keys():
            new_dict['prefix'] = citation_item['prefix']
            # print(citation_item['prefix'])
        if 'locator' in citation_item.keys():
            new_dict['locator'] = citation_item['locator']
            # print(citation_item['locator'])
        result.append(new_dict)
    # print(json_data['prefix'])
    # print(json_data['locator'])
    return result


def get_footnote_information(id):
    print(colored("Looking for citation id " + id, 'red'))
    tree = etree.parse(footnote_xml)
    # root = tree.getroot()
    results = tree.xpath("//w:footnotes/w:footnote/w:p/w:r/w:instrText",
                         namespaces=nsmap)
    for footnote in results:
        if str(footnote.getparent().getparent().getparent().get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id")) == id:
            # print(footnote.text)
            return extract_csl_data_from_footnote(footnote.text)


class List_object:
    footnote = False
    footnote_information = []

    def __str__(self):
        # print("I am a list object")
        if self.footnote:
            # return ("I am a footnote.")
            # result = self.footnote_information
            return colored(self.id + ": " + str(self.footnote_information), 'red')

        else:
            # return ("I am text.")
            return self.text


def main():
    tree = etree.parse(main_document_xml)

    root = tree.getroot()

    # collected_text_list = []
    document_content = []

    for child in root[0]:
        # print(child.tag)
        for child in child:
            # print(child.tag)
            # print('\t' + child.tag)
            # print(colored(child.get('t'), 'green'))
            # print(child.tag)
            # current_localname = etree.QName(child.tag).localname
            # print(current_localname)
            for child in child:
                # print(etree.QName(child.tag).localname)
                if etree.QName(child.tag).localname is 't':
                    if child.text is not None:
                        # new_list_object = List_object()
                        new_list_object = List_object()
                        new_list_object.footnote = False
                        if child.get('{http://www.w3.org/XML/1998/namespace}space') is not None:
                            # collected_text_list.append(' ' + child.text)
                            new_list_object.text = ' ' + child.text
                            # print(child.text, end='')
                        else:
                            # print(' ' + child.text, end='')
                            # collected_text_list.append(child.text)
                            new_list_object.text = child.text
                        document_content.append(new_list_object)

                else:
                    if child.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id') is not None:
                        # current_id = str(child.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id'))
                        new_list_object = List_object()
                        # get_footnote_information(current_id, new_list_object)
                        new_list_object.footnote = True
                        new_list_object.id = str(child.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id'))
                        # print(colored(str(child.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')), 'red'),  end='')
                        new_list_object.footnote_information = get_footnote_information(new_list_object.id)
                        document_content.append(new_list_object)
                # print(child.keys())
        new_list_object = List_object()
        new_list_object.text = '\n'
        document_content.append(new_list_object)

    output_file = open("output.tex", 'w')
    for entry in document_content:
        if entry.footnote is True:
            # print(entry.footnote_information, end='')
            output_file.write(str(create_citation_command_from_footnote_list(entry.footnote_information)))
        else:
            output_file.write(str(entry))
            # print(entry, end='')

    output_file.close()


if __name__ == '__main__':
    # load_local_zotero_cache()
    main()

    # footnote_list = [{'uri': 'http://zotero.org/users/3766391/items/TJI56T4I'}, {'uri': 'http://zotero.org/users/3766391/items/VFGZ5EZI', 'prefix': "on the reception of Mitchell's 1913 book, see", 'locator': '174'}, {'uri': 'http://zotero.org/users/3766391/items/DIJH9IB2', 'locator': '47'}]
    # print(create_autocite_from_footnote_list(footnote_list))

    # print(call_zotero_api("https://www.zotero.org/le_ticia/items/43YYHYDG"))
