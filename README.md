# word_plus_zotero_to_lyx_converter

This only works under very special circumstances, but it does the trick for me. Starting from a Word document which uses footnote-based citations from Zotero, this extract the footnote information, queries the Zotero API and retrieves the BibTex citation key created by [Zotero Better BibTex](https://github.com/retorquere/zotero-better-bibtex). Using this information, it outputs the raw text embedded in the Word document plus correct LaTeX cite commands containing prefixes, suffixes and, most importantly, the citation key. In addition to that, it is able to output complete, working LyX documents containing the Word document text, its paragraph structure, and the citation commands.


