import csv
import xml.etree.ElementTree as ET

annotations_file = "raw_corpora/ETS_Corpus_of_Non-Native_Written_English/Annotations.tsv"
corpus_path_data = "raw_corpora/ETS_Corpus_of_Non-Native_Written_English/data/text/responses/original/"

with open(annotations_file, mode="r", encoding="utf-8") as f:
    content = csv.DictReader(f, delimiter="\t")
    rows = list(content)  # Convert to list for access

print(rows[:10])  # Print first 10 rows

corpus = ET.Element("corpus")
corpus.set("name", "ETS")
corpus.set("language", "English")


lastTextId = -1
textId = -1
originalText = ""
errorlist = []
lastend = -1
text = None

for row in rows:
    #print(row)
    lastTextId = textId
    textId = row['Filename']
    offset = row['OffsetSpan']
    start = int(offset.split("-")[0])
    end = int(offset.split("-")[1])
    type = row['Type']
    misspelling = row['Misspelling']
    correction = row['Correction']
    print(textId)
    if (textId == lastTextId):
        print(textId)
    else:
        # new Text, append all old errors
        if len(errorlist) != 0 and text is not None:
            lasterror = errorlist[-1]
            lasterror.tail = originalText[lastend:]
        if text is not None:
            for elem in errorlist:
                text.append(elem)
        errorlist = []
        print("new ID")
# open new file
        with open(corpus_path_data+str(textId)+'.txt', mode="r", encoding="utf-8") as f:
            originalText = f.read()
            print(originalText)
            beforeText = originalText[0:start]
            print(beforeText)
        text = ET.SubElement(corpus, "text")
        text.set("id", str(textId))
        text.text = str(beforeText)
        text.set("lang","en")
    error = ET.Element("error")
    error.set("correct", str(correction))
    error.set("type", str(type))
    error.text = str(misspelling)
    if (len(errorlist) != 0):
        lasterror = errorlist[-1]
        lasterror.tail = originalText[lastend:start]
    errorlist.append(error)
    lastend = end

if (len(errorlist) != 0):
    lasterror = errorlist[-1]
    lasterror.tail = originalText[lastend:]
for elem in errorlist:
    text.append(elem)

tree = ET.ElementTree(corpus)
corpusname = "processed_corpora/toefl_spelling.xml"
tree.write(corpusname, encoding="unicode")
