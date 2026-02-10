import language_tool_python
import pandas as pd
import re

import sys

lang = sys.argv[1]
infile = sys.argv[2]

tool = language_tool_python.LanguageTool(lang)
df = pd.read_csv(infile, sep="\t")

# Drop rows that do not have any misspellings
df = df[df['initial_word'].notna()]

sent_dict = df.to_dict(orient="index")

for k,v in sent_dict.items():
    
    sentence = v["Sentence"]
    orig = v["initial_word"]
    start_index = v["start_index"]
    end_index = v["end_index"]
    our_corrections = v["our_correction"]
    target = v["gold_correction"]
    ours_correct = v["ours_is_correct"]
    
    sent_dict[k]["languagetool_corrections"] = []
    
    matches = tool.check(sentence)
    correction_found = False
    
    for m in matches:
        if m.offset == start_index and m.matchedText == orig:
            
            if len(m.replacements) > 0:
                
                
                if correction_found and m.replacements[0] != correction_found[0]:
                    print("Attention! Two different matches for same word!")
                    print(m.matchedText, m.replacements[0], m.ruleId, "vs.", correction_found)
                    print(sentence)
                
                sent_dict[k]["languagetool_corrections"] = m.replacements
                correction_found = (m.replacements[0], m.ruleId)
                #print("orig:", orig, "target:", target, "languagetool:", m.replacements[0], m.offset, sentence)
        
number_of_sentences = len(sent_dict)

lt_correct = {k:v for k,v in sent_dict.items() if len(v["languagetool_corrections"]) > 0 and v["gold_correction"] == v["languagetool_corrections"][0]}
lt_incorrect = {k:v for k,v in sent_dict.items() if len(v["languagetool_corrections"]) == 0 or v["gold_correction"] != v["languagetool_corrections"][0] }


##### print languagetool result 
outfile = re.sub("\.tsv", "_LT_correction.tsv", infile)

lt_df = pd.DataFrame.from_dict(sent_dict, orient="index")
lt_df.to_csv(outfile, sep="\t")

##### print languagetool stats
outfile_stats = re.sub("/", "/correction_stats_", outfile)
outfile_stats = re.sub("tsv", "txt", outfile_stats)

lt_correct_our_correct = len([v for k,v in lt_correct.items() if v["ours_is_correct"] == "y"])
lt_correct_our_incorrect = len([v for k,v in lt_correct.items() if v["ours_is_correct"] == "n"])
lt_incorrect_our_correct = len([v for k,v in lt_incorrect.items() if v["ours_is_correct"] == "y"])
lt_incorrect_our_incorrect = len([v for k,v in lt_incorrect.items() if v["ours_is_correct"] == "n"])


with open(outfile_stats, mode="w", encoding="utf-8") as o:
    print("Languagetool gets right:", len(lt_correct), file=o)
    print("Out of:", number_of_sentences, file=o)
    print("Accuracy:", round(len(lt_correct)/number_of_sentences,3), file=o)
    print(file=o)
    print("LT correct + ours correct:", lt_correct_our_correct, file=o)
    print("LT correct + ours incorrect:", lt_correct_our_incorrect, file=o)
    print("LT incorrect + ours correct:", lt_incorrect_our_correct, file=o)
    print("LT incorrect + ours incorrect:", lt_incorrect_our_incorrect, file=o)
    print(file=o)
    
    print("############ Correct by Languagetool, correct by us ##########", file=o)
    for k,v in lt_correct.items():
        if v["ours_is_correct"] == "y":
            if len(v["languagetool_corrections"]) > 0:
                lt_correction = v["languagetool_corrections"][0]
            else:
                lt_correction = ""
            print("orig:", v["initial_word"], "\t", "correct:", lt_correction, "ours:", v["our_correction"], file=o)
    
    print(file=o)
    print("############ Correct by Languagetool, incorrect by us ##########", file=o)
    for k,v in lt_correct.items():
        if v["ours_is_correct"] == "n":
            if len(v["languagetool_corrections"]) > 0:
                lt_correction = v["languagetool_corrections"][0]
            else:
                lt_correction = ""
            print("orig:", v["initial_word"], "\t", "correct:", lt_correction, "ours:", v["our_correction"], file=o)
    
    print(file=o)
    print("############ Inorrect by Languagetool, correct by us##########", file=o)
    for k,v in lt_incorrect.items():
        if v["ours_is_correct"] == "y":
            if len(v["languagetool_corrections"]) > 0:
                lt_correction = v["languagetool_corrections"][0]
            else:
                lt_correction = ""
            print("orig:", v["initial_word"], "\t",
                  "languagetool:", lt_correction, "\t",
                  "correct:", v["gold_correction"],
                  "ours:", v["our_correction"],file=o)
        
    print(file=o)
    print("############ Inorrect by Languagetool, incorrect by us ##########", file=o)
    for k,v in lt_incorrect.items():
        if v["ours_is_correct"] == "n":
            if len(v["languagetool_corrections"]) > 0:
                lt_correction = v["languagetool_corrections"][0]
            else:
                lt_correction = ""
            print("orig:", v["initial_word"], "\t",
                  "languagetool:", lt_correction, "\t",
                  "correct:", v["gold_correction"],
                  "ours:", v["our_correction"],file=o)
