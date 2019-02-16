import sys
from lxml import etree

from termcolor import colored


if len(sys.argv) < 2:
	sys.exit()

# print(sys.argv)

footnote_xml = sys.argv[1]

# mylist = []

tree = etree.parse(footnote_xml)

# for element in tree.iter():
	# print(element.tag)

# print(tree.getroot())

def get_footnote_information(id, current_list_object):
	current_list_object.footnote = True
	current_list_object.footnote_id = id
	current_list_object.citation_key = "999999999"
	current_list_object.pre_text = ""
	current_list_object.post_text = ""

class List_object:
	footnote = False
	
	def __str__(self):
		# print("I am a list object")
		if self.footnote:
			# return ("I am a footnote.")
			return self.id
		else:
			# return ("I am text.")
			return self.text

root = tree.getroot()

collected_text_list = []
document_content = []

for child in root[0]:
	# print(child.tag)
	for child in child:
		# print(child.tag)
		# print('\t' + child.tag)
		# print(colored(child.get('t'), 'green'))
		# print(child.tag)
		current_localname =  etree.QName(child.tag).localname
		# print(current_localname)
		for child in child:
			# print(etree.QName(child.tag).localname)
			if etree.QName(child.tag).localname is 't':
				if child.text is not None:
					# new_list_object = List_object()
					new_list_object = List_object()
					new_list_object.footnote = False
					if child.get('{http://www.w3.org/XML/1998/namespace}space') is not None:
					# print(child.keys())
						collected_text_list.append(' ' + child.text)
						new_list_object.text = ' ' + child.text
						# print(child.text, end='')
					else:
						# print(' ' + child.text, end='')
						collected_text_list.append(child.text)
						new_list_object.text = child.text
					document_content.append(new_list_object)

			else:
				if child.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id') is not None:
					new_list_object = List_object()
					new_list_object.footnote = True
					new_list_object.id = str(child.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id'))
					print(colored(str(child.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')), 'red'),  end='')
					document_content.append(new_list_object)
			# print(child.keys())
	new_list_object = List_object()
	new_list_object.text = '\n'
	document_content.append(new_list_object)
	# collected_text_list.append('\n')

# collected_text = [y for x in collected_text_list for y in x]

collected_text = ""
for entry in collected_text_list:
	collected_text = collected_text + entry

for entry in document_content:
	print(entry, end='')

# collected_text = lambda l: [item for sublist in collected_text_list for item in sublist]



# print(collected_text)

# collected_text = 

# for element in root.findall("r"):
	# print(element)

# for element in root.iter():
# 	# if element.tag is '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}footnoteReference':
# 		# print(colored("hallo", 'red'))
# 	# print(current_localname)

# 	# if current_localname is 'w:footnoteReference':
# 		# print(etree.tostring(element))
# 	print(element.tag)
# 	current_localname =  etree.QName(element.tag).localname
# 	if current_localname is 'p':
# 		print(colored("p", 'red'))
# 	if current_localname is 't':
# 		print(colored("t", 'red'))
# 	if current_localname is 'rFonts':
# 		print(colored("rFonts", 'red'))
# 	if current_localname is "footnoteReference":
# 		print(colored("footnoteReference", 'red'))


# for element in tree.iter():
# 	# print(element.tag.localname)
# 	# print(etree.QName(element.tag).localname)
# 	current_localname =  etree.QName(element.tag).localname
# 	print(colored(current_localname, 'red'))
# 	if current_localname is 'p':
# 		# print(element)
# 		# print(etree.tostring(element))
# 		for child in element:
# 			# print(child)
# 			current_localname =  etree.QName(child.tag).localname
# 			# print(current_localname)
# 			if current_localname is 'r':
# 				# print(etree.tostring(child))
# 				# print(etree.tostring(child))
# 				for child in child:
# 					current_localname = etree.QName(child.tag).localname
# 					# mylist.append(current_localname)
# 					# print(current_localname)
# 					# if current_localname is 't':
# 						# print(current_localname)
# 						# print(etree.tostring(child))
# 					# print(etree.tostring(child))
# 					# print(current_localname_child)
# 					if current_localname is 't':
# 						if child.text is not None:
# 							print('\t' + colored(child.text, 'green'))
# 	if current_localname is 'footnoteReference':
# 		print(etree.tostring(element))
# 			# for child in child:
# 				# print(child)
# 						# current_localname = etree.QName(child.tag).localname
# 						# print(child.keys())
# 						# print(child.get('id'))
# 						# print(etree.tostring(child))
# 						# if child.text is not None:
# 							# print(child.text)

# # print(mylist)