
ori_file = open('gene.test')
test_file = open('gene.test.key','w')

for line in ori_file:
    a = line.strip()
    if a!='':
        test_file.write(a+' O\n')
    else: test_file.write(line)

ori_file.close()
test_file.close()
