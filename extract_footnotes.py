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

# \begin_inset CommandInset citation
# LatexCommand footcite
# key "mitchellLetterHenryDennison1924,AdvertisementBrookmireEconomic1912"
# pretextlist "mitchellLetterHenryDennison1924 see:   AdvertisementBrookmireEconomic1912 also look at:"
# posttextlist "mitchellLetterHenryDennison1924 25    AdvertisementBrookmireEconomic1912 2"
# literal "false"

# \end_inset


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

        # print(key_list.join(','))
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
        # f = open(latex_output_file, 'w')

        # write the string buffer to the file
        # f.write(buf.getvalue())

        # close file handle
        # f.close()

        # result = ""
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
    tree = etree.parse(os.path.join(document_temp_path, "word", "footnotes.xml"))
    # tree = etree.parse(footnote_xml)
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
    new_paragraph = False

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
    tree = etree.parse(os.path.join(document_temp_path, "word", "document.xml"))
    # tree = etree.parse(main_document_xml)

    root = tree.getroot()

    # collected_text_list = []
    document_content = []

    for child in root[0]:
        # print(child.tag)
        new_list_object = List_object()
        # new_list_object.new_paragraph = True
        new_list_object.text = "\n\n"
        document_content.append(new_list_object)
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
                        # if False:
                        if child.get('{http://www.w3.org/XML/1998/namespace}space') is not None:
                            # collected_text_list.append(' ' + child.text)
                            # new_text = child.text.lstrip(' ').rstrip(' ')
                            new_list_object.text = ' ' + child.text + ' '
                            # print(child.text, end='')
                        else:
                            # print(' ' + child.text, end='')
                            # collected_text_list.append(child.text)
                            new_list_object.text = (child.text).lstrip(' ').rstrip(' ')
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

    if output_lyx is True:
        mytemplate = Template(filename='lyx_template/lyx_template.tmpl')
        buf = io.StringIO()

        content_list = []
        content_list.append("\\begin_layout Standard\n")

        for entry in document_content:
            try:
                # doStuff(a.property)
                if entry.text == "\n\n":
                    content_list.append("\\end_layout\n")
                    content_list.append("\\begin_layout Standard\n")
            except AttributeError:
                # otherStuff()
                pass
            # content_list.a
            if entry.footnote is True:
                if FOOTNOTE_WRITING is True:
                    content_list.append(str(create_citation_command_from_footnote_list(entry.footnote_information)))
                else:
                    # content_list.append("\n\\textcolor{red}{DEBUG: Writing footnotes disabled}\n")
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

        # result = buf.getvalue()
        # print(result)
        output_file = open("output.lyx", 'w')

        # write the string buffer to the file
        output_file.write(buf.getvalue())

        # close file handle
        output_file.close()

    else:
        output_file = open("output.tex", 'w')
        for entry in document_content:
            # if entry.new_paragraph is True:
                # output_file.write("\n\n")
            if entry.footnote is True:
                # print(entry.footnote_information, end='')
                # output_file.write(str(create_citation_command_from_footnote_list(entry.footnote_information)))
                if FOOTNOTE_WRITING is True:
                    output_file.write(str(create_citation_command_from_footnote_list(entry.footnote_information)))
                else:
                    output_file.write("\n\\textcolor{red}{DEBUG: Writing footnotes disabled}\n")
            else:
                current_entry = str(entry)
    #             if output_lyx is True:
    #                 current_entry = current_entry.replace('“', """\\begin_inset Quotes eld
    # \\end_inset
    # """)
    #                 current_entry = current_entry.replace('”', """\\begin_inset Quotes erd
    # \\end_inset
    # """)
    #             else:
                current_entry = current_entry.replace("&", "\\&")
                current_entry = current_entry.replace("%", "\\%")
                current_entry = current_entry.replace("$", "\\$")

                current_entry = current_entry.replace("“", "``")
                current_entry = current_entry.replace("„", "``")
                current_entry = current_entry.replace("”", "\'\'")
                output_file.write(current_entry)
                # print(entry, end='')

        output_file.close()


if __name__ == '__main__':
    print(sys.argv[1])
    zip_ref = zipfile.ZipFile(sys.argv[1], 'r')

    document_temp_path = os.path.join(tempfile.gettempdir(), sys.argv[1] + "_unpacked")
    zip_ref.extractall(document_temp_path)
    zip_ref.close()

    # load_local_zotero_cache()
    main()

    # footnote_list = [{'uri': 'http://zotero.org/users/3766391/items/TJI56T4I'}, {'uri': 'http://zotero.org/users/3766391/items/VFGZ5EZI', 'prefix': "on the reception of Mitchell's 1913 book, see", 'locator': '174'}, {'uri': 'http://zotero.org/users/3766391/items/DIJH9IB2', 'locator': '47'}]
    # print(create_autocite_from_footnote_list(footnote_list))

    # print(call_zotero_api("https://www.zotero.org/le_ticia/items/43YYHYDG"))
