import language_tool_python
import pandas as pd
import re
import  math

import sys

lang = sys.argv[1]
infile = sys.argv[2]

tool = language_tool_python.LanguageTool(lang)
df = pd.read_csv(infile, sep="\t")

sent_dict = df.to_dict(orient="index")
#print(math.isnan(sent_dict[0]["gold_correction"]))

seen_index = []

tp_list = []
fp_list = []
fn_list = []

potential_fp = {} #store index: [(offset, matchedText), ...]

for k,v in sent_dict.items():
    
    #print(k)
    index = v["SentenceID"]
    sentence = v["Sentence"]
    orig = v["initial_word"]
    start_index = v["start_index"]
    #end_index = v["end_index"]
    #our_corrections = v["our_correction"]
    target = v["gold_correction"]
    #ours_correct = v["ours_is_correct"]
    
    sent_dict[k]["languagetool_detection"] = []
    matches = tool.check(sentence)
    
    #if there is indeed an error in the sentence
    if isinstance(target, str):
        
        for m in matches:
            if m.ruleIssueType == "misspelling":
                
                if m.offset == start_index and m.matchedText == orig:
                    tp_list.append((index,m.matchedText))
                    sent_dict[k]["languagetool_detection"].append("TP")
                    
                    #remove potential fp if applicable
                    if index in potential_fp and (m.offset, m.matchedText) in potential_fp[index]:
                        potential_fp[index].remove((m.offset, m.matchedText))
                    
                else:
                    if not index in seen_index: #do not look (again) for FPs if the sentence was already seen
                        sent_dict[k]["languagetool_detection"].append("FP?")
                        if index not in potential_fp:
                            potential_fp[index]= [(m.offset, m.matchedText)]
                        else:
                            potential_fp[index].append((m.offset, m.matchedText))
                        #fp_list.append(m.matchedText)
        
        if "TP" not in sent_dict[k]["languagetool_detection"]:
            sent_dict[k]["languagetool_detection"].append("FN")
            fn_list.append((index,orig))
        
        
        
    #if there is no error in the sentence
    if not isinstance(target, str):
        for m in matches:
            if m.ruleIssueType == "misspelling":
                sent_dict[k]["languagetool_detection"].append("FP")
                fp_list.append((index,m.matchedText))
                
    seen_index.append(index)
    
        
#add all remaining potential FPs
for i,fps in potential_fp.items():
    if len(fps) > 0:
        for fp in fps:
            fp_list.append((i,fp[1])) #add sentence index and matched text only

tp = len(tp_list)
fp = len(fp_list)
fn = len(fn_list)

precision = tp/(tp+fp)
recall = tp/(tp+fn)
fscore = 2*((precision*recall)/(precision+recall))


##### print languagetool result 
outfile = re.sub("\.tsv", "_LT_detection.tsv", infile)

lt_df = pd.DataFrame.from_dict(sent_dict, orient="index")
lt_df.to_csv(outfile, sep="\t")


##### print languagetool stats
outfile_stats = re.sub("/", "/detection_stats_", outfile)
outfile_stats = re.sub("tsv", "txt", outfile_stats)


with open(outfile_stats, mode="w", encoding="utf-8") as o:
    print("TP:", tp, file=o)
    print("FP:", fp, file=o)
    print("FN:", fn, file=o)
    print("Precision:", round(precision,2), file=o)
    print("Recall:", round(recall,2), file=o)
    print("F-Score:", round(fscore,2), file=o)
    print(file=o)
    print("########## FALSE POSITIVES:", file=o)
    for word in fp_list:
        print(word, file=o)
    print(file=o)
    print("########## FALSE NEGATIVES:", file=o)
    for word in fn_list:
        print(word, file=o)

