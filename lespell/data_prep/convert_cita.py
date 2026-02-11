"""
Transform the CItA-Corpus into the spelling-XML-file format:
-  errors of types "20", "21", "22", "23", "24", "25" get <error> tag, all others <grammar_error>
    e.g. <M t="20" c="compiti">conpiti</M> becomes  <error correct="compiti" type="20">conpiti</error>

- if original and target annotation span the same number of (multiple) tokens, they are aligned 1:1 and not n:n.
    if there are two original tokens correpsonding to one target token, each original token gets its own error tag
    (but the target token remains the same for both))
"""

import os
import re
import xml.etree.ElementTree as ET

corpus_path = "raw_corpora/cita-corrected/"

#root element for our spelling-XML with corpus name as attribute
corpus = ET.Element("corpus")
corpus.set("name", "CItA")


for year_folder in ["I-year/", "II-year/"]:
    for file in sorted(os.listdir(corpus_path+year_folder)):
        filename = corpus_path+year_folder+file
        #print(filename)

        with open(filename, mode="r", encoding="utf-8") as f:
            originaltext = f.read()

        #replace '&' and '<<' in original text ('>' is automatically replaced by &gt; when the file is processed
        originaltext = re.sub("&", "&amp;", originaltext)
        originaltext = re.sub("<<", "&lt;&lt;", originaltext)

        #add a root element to the original data, otherwise the file cannot be parsed as XML
        originaltext = "<data>" + originaltext + "</data>"
        orig_root = ET.fromstring(originaltext)

        #print(originaltext)

        #create sub element for each text with text ID as attribute
        text = ET.SubElement(corpus, "text")
        text.set("id", re.sub(r"\.txt", "", year_folder+file))
        text.set("lang", "it")

        #add the text that appears until the first markup <M>
        text.text = orig_root.text
        if text.text is not None and not text.text.endswith(" "):
            text.text += " "

        #collects all XML elements that contain our spelling error markups
        errorlist = []

        #go through all markups in original text
        #note: the raw text following an error markup can be accessed with the "tail" attribute
        for orig_err in orig_root:
            if orig_err.tag == "M":

                #if the error is of the relevant types, create a spelling error element
                if orig_err.attrib["t"] in ["20", "21", "22", "23", "24", "25"]:
                    error = ET.Element("error")
                else:
                    error = ET.Element("grammar_error")

                #split orig tokens at " " or "'": if target has same number of tokens, align
                if orig_err.text is not None and (" " in orig_err.text or "'" in orig_err.text):
                    #print(orig_err.text, ">>", orig_err.attrib["c"], year_folder, file)
                    if " " in orig_err.text:
                        merge_orig = orig_err.text.strip().split(" ")
                        merge_target = orig_err.attrib["c"].strip().split(" ")
                    elif "'" in orig_err.text:
                        merge_orig = orig_err.text.strip().split("'")
                        merge_orig[0] += "'"
                        merge_target = orig_err.attrib["c"].strip().split("'")
                        merge_target[0] += "'"

                    for i in range(len(merge_orig)):
                        # if the error is of the relevant types, create a spelling error element
                        if orig_err.attrib["t"] in ["20", "21", "22", "23", "24", "25"]:
                            error = ET.Element("error")
                        else:
                            error = ET.Element("grammar_error")

                        error.text = merge_orig[i]

                        if len(merge_orig) == len(merge_target): #actually no merge error but multiple tokens annotated in original CItA
                            error.set("correct", merge_target[i])

                        else:
                            error.set("correct", orig_err.attrib["c"])

                        merge_type = "merge_middle"
                        if i == 0:
                            merge_type = "merge_left"
                        elif i == len(merge_orig)-1:
                            merge_type = "merge_right"
                        if len(merge_orig) == len(merge_target):
                            error.set("type", orig_err.attrib["t"])
                        else:
                            error.set("type", orig_err.attrib["t"]+","+merge_type)

                        if i == len(merge_orig)-1:
                            space_begin = ""
                            space_end = ""
                            if not orig_err.tail.startswith(" "): #make sure that there is a space before and after each error
                                space_begin = " "
                            if not orig_err.tail.endswith(" "):
                                space_end = " "
                            error.tail = space_begin+orig_err.tail+space_end
                        else:
                            error.tail = " "

                        text.append(error)

                else:

                    error.text = orig_err.text
                    error.set("correct", orig_err.attrib["c"])
                    error.set("type", orig_err.attrib["t"])

                    # make sure that there is a space before and after each error
                    space_begin = ""
                    space_end = ""
                    if not orig_err.tail.startswith(" "):
                        space_begin = " "
                    if not orig_err.tail.endswith(" "):
                        space_end = " "
                    error.tail = space_begin + orig_err.tail + space_end

                    text.append(error)

                #now obsolete because all errors are taken over (just with different markup
                ##if the error is not of the relevant types, just add the original text that the learner wrote
                #else:
                #    if len(errorlist) == 0 and text.text != None:
                #        text.text += orig_err.text + orig_err.tail #if it's the first error, add to 'root' text
                #    elif len(errorlist) == 0 and text.text == None:
                #        text.text = orig_err.text + orig_err.tail # if the text starts with this error, create 'root' text
                #    else:
                #        errorlist[-1].tail += orig_err.text + orig_err.tail #otherwise add to the 'tail' of the previous error

        #add all errors as child elements of a text
        #note that the error-free text in between two errors is in the 'tail' of an error
        #for elem in errorlist:
        #    text.append(elem)

#create an XML tree with 'corpus' as root node and write to file
tree = ET.ElementTree(corpus)
tree.write("processed_corpora/cita_spelling.xml", encoding="unicode")

