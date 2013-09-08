
cnt_map = dict(); rare_map = dict()

cnt_file = open('cfg.counts')
for line in cnt_file:
    items = line.split()
    if len(items)==4:
        key = items[3]
        cnt = int(items[0])
        cnt_map[key] = cnt_map.get(key,0) + cnt
cnt_file.close()

for (k,v) in cnt_map.items():
    if v < 5:
        rare_map[k] = v

print rare_map

in_file = open('parse_train.dat')
out_file = open('parse_train_rep.dat','w')
for line in in_file:
    n_line = line
    for (k,v) in rare_map.items():
        n_line = n_line.replace('\"'+k+'\"', '\"_RARE_\"')
    out_file.write(n_line)
in_file.close()
out_file.close()
