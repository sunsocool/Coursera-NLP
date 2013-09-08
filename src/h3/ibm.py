'''
Created on 2013-4-16

@author: purlin
'''


en_words, es_words = dict(), dict()
en_data, es_data = list(), list()
en_dict, es_dict = dict(), dict()


def ibm2_em(max_epoch, num_records, t_fe):
    
    q_jilm = dict()
    for k in xrange(num_records):
        l = len(en_data[k])
        m = len(es_data[k])
        for i in xrange(m):
            for j in xrange(l):
                q_jilm[str(j)+' '+str(i)+' '+str(l)+' '+str(m)] = 1.0/l
    
    # EM
    for it in xrange(max_epoch):
        c_ef, c_e = dict(), dict()
        c_jilm, c_ilm = dict(), dict()
        print 'Iteration: ' + str(it)
        
        #E-step
        for k in xrange(num_records):
            #print 'E-step: ' + str(k)
            en_items = en_data[k]; #en_items.append('NULL')
            es_items = es_data[k]
            l = len(en_items)
            m = len(es_items)
            cnt_dict = dict()
            for i in xrange(m):
                es = es_items[i]
                for j in xrange(l):
                    en = en_items[j]
                    cnt_dict[es] = cnt_dict.get(es, 0.0) + t_fe.get(en).get(es) * q_jilm.get(str(j)+' '+str(i)+' '+str(l)+' '+str(m))
            for j in xrange(l):
                en = en_items[j]
                line_dict = t_fe.get(en)
                for i in xrange(m):
                    es = es_items[i]
                    k1 = str(j)+' '+str(i)+' '+str(l)+' '+str(m)
                    k2 = str(i)+' '+str(l)+' '+str(m)
                    theta_ij = line_dict.get(es)*q_jilm.get(k1)/cnt_dict.get(es)
                    c_ef[en+'\t'+es] = c_ef.get(en+'\t'+es, 0.0) + theta_ij
                    c_e[en] = c_e.get(en, 0.0) + theta_ij
                    c_jilm[k1] = c_jilm.get(k1, 0.0) + theta_ij
                    c_ilm[k2] = c_ilm.get(k2, 0.0) + theta_ij
        
        #M-step
        for en, w_list in en_dict.items():
            line_dict = dict()
            for es in w_list:
                line_dict[es] = c_ef.get(en+'\t'+es)/c_e.get(en)
            t_fe[en] = line_dict 
        for k, v in c_jilm.items():
            j, i, l, m = k.split()
            if c_ilm.get(i+' '+l+' '+m)<=0.0:
                q_jilm[k] = 0.0
            else:
                q_jilm[k] = v/c_ilm.get(i+' '+l+' '+m)
    
    return t_fe, q_jilm 

def ibm2_translate(en_file_name, es_file_name, pre_file_name, t_fe, q_jilm):  
    
    pt = 1
    en_file = open(en_file_name)
    es_file = open(es_file_name)
    pre_file = open(pre_file_name,'w')
    for en_line in en_file:
        en_items = en_line.strip().split()
        es_items = es_file.readline().strip().split()
        l = len(en_items)
        m = len(es_items)
        for j in xrange(l):
            en = en_items[j]
            kv_list = dict()
            for i in xrange(m):
                es = es_items[i]
                v = t_fe.get(en).get(es)*q_jilm.get(str(j)+' '+str(i)+' '+str(l)+' '+str(m))
                kv_list[i] = v
            kv_list = sorted(kv_list.items(), key=lambda d:d[1], reverse=True)
            pre_file.write(str(pt) + ' ' + str(j+1) + ' ' + str(kv_list[0][0]+1) + '\n')
        pt += 1
    pre_file.close()
    en_file.close()
    es_file.close()     

def ibm1_em(max_epoch, num_records):
    
    # ientializing
    t_fe = dict()
    for en, w_list in en_dict.items():
        line_dict = dict()
        for es in w_list:
            line_dict[es] = 1.0/len(w_list)
        t_fe[en] = line_dict
    
    # EM
    for it in xrange(max_epoch):
        c_ef, c_e = dict(), dict()
        
        #E-step
        for k in xrange(num_records):
            en_items = en_data[k]#; en_items.append('NULL')
            es_items = es_data[k]
            cnt_dict = dict()
            for es in es_items:
                for en in en_items:
                    cnt_dict[es] = cnt_dict.get(es, 0.0) + t_fe.get(en).get(es)
            for en in en_items:
                for es in es_items:
                    theta_ij = t_fe.get(en).get(es)/cnt_dict.get(es)
                    c_ef[en+'\t'+es] = c_ef.get(en+'\t'+es, 0.0) + theta_ij
                    c_e[en] = c_e.get(en, 0.0) + theta_ij
        
        #M-step
        for en, w_list in en_dict.items():
            line_dict = t_fe.get(en)
            for es in w_list:
                line_dict[es] = c_ef.get(en+'\t'+es)/c_e.get(en)
            t_fe[en] = line_dict 
            
    return t_fe

