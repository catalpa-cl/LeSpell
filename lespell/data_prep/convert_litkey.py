"""
Transform the Litkey Corpus (XML) into the spelling-XML-file format
If orig and target differ, it is tagged as e.g. <error correct="Fenster" type="ins_V">Fnster</error>
Targets with comments "unclear/onom" or "ungram" are tagged as <grammar_error> and no correction is given; if there are further
errors in the word, these are ignored (e.g. split errors as in fällterunter, which is annotated as <grammar_error type="ungram">fällterunter</grammar_error> (see file 09-208)

Tokens with merge-errors each get their own error tag but the target token is the same for all parts, e.g.
<error correct="mitnehmen" type="merge_left">mit</error> <error correct="mitnehmen" type="merge_right">nehmen</error>
"""

import xml.etree.ElementTree as ET
import re
import os

corpus_path = "raw_corpora/litkey-xml/"

#root element for our spelling-XML with corpus name as attribute
corpus = ET.Element("corpus")
corpus.set("name", "Litkey")

for file in sorted(os.listdir(corpus_path)):
    #if not file.startswith("01-338"):  continue #check single file (01-140)
    tree = ET.parse(corpus_path+"/"+file)
    root = tree.getroot()

    # initialize collection of correct tokens at the beginning of a text
    # create sub element for each text with text ID as attribute
    text = ET.SubElement(corpus, "text")
    text.set("id", re.sub("\.xml", "", file))
    text.set("lang", "de")
    text.text = None

    # collects all XML elements that contain our spelling error markups
    errorlist = []

    index = 0

    while index < len(root.findall("token")):
        token = root.findall("token")[index]
        orig = token.get("orig")
        target = token.get("target")

        #orig = re.sub("_", " ", orig)  # replace merge marker with space

        if orig != target or token.get("target_comments")  in ["unclear/onom", "ungram"]:


            if orig.endswith("|"):

                orig_list = []
                target_list = []
                split_error_list = []

                orig_list.append(re.sub("\|", "", orig))
                target_list.append(target)
                split_error_list.extend([err.get("cat_fine") for errors in token.findall("errors") for err in errors.findall("err")])

                index2 = index+1
                while root.findall("token")[index2].get("orig").endswith("|"):
                    current_token = root.findall("token")[index2]
                    orig_list.append(re.sub("\|", "", current_token.get("orig")))
                    target_list.append(current_token.get("target"))
                    split_error_list.extend([err.get("cat_fine") for errors in current_token.findall("errors") for err in
                                errors.findall("err")])
                    index2 += 1

                current_token = root.findall("token")[index2]
                orig_list.append(re.sub("\|", "", current_token.get("orig")))
                target_list.append(current_token.get("target"))
                split_error_list.extend([err.get("cat_fine") for errors in current_token.findall("errors") for err in
                                         errors.findall("err")])
                index2 += 1


                #get instances of merge
                full_orig = "".join(orig_list)
                merge_list = full_orig.split("_")
                if len(merge_list) > 1:

                    for i in range(len(merge_list)):
                        part = merge_list[i]

                        merge_type = "merge_middle"
                        if i == 0:
                            merge_type = "merge_left"
                        elif i == len(merge_list) - 1:
                            merge_type = "merge_right"

                        if token.get("target_comments") in ["unclear/onom", "ungram"]:
                            error = ET.Element("grammar_error")
                            error.set("type", token.get("target_comments")+","+merge_type)
                        else:
                            error = ET.Element("error")
                            error.set("correct", " ".join(target_list))
                            err_cats = re.sub("merge", merge_type, ",".join(split_error_list))
                            error.set("type", err_cats)
                        error.text = part
                        error.tail = " "

                        errorlist.append(error)
                    index = index2

                else:
                    if token.get("target_comments") in ["unclear/onom", "ungram"]:
                        error = ET.Element("grammar_error")
                        error.set("type", token.get("target_comments"))
                    else:
                        error = ET.Element("error")
                        error.set("correct", " ".join(target_list))
                        error.set("type", ",".join(split_error_list))

                    error.text = full_orig
                    error.tail = " "


                    errorlist.append(error)
                    index = index2

            else:

                merge_list = orig.split("_")
                for i in range(len(merge_list)):
                    part = merge_list[i]

                    merge_type = ""
                    if len(merge_list) > 1:
                        merge_type = "merge_middle"
                        if i == 0:
                            merge_type = "merge_left"
                        elif i == len(merge_list) - 1:
                            merge_type = "merge_right"

                    if token.get("target_comments") in ["unclear/onom", "ungram"]:
                        error = ET.Element("grammar_error")
                        error.set("type", token.get("target_comments")+","+merge_type)

                    else:
                        error = ET.Element("error")
                        error.set("correct", target)
                        err_cats = [err.get("cat_fine") for errors in token.findall("errors") for err in
                                    errors.findall("err")]
                        err_cats = re.sub("merge", merge_type, ",".join(err_cats))
                        error.set("type", err_cats)


                    error.text = part
                    error.tail = " "


                    errorlist.append(error)
                index += 1


        else:
            if len(errorlist) == 0 and text.text != None:
                text.text += orig + " "
            elif len(errorlist) == 0 and text.text == None:
                text.text = orig + " "
            else:
                if errorlist[-1].tail != None:
                    errorlist[-1].tail += orig + " "
                else:
                    errorlist[-1].tail = orig + " "
            index += 1

    for elem in errorlist:
        text.append(elem)

corpus_tree = ET.ElementTree(corpus)
corpus_tree.write("processed_corpora/litkey_spelling.xml", encoding="unicode")



