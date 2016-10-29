from bs4 import BeautifulSoup as bs
import urllib2
import csv

writers = {'QB':None,'WR':None,'RB':None,'TE':None,'PK':None,'Def':None}
fieldnames = ['week', 'year', 'GID', 'name', 'pos', 'team', 'h/a', 'oppt', 'fd points', 'fd salary']

POS_INDEX = 4
NAME_INDEX = 3

for pos in writers.keys():
    outfile = open ('roto_'+pos+'.csv','wb')
    outfile.write(';'.join(fieldnames))
    outfile.write('\n')
    outfile.truncate()
    writers[pos] = outfile
    


with open('rotoguru.csv','rb') as infile:
    infile.next()
    rotoreader = csv.reader(infile, delimiter=';', quotechar='"')
    for line in rotoreader:
        if len(line) <= 1:
            continue
        if line[0].find('<pre>') != -1:
            continue
        pos = line[POS_INDEX]
        name = line[NAME_INDEX]
        gap = name.find(',')
        fixed_name = name[gap+2:] + ' ' + name[:gap]
        line[NAME_INDEX] = fixed_name

        line_write = ';'.join(line)
        writers[pos].write(line_write+'\n')
