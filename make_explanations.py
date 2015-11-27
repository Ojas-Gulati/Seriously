#!/usr/bin/env python

def make_explanations():
    lines = []
    with open('commands.txt','rb') as f:
        for line in f:
            lines.append(line)
    i=0
    while not lines[i][0].isdigit():
        i+=1
    ex = "var explanations = {\n%s\n};"
    exps = []
    for line in lines[i:]:
        toks = line.split(':')
        val,desc = toks[0],':'.join(toks[1:])
        val = val[:val.index(' ')]
        desc = repr(desc.strip())
        exps.append('"%s":%s'%(val,desc))
    with open('static/explanations.js','wb') as f:
        f.write(ex%(',\n'.join(exps)))
        
if __name__ == '__main__':
    make_explanations()