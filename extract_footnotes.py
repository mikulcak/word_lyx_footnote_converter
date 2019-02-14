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

root = tree.getroot()

for child in root[0]:
	# print(child.tag)
	for child in child:
		# print('\t' + child.tag)
		# print(colored(child.get('t'), 'green'))
		# print(child.tag)
		current_localname =  etree.QName(child.tag).localname
		# print(current_localname)
		for child in child:
			# print(etree.QName(child.tag).localname)
			if etree.QName(child.tag).localname is 't':
				print(child.text, end=' ')
			else:
				if child.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id') is not None:
					print(colored(str(child.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')), 'red'),  end='')
			# print(child.keys())

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