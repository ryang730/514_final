## import packages
import pandas as pd
import numpy as np
import re

#create a list of file names
name_list = []
root = 'hunterData/'
sub1 = 'Hunter x Hunter - '
sub2 = '.enUS.ass'
for i in range(1,10):
    name = root+sub1+str(i).zfill(2)+sub2
    name_list.append(name)
for i in range(10,149):
    name = root+sub1+str(i)+sub2
    name_list.append(name)

#read lines in ass files into list
line_list = []
episode = []
epi_num = 1
for name in name_list:
    with open(name, encoding='utf_8_sig') as f:
        doc = ass.parse(f)
        cnt = len(doc.events)
        for i in range(cnt):
            line = doc.events[i].text
            if ' \\N' in line:
                line.replace(' \\N', '')
            if '}' in line:
                line = re.split(r"\}", line)[1]
            #print(line)
            if line!='':
                line_list.append(line)
                episode.append(epi_num)
    epi_num +=1

#some sentences are seperated into lines. consider combine them --Complete for lines starts with lower letter
## can't deal with ...,might ignore
#lines which are multiple lines are connected by" \\N", no space after
#some sentences contain special format
## {\\an8\\fad(601,580)}

remove = [0]*len(line_list)
for i in range(len(line_list)-1,-1,-1):
    line = line_list[i]

    if line[0].islower() == True:
        line_list[i-1] = line_list[i-1]+' '+line
        remove[i]=1

hunter = pd.DataFrame (episode, columns = ['Episode'])
hunter['Line'] = line_list
hunter['remove'] = remove

hunter.head()

hunter['remove'].value_counts()

hunter.drop(hunter[hunter['remove'] ==1].index, inplace = True)
hunter.drop(['remove'], axis=1, inplace = True)
hunter.reset_index(drop = True,inplace = True)
hunter.head()

hunter.to_csv('hunter_line.csv')

## Trying to identify title for each episode
#######notice it appears twice, first in the previous episode's '^Next Time: \w+', next time as a line in the episode <br/>
#######however might include additional lines between the two lines, not consecutive

# some titles are separated into two lines, e.g.'Next time:', use index to find the real title
title_list = []
for i in range(len(line_list)):
    line = line_list[i]
    line1 = line.lower()
    if 'next time:' in line1 and line1 !='next time:':
        title_list.append(line)
    elif line1 =='next time:':
        #line_new = line + ' '+line_list[i+1]
        title_list.append(line_list[i+1])

title_df = pd.DataFrame(title_list,columns=['Title'])
title_df = pd.merge(title_df,hunter,left_on='Title',right_on='Line',how='left')
title_df['Episode']+=1
title_df = title_df[['Title','Episode']]
episode_list = []

for i in range(1,149):
    episode_list.append(i)
episode_df = pd.DataFrame(episode_list,columns=['Episode'])
episode_df = pd.merge(title_df,episode_df,on='Episode'how='right')

#Episode 1 and 40's title is missing
episode_df[episode_df['Title'].isnull()].index.tolist()

#rename manually
episode_df['Title'][0] = 'Departure x And x Friends'
episode_df['Title'][39] = 'Wish x And x Promise!'

title_list = []
for title in episode_df['Title']:
    if 'next time' in title.lower():
        title = re.split(r": ", title)[1]
    title_list.append(title)

episode_df['Title']=title_list
hunter = pd.merge(episode_df,hunter,on='Episode',how='right')
hunter.to_csv('hunter_line.csv') 