def ibm1_translate(en_file_name, es_file_name, pre_file_name, t_fe):  
    
    pt = 1
    en_file = open(en_file_name)
    es_file = open(es_file_name)
    pre_file = open(pre_file_name,'w')
    for en_line in en_file:
        en_items = en_line.strip().split()
        es_items = es_file.readline().strip().split()
        cnt = 1
        for en in en_items:
            kv_list = dict()
            ent = 1
            for es in es_items:
                v = t_fe.get(en).get(es)
                kv_list[ent] = v
                ent += 1
            kv_list = sorted(kv_list.items(), key=lambda d:d[1], reverse=True)
            pre_file.write(str(pt) + ' ' + str(cnt) + ' ' + str(kv_list[0][0]) + '\n')
            cnt += 1
        pt += 1
    pre_file.close()
    en_file.close()
    es_file.close()     
        
def read_data(en_file_name, es_file_name):   
    num_records = 0
    # read data from files 
    en_file = open(en_file_name)
    es_file = open(es_file_name)
    for line in en_file:
        en_data.append(line.strip().split())
        num_records += 1
    for line in es_file:
        es_data.append(line.strip().split())
    en_file.close()
    es_file.close()
    
    # fill data structures
    for i in xrange(num_records):
        en_items = en_data[i]
        es_items = es_data[i]
        for en in en_items:
            en_words[en] = en_words.get(en, 0) + 1
        for es in es_items:
            es_words[es] = es_words.get(es, 0) + 1
        for en in en_items:
            for es in es_items:
                en_list = en_dict.get(en, dict())
                en_list[es] = True
                es_list = es_dict.get(es, dict())
                es_list[en] = True
                en_dict[en] = en_list
                es_dict[es] = es_list
    
        #null_list = en_dict.get('NULL', dict())
        #for es in es_items:
        #    null_list[es] = True
        #en_dict['NULL'] = null_list
                
    return num_records

def ibm2(en_file_name, es_file_name, model_file_name, tef_file_name, q_file_name, en_test_name, es_test_name, pre_file_name):
    num_records = read_data(en_file_name, es_file_name)
    t_fe = dict()
    model_file = open(model_file_name)
    for line in model_file:
        items = line.split()
        v = float(items[2])
        line_dict = t_fe.get(items[0], dict())
        line_dict[items[1]] = v
        t_fe[items[0]] = line_dict
    model_file.close()
    t_fe, q_jilm = ibm2_em(5, num_records, t_fe)
    
    tef_file = open(tef_file_name,'w')
    for k1, v1 in t_fe.items():
        for k2, v2 in v1.items():
            tef_file.write(k1+'\t'+k2+'\t'+str(v2)+'\n')
    tef_file.close()
    q_file = open(q_file_name,'w')
    for k, v in q_jilm.items():
        q_file.write(k+'\t'+str(v)+'\n')
    q_file.close()
    
    ibm2_translate(en_test_name, es_test_name, pre_file_name, t_fe, q_jilm)
    
      
def ibm1(en_file_name, es_file_name, model_file_name, en_test_name, es_test_name, pre_file_name):
    num_records = read_data(en_file_name, es_file_name)
    t_fe = ibm1_em(5, num_records)
    model_file = open(model_file_name,'w')
    for k1, v1 in t_fe.items():
        for k2, v2 in v1.items():
            model_file.write(k1+'\t'+k2+'\t'+str(v2)+'\n')
    model_file.close()
    ibm1_translate(en_test_name, es_test_name, pre_file_name, t_fe)
    
en_file_name = 'D:/SkyDrive/Course/Natural Language Processing/HW/h3-p/corpus.en'
es_file_name = 'D:/SkyDrive/Course/Natural Language Processing/HW/h3-p/corpus.es'
en_test_name = 'D:/SkyDrive/Course/Natural Language Processing/HW/h3-p/test.en'
es_test_name = 'D:/SkyDrive/Course/Natural Language Processing/HW/h3-p/test.es'
model_file_name = 'D:/SkyDrive/Course/Natural Language Processing/HW/h3-p/model.ibm1'
tef_file_name = 'D:/SkyDrive/Course/Natural Language Processing/HW/h3-p/model.ibm2.t'
q_file_name = 'D:/SkyDrive/Course/Natural Language Processing/HW/h3-p/model.ibm2.q'
pre_file_name = 'D:/SkyDrive/Course/Natural Language Processing/HW/h3-p/alignment test.p2.out'

#ibm1(en_file_name, es_file_name, model_file_name, en_test_name, es_test_name, pre_file_name)
ibm2(en_file_name, es_file_name, model_file_name, tef_file_name, q_file_name, en_test_name, es_test_name, pre_file_name)