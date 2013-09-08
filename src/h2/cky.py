import json

count_name = 'parse_train.counts.out'
test_name = 'parse_test.dat'
pred_name = 'parse_test.out'

bin_map = dict(); un_map = dict(); non_map = dict(); w_map = dict()
p_xyy = dict(); p_xw = dict()

def cal_statistic():
    count_file = open(count_name)
    for line in count_file:
        items = line.strip().split()
        if items[1] == 'NONTERMINAL': non_map[items[2]] = float(items[0])
        elif items[1] == 'BINARYRULE': bin_map[items[2]+'\t'+items[3]+'\t'+items[4]] = float(items[0])
        elif items[1] == 'UNARYRULE':
            un_map[items[2]+'\t'+items[3]] = float(items[0])
            w_map[items[3]] = w_map.get(items[3],0) + int(items[0])
    count_file.close()
    for (k,v) in un_map.items():
        k_non = k.split()[0]
        p_xw[k] = v/non_map.get(k_non)
    for (k,v) in bin_map.items():
        k_non = k.split()[0]
        p_xyy[k] = v/non_map.get(k_non)

pi = dict(); bp = dict()

def __backstrap__(i, j, root, bp, sentence):
    if i == j:
        return '[\"'+root+'\", \"'+sentence[i-1]+'\"]'
    key = str(i)+'\t'+str(j)+'\t'+root
    item = bp.get(key)
    X, Y, Z, s = item.split()
    left = __backstrap__(i, int(s), Y, bp, sentence)
    right = __backstrap__(int(s)+1, j, Z, bp, sentence)
    return '[\"'+root+'\", ' + left + ', ' + right + ']'

def __rep__(w):
    if w_map.get(w,0)>=5: return w
    else: return '_RARE_'

def cky():
    test_file = open(test_name)
    pred_file = open(pred_name,'w')
    char_s = non_map.keys()
    bin_s = bin_map.keys()
    print char_s
    m = len(char_s); t = len(bin_s)
    for line in test_file:
        print line
        terms = line.strip().split()
        n = len(terms)
        # Initializing
        for i in xrange(1,n+1):
            for j in xrange(1,n+1):
                for k in xrange(m):
                    key = str(i)+'\t'+str(j)+'\t'+char_s[k]
                    pi[key] = 0.0; bp[key] = ''
        for i in xrange(1,n+1):
            w = __rep__(terms[i-1])
            for k in xrange(m):
                key = str(i)+'\t'+str(i)+'\t'+char_s[k]
                un_key = char_s[k]+'\t'+w
                pi[key] = p_xw.get(un_key,0.0)
                bp[key] = char_s[k]
                #if i==1: print un_key, pi.get(key)
        # DP
        for l in xrange(1,n):
            for i in xrange(1,n-l+1):
                j = i + l
                for k in xrange(t):
                    X, Y, Z = bin_s[k].split()
                    #print i, j, X, Y, Z
                    p = p_xyy.get(bin_s[k])
                    key = str(i)+'\t'+str(j)+'\t'+X
                    for s in xrange(i,j):
                        if not pi.has_key(str(i)+'\t'+str(s)+'\t'+Y):
                            print str(i)+'\t'+str(s)+'\t'+Y
                        if not pi.has_key(str(s+1)+'\t'+str(j)+'\t'+Z):
                            print str(s+1)+'\t'+str(j)+'\t'+Z
                        v = p * pi.get(str(i)+'\t'+str(s)+'\t'+Y) * pi.get(str(s+1)+'\t'+str(j)+'\t'+Z)
                        if v > pi.get(key): 
                            pi[key] = v; bp[key] = bin_s[k] + '\t' + str(s)
        #print bp.get('1\t'+str(n)+'\tSBARQ')
        #print pi.get('1\t1\tWHNP+PRON')
        # Backstrap
        res = __backstrap__(1,n,'SBARQ',bp,terms)
        # Save
        pred_file.write(res+'\n')
    test_file.close()
    pred_file.close()

cal_statistic()
cky()              
            
    
