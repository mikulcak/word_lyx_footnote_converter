import sys
import io
from lxml import etree

import os

from termcolor import colored

from mako.template import Template
from mako.runtime import Context

import re

import json

from pyzotero import zotero
from pyzotero import zotero_errors

import zipfile

import tempfile

if len(sys.argv) < 3:
    sys.exit()

output_lyx = True

FOOTNOTE_WRITING = True

zotero_library_id = sys.argv[2]
zotero_api_key = sys.argv[3]

nsmap = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}


def create_citation_command_from_footnote_list(footnote_list):
    print("Getting information for footnote with information " + str(footnote_list))
    result = "EMPTY-CITATION-FIX-ME"
    if output_lyx is True:
        print("Outputting LyX citation command")
        mytemplate = Template(filename='lyx_template/lyx_citation_command_template.tmpl')
        buf = io.StringIO()

        # create context to impose on the template in the current iteration
        key_list = []
        if footnote_list is not None:
            for entry in footnote_list:
                if 'uri' in entry.keys():
                    key_list.append(get_biblatex_cite_key_from_zotero_api(entry['uri']))

        print(','.join(key_list))

        pretext_list = []
        if footnote_list is not None:
            for entry in footnote_list:
                if 'prefix' in entry.keys():
                    pretext_list.append(get_biblatex_cite_key_from_zotero_api(entry['uri']))
                    pretext_list.append(' ')
                    pretext_list.append(entry['prefix'].replace("\"", "\\\""))
                    pretext_list.append('\t')

        posttext_list = []
        if footnote_list is not None:
            for entry in footnote_list:
                if 'locator' in entry.keys():
                    posttext_list.append(get_biblatex_cite_key_from_zotero_api(entry['uri']))
                    posttext_list.append(' ')
                    posttext_list.append(entry['locator'].replace("\"", "\\\""))
                    posttext_list.append('\t')

        ctx = Context(buf, key_list=','.join(key_list), pretext_list=''.join(pretext_list), posttext_list=''.join(posttext_list))

        # render template with context we've just generated
        mytemplate.render_context(ctx)

        result = buf.getvalue()
        print(result)
    else:
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
    return result


def parse_citation_key(extra_field):
    return re.sub(r'.*\W*(citation key:)\W*', '', extra_field, flags=re.IGNORECASE)


def get_zotero_item_key_from_uri(uri):
    return uri.split('/')[-1]


def get_biblatex_cite_key_from_zotero_api(citation_uri):

    item_key = str(get_zotero_item_key_from_uri(citation_uri))

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
    json_data = json.loads(csl_data.lstrip('ADDIN ZOTERO_ITEM CSL_CITATION'))

    result = []
    for citation_item in json_data['citationItems']:
        new_dict = {}
        new_dict['uri'] = citation_item['uri'][0]
        if 'prefix' in citation_item.keys():
            new_dict['prefix'] = citation_item['prefix']
        if 'locator' in citation_item.keys():
            new_dict['locator'] = citation_item['locator']
        result.append(new_dict)
    return result


def get_footnote_information(id):
    print(colored("Looking for citation id " + id, 'red'))
    tree = etree.parse(os.path.join(document_temp_path, "word", "footnotes.xml"))

    results = tree.xpath("//w:footnotes/w:footnote/w:p/w:r/w:instrText",
                         namespaces=nsmap)
    for footnote in results:
        if str(footnote.getparent().getparent().getparent().get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id")) == id:
            return extract_csl_data_from_footnote(footnote.text)


class List_object:
    footnote = False
    footnote_information = []
    new_paragraph = False

    def __str__(self):
        # print("I am a list object")
        if self.footnote:
            # return ("I am a footnote.")
            return colored(self.id + ": " + str(self.footnote_information), 'red')

        else:
            # return ("I am text.")
            return self.text


def main():
    tree = etree.parse(os.path.join(document_temp_path, "word", "document.xml"))

    root = tree.getroot()

    document_content = []

    for child in root[0]:
        new_list_object = List_object()
        new_list_object.text = "\n\n"
        document_content.append(new_list_object)
        for child in child:
            for child in child:
                if etree.QName(child.tag).localname is 't':
                    if child.text is not None:
                        new_list_object = List_object()
                        new_list_object.footnote = False
                        if child.get('{http://www.w3.org/XML/1998/namespace}space') is not None:
                            new_list_object.text = ' ' + child.text + ' '
                        else:
                            new_list_object.text = (child.text).lstrip(' ').rstrip(' ')
                        document_content.append(new_list_object)

                else:
                    if child.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id') is not None:
                        new_list_object = List_object()
                        new_list_object.footnote = True
                        new_list_object.id = str(child.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id'))
                        new_list_object.footnote_information = get_footnote_information(new_list_object.id)
                        document_content.append(new_list_object)
        new_list_object = List_object()
        new_list_object.text = '\n'
        document_content.append(new_list_object)

    if output_lyx is True:
        mytemplate = Template(filename='lyx_template/lyx_template.tmpl')
        buf = io.StringIO()

        content_list = []
        content_list.append("\\begin_layout Standard\n")

        for entry in document_content:
            try:
                if entry.text == "\n\n":
                    content_list.append("\\end_layout\n")
                    content_list.append("\\begin_layout Standard\n")
            except AttributeError:
                pass
            if entry.footnote is True:
                if FOOTNOTE_WRITING is True:
                    content_list.append(str(create_citation_command_from_footnote_list(entry.footnote_information)))
                else:
                    content_list.append("\n\\color red\nDEBUG: Writing footnotes disabled\n\\color inherit\n")
            else:
                current_entry = str(entry)
                current_entry = current_entry.replace('“', """\\begin_inset Quotes eld
\\end_inset
""")
                current_entry = current_entry.replace('”', """\\begin_inset Quotes erd
\\end_inset
""")
                content_list.append(current_entry)
        content_list.append("\\end_layout\n")
        ctx = Context(buf, document_content=''.join(content_list))

        # render template with context we've just generated
        mytemplate.render_context(ctx)

        output_file = open("output.lyx", 'w')

        # write the string buffer to the file
        output_file.write(buf.getvalue())

        # close file handle
        output_file.close()

    else:
        output_file = open("output.tex", 'w')
        for entry in document_content:
            if entry.footnote is True:
                if FOOTNOTE_WRITING is True:
                    output_file.write(str(create_citation_command_from_footnote_list(entry.footnote_information)))
                else:
                    output_file.write("\n\\textcolor{red}{DEBUG: Writing footnotes disabled}\n")
            else:
                current_entry = str(entry)
                current_entry = current_entry.replace("&", "\\&")
                current_entry = current_entry.replace("%", "\\%")
                current_entry = current_entry.replace("$", "\\$")

                current_entry = current_entry.replace("“", "``")
                current_entry = current_entry.replace("„", "``")
                current_entry = current_entry.replace("”", "\'\'")
                output_file.write(current_entry)

        output_file.close()


if __name__ == '__main__':
    print(sys.argv[1])
    zip_ref = zipfile.ZipFile(sys.argv[1], 'r')

    document_temp_path = os.path.join(tempfile.gettempdir(), sys.argv[1] + "_unpacked")
    zip_ref.extractall(document_temp_path)
    zip_ref.close()

    main()
