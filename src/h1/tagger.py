import sys, re

counts_file_name = sys.argv[1]
dev_file_name = sys.argv[2]
out_file_name = sys.argv[3]

pair_dict = dict()
unigram_dict = dict()
bigram_dict = dict()
trigram_dict = dict()
condition_dict = dict()

def cal_statistics():
    counts_file = open(counts_file_name)
    for line in counts_file:
        items = line.strip().split()
        cnt = float(items[0])
        if items[1]=='WORDTAG':
            tag = items[2]
            word = items[3]
            pair_list = pair_dict.get(word,[])
            pair_list.append([tag,cnt])
            pair_dict[word] = pair_list
        if items[1]=='1-GRAM':
            tag = items[2]
            unigram_dict[tag] = cnt
        if items[1]=='2-GRAM':
            tag = items[2] + ' ' + items[3]
            bigram_dict[tag] = cnt
        if items[1]=='3-GRAM':
            tag = items[2] + ' ' + items[3] + ' ' + items[4]
            trigram_dict[tag] = cnt
    counts_file.close()

def cal_conditional_prob():
    for (k,v_list) in pair_dict.items():
        word = k; pair_list = list()
        for v in v_list:
            tag = v[0]
            cnt = float(v[1])
            cnt_tag = float(unigram_dict.get(tag))
            ratio = cnt/cnt_tag
            pair_list.append([tag,ratio])
        pair_dict[word] = pair_list
    pair_dict['#'] = [['*',1.0]]
    pair_dict['STOP'] = [['STOP',1.0]]
    #print pair_dict.get('#')
    for (k,v) in trigram_dict.items():
        tri = k
        bi = k.split()[0] + ' ' + k.split()[1]
        pair_v = bigram_dict.get(bi)
        condition_dict[tri] = v/pair_v

def __get_alias(s):
    if pair_dict.has_key(s):
        return s
    else:
        if re.search('\d+', s): return '_NUMBER_'
        elif not re.search('[^A-Z]', s): return '_AllCap_'
        elif re.search('[A-Z]\Z', s): return '_LastCap_'
        else: return '_RARE_'
    
def viterbi():
    dev_file = open(dev_file_name)
    out_file = open(out_file_name,'w')
    current_sentence = '# # '
    default_value = pair_dict.get('_RARE_')
    for line in dev_file:
        if line.strip() == '':
            current_sentence = current_sentence + ' STOP'
            word_list = current_sentence.split()
            n = len(word_list)
            # dynamic programing
            pi = dict(); bpi = dict();
            k = '0 * *'
            pi[k]=1.0; bpi[k]='O'
            for i in xrange(2,n):
                word = __get_alias(word_list[i])
                word_1 = __get_alias(word_list[i-1])
                word_2 = __get_alias(word_list[i-2])
                word_pair_list = pair_dict.get(word, default_value)
                word_pair_list_1 = pair_dict.get(word_1, default_value)
                word_pair_list_2 = pair_dict.get(word_2, default_value)
                #print word, word_1, word_2
                for v in word_pair_list:
                    e = v[1]
                    for v1 in word_pair_list_1:
                        state_k = str(i-1)+' '+v1[0]+' '+v[0]
                        w = 'O'; score = 0.0
                        for v2 in word_pair_list_2:
                            k = str(i-2)+' '+v2[0]+' '+v1[0]
                            con_p = condition_dict.get(v2[0]+' '+v1[0]+' '+v[0])
                            current_s = pi.get(k)*con_p*e
                            if current_s>score:
                                score = current_s
                                w = v2[0]
                        pi[state_k] = score
                        bpi[state_k] = w
            # backtrap
            y = ['O']*(n-3)
            w_1 = __get_alias(word_list[n-2]); w_2 = __get_alias(word_list[n-3])
            word_pair_list_1 = pair_dict.get(w_1,pair_dict)
            word_pair_list_2 = pair_dict.get(w_2,pair_dict)
            score = -0.1
            for v1 in word_pair_list_1:
                for v2 in word_pair_list_2:
                    k = str(n-3)+' '+v2[0]+' '+v1[0]
                    #print k
                    con_p = condition_dict.get(v2[0]+' '+v1[0]+' STOP')
                    current_s = pi.get(k)*con_p
                    if current_s>score:
                        score = current_s
                        y[n-5] = v2[0]; y[n-4] = v1[0]
            for i in xrange(4,n-1):
                idx = n - i; w = __get_alias(word_list[idx])
                k = str(idx+1)+' '+y[idx-1]+' '+y[idx]
                if bpi.has_key(k):
                    y[idx-2] = bpi.get(k)
            # write
            for i in xrange(2,n-1):
                out_file.write(word_list[i]+' '+y[i-2]+'\n')
            out_file.write('\n')
            # reset    
            current_sentence = '# # '
        else: current_sentence = current_sentence + line.strip() + ' '
    dev_file.close()
    out_file.close()

def unigram_mle():
    uni_pair_dict = dict()
    for (k,v_list) in pair_dict.items():
        word = k; base_tag = ''; base_ratio = 0.0
        for v in v_list:
            tag = v[0]; ratio = v[1]
            if ratio>base_ratio:
                base_tag = tag
                base_ratio = ratio
        uni_pair_dict[word] = [base_tag,base_ratio]
    dev_file = open(dev_file_name)
    out_file = open(out_file_name,'w')
    for line in dev_file:
        word = line.strip()
        if len(word)==0:
            out_file.write('\n')
            continue
        if not word in pair_dict:
            word = '_RARE_'
        pair = uni_pair_dict.get(word)
        out_file.write(line.strip()+' '+pair[0]+'\n')
    out_file.close()
    dev_file.close()

cal_statistics()
cal_conditional_prob()
viterbi()
