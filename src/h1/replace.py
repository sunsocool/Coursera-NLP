import sys, string, re

base_file_name = sys.argv[1]
ori_file_name = sys.argv[2]
rep_file_name = sys.argv[3]

rep_file = open(rep_file_name,'w')

cnt_dict = dict()

base_file = open(base_file_name)
for line in base_file:
    items = line.split()
    if len(items) < 2: continue
    cnt_dict[items[0]] = cnt_dict.get(items[0],0) + 1
base_file.close()

ori_file = open(ori_file_name)
for line in ori_file:
    items = line.strip().split()
    if len(items) < 1:
        rep_file.write(line)
        continue
    elif len(items) < 2:
        value = ''
    else: value = items[1]
    cnt = cnt_dict.get(items[0],0)
    if cnt<5:
        if re.search('\d+', items[0]): rep_file.write('_NUMBER_ '+value+'\n')
        elif not re.search('[^A-Z]', items[0]): rep_file.write('_AllCap_ '+value+'\n')
        elif re.search('[A-Z]\Z', items[0]): rep_file.write('_LastCap_ '+value+'\n')
        else: rep_file.write('_RARE_ '+value+'\n')
    else: rep_file.write(line)
ori_file.close()
                    
rep_file.close()
