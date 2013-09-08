import re, json

def dropchars(s1, s2):
    keeps = list(s2)
    for char in s1:
        try:
            keeps.remove(char)
        except ValueError:
            pass
    onefromtwo = len(keeps)
    keeps = list(s1)
    for char in s2:
        try:
            keeps.remove(char)
        except ValueError:
            pass
    twofromone = len(keeps)
    return min(onefromtwo, twofromone)

def getwords(wordtype):
    fp=open('/usr/share/wordnet/index.%s' % wordtype)
    idx = [l.split() for l in fp.readlines() if l.split() and not l.startswith('#')]
    fp.close()
    mat = [{"word": x[0], "offset": int(x[-1])} for x in idx 
        if re.match("^[a-z]+$", x[0]) and x[2] == "1"
        and x[0][-1] != "a" and x[0][-2:] != "ae"] # exclude words ending in a, 'cos Latin
    okwords = {}
    double_words = {}
    fp = open('/usr/share/wordnet/data.%s' % wordtype)
    for m in mat:
        defining_tuple = (wordtype, m["offset"])
        if defining_tuple in double_words:
            allok = True
            for existing in double_words[defining_tuple]:
                if dropchars(existing, m["word"]) < 4:
                    allok = False
                    break
            if allok:
                double_words[defining_tuple].append(m["word"])
        elif defining_tuple in okwords:
            if dropchars(okwords[defining_tuple], m["word"]) > 3:
                double_words[defining_tuple] = [okwords[defining_tuple], m["word"]]
        else:
            okwords[defining_tuple] = m["word"]
        fp.seek(m["offset"])
        line = fp.read(400)
        parts = line.split("|")
        word_metadata = parts[0].split()

        if len(parts) >= 2 and "\n" in parts[1]:
            defn = parts[1].split("\n")[0].strip()
            if ";" in defn:
                defn = defn.split(";")[0]
            if len(defn) < 100:
                definitions[defining_tuple] = defn
    fp.close()
    return double_words

words = {}
definitions = {}

words.update(getwords("noun"))
words.update(getwords("verb"))
words.update(getwords("adj"))
words.update(getwords("adv"))

out = []
for k in words:
    if k in definitions:
        out.append([definitions[k], words[k]]);

fp = open("defs.js", "w")
fp.write("defsload(%s)" % json.dumps(out, indent=0))
fp.close()
print "%s definitions" % len(out)
