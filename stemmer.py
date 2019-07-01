import sys
import os
import argparse
import re
import json


class PorterStemmer: 
    mapping = {'p':'b','t':'d','c':'g','r':'rh','l':'ll','b':'f','m':'f'}
    unvoiced_stop = ['p','t','c']
    voiced_stop = ['b','d','g']
    dau_letters = ['ph','rh','ll','th','dd']
    
    def isCons(self, letter):
        if letter == 'a' or letter == 'e' or letter == 'i' or letter == 'o' or letter == 'u' or letter == 'y' or letter == 'w':
            return False            
        else:
            return True

    def isConsonant(self, word, i):
        letter = word[i]
        if self.isCons(letter):
            if letter == 'w':
                if(word[i-1]=='y'):
                    return False
                if(isCons(word[i-1]) and isCons(word[i+1])):
                    return False
                if(word[i-1]=='g' and word[i+1]=='y'):
                    return True
            else:
                return True
        else:
            return False

    def isVowel(self, word, i):
        return not(self.isConsonant(word, i))
    
    # S*
    def startsWith(self, stem, letter):
        if stem.startswith(letter):
            return True
        else:
            return False

    # *S
    def endsWith(self, stem, letter):
        if stem.endswith(letter):
            return True
        else:
            return False

    # *v*
    def containsVowel(self, stem):
        for i in stem:
            if not self.isCons(i):
                return True
        return False

    # *d
    def doubleCons(self, stem):
        if len(stem) >= 2:
            if self.isConsonant(stem, -1) and self.isConsonant(stem, -2):
                return True
            else:
                return False
        else:
            return False

    def getForm(self, word):
        form = []
        formStr = ''
        for i in range(len(word)):
            if self.isConsonant(word, i):
                if i != 0:
                    prev = form[-1]
                    if prev != 'C':
                        form.append('C')
                else:
                    form.append('C')
            else:
                if i != 0:
                    prev = form[-1]
                    if prev != 'V':
                        form.append('V')
                else:
                    form.append('V')
        for j in form:
            formStr += j
        return formStr

    def getM(self, word):
        form = self.getForm(word)
        m = form.count('V')
        return m

    def replace(self, orig, rem, rep):
        result = orig.rfind(rem)
        base = orig[:result]
        replaced = base + rep
        return replaced
    
    def replaceStart(self, orig, rem, rep):
        result = orig.find(rem)+len(rem)
        base = orig[result:]
        replaced = rep + base
        return replaced

    def replaceM0(self, orig, rem, rep):
        result = orig.rfind(rem)
        base = orig[:result]
        if self.getM(base) > 0:
            replaced = base + rep
            return replaced
        else:
            return orig

    def replaceM1(self, orig, rem, rep):
        result = orig.rfind(rem)
        base = orig[:result]
        if self.getM(base) > 1:
            replaced = base + rep
            return replaced
        else:
            return orig
    
    def valid_unmutated(self,unmutated):
        if(unmutated[:2] in self.dau_letters):
            if(len(unmutated) > 3):
                if(self.isVowel(unmutated,3) or unmutated[3] in ('r','l')):
                    return True
                else:
                    return False
            else:
                return True
        elif(unmutated[0] in self.unvoiced_stop and unmutated[1] in self.voiced_stop):
            return False
        elif(unmutated[0]=='g' and self.isConsonant(unmutated,1)):
            return False
        else:
            return True            
           
    
    def choose_unmutated(self, word,unmutated_candidates):
        unmutated = unmutated_candidates[0][0]
        if(len(unmutated_candidates) > 1):
            for candidate in unmutated_candidates:
               #print('Candidate: ',candidate)
               if(not self.valid_unmutated(candidate[0])):
                   continue
               elif(candidate[1]=='sm' and candidate[0].startswith('g')):
                   if(self.isVowel(word,0) or word[0]=='w' or word[0]=='y'):
                       unmutated = candidate[0]
                       break
                   else:
                       continue                     
               elif(candidate[1]=='sm' and candidate[0].startswith('b')):
                   unmutated = candidate[0]
                   continue
               elif(candidate[1]=='sm' and candidate[0].startswith('m')):
                   unmutated += '|'+candidate[0]
                   break
               else:
                   unmutated = candidate[0]
                   break       
        #print('Unmutated finally', unmutated)
        return unmutated  
           
    def step1(self, word, pos, number):
        token = word
        #print('Outside getM, ',self.getM(word))
        if(self.getM(word)>1):
            #print('Inside step 1')
            if(word.endswith('au') and pos in('e','ans','unk')):
                if(word.endswith('iau') and number=='pl' and word not in('diau','dieisiau','difiau','eisiau','oriau','weithiau')):
                    word = self.replace(word,'iau','')
                if(word.endswith('au') and number=='pl'):
                    word = self.replace(word,'au','')
            if(word.endswith('od') and number=='pl'):
                if(word.endswith('dod')):
                    word = self.replace(word,'dod','')
                if(word.endswith('od') and word not in ('bwyellod','clustod','cwympod','deincod','dyrnod','ffagod','gwirod','gwrthod','llaesod','rhagod','rhyfeddod')):
                    word = self.replace(word,'od','')
            if(word in('agored','colled','syched','bydded','casged','clywed','cwpled','fyned','gweled','cyfled','chweched','doded','dwbled','fflasged','gwasanaethferched','gwrferched','hawsed','lledred','merched','pared','poened','rhagweled','rhodded','stribed','syrffed','tabled','syched','taped','ticed','trwydded','uned')):
                word = self.replace(word,'ed','')   
            if(word in ('degfed','deuddegfed','pymthegfed','deunawfed','ugeinfed','deugeinfed','milfed','seithfed','trigeinfed','wythfed','aeddfed','canfed','unfed')):
                word = self.replace(word,'fed','')
            if(word.endswith('iaidd') and pos in('ans','unk')):
                word = self.replace(word,'iaidd','')
            if(word.endswith('ïaidd') and pos in('ans','unk')):
                word = self.replace(word,'ïaidd','i')
            if(word.endswith('aidd') and pos in('ans','unk')):
                word = self.replace(word,'aidd','')
            if(word.endswith('iach') and word not in ('afiach','iach')):
                word = self.replace(word,'iach','')
            if(word.endswith('ach') and self.getM(word)>1):
                if(pos not in('ans','e','unk')):
                    word = self.replace(word,'ach','')
                if(word.endswith('ach') and pos in('ans','unk') and word not in ('hytrach','chwaethach')):
                    word = self.replace(word,'ach','')
                if(word.endswith('ach') and pos in('e','unk') and word in ('clogyrnach','cyfeddach','cyfeillach','chwantach','crepach','crwbach','crwmach','gwyach','llinach','llosgach','simach','sinach','sothach','swbach','tolach')):
                    word = self.replace(word,'ach','')
            
            if(word.endswith('wr') and pos=='e'):
                word = self.replace(word,'wr','')
            if(word.endswith('iaeth')):
                word = self.replace(word,'iaeth','')
            if(word.endswith('aeth')):
                word = self.replace(word,'aeth','')
            if(word.endswith('ell') and number=='pl'):
                word = self.replace(word,'ell','')
            if(word.endswith('i') and pos in ('b','e')):
                if(pos=='e' and number=='pl'):
                    word = self.replace(word,'i','')
                if(pos=='b'):
                    word = self.replace(word,'i','')
            if(word.endswith('iad')):
                word = self.replace(word,'iad','')
            if(word.endswith('ad')):
                word = self.replace(word,'ad','')
            if(word.endswith('iol') and pos in('ans','unk')):
                word = self.replace(word,'iol','')
            if(word.endswith('ol') and pos in('ans','unk')):
                word = self.replace(word,'ol','')
            if(word.endswith('yn') and self.getM(word)>1):
                word = self.replace(word,'yn','')
            if(word.endswith('ion')):
                word = self.replace(word,'ion','')
            if(word.endswith('oedd')):
                word = self.replace(word,'oedd','')
            if(word.endswith('as') and pos in('e','unk')):
                word = self.replace(word,'as','')
            if(word.endswith('eg')):
                word = self.replace(word,'eg','')
            if(word.endswith('en')):
                word = self.replace(word,'en','')
            if(word.endswith('es')):
                word = self.replace(word,'es','')
            if(word.endswith('fa')):
                word = self.replace(word,'fa','')
            if(word.endswith('or')):
                word = self.replace(word,'or','')
            if(word.endswith('red')):
                word = self.replace(word,'red','')
            if(word.endswith('wraig')):
                word = self.replace(word,'wraig','')
            if(word.endswith('adur')):
                word = self.replace(word,'adur','')
            if(word.endswith('ai') and pos in('e','unk')):
                word = self.replace(word,'ai','y')
            if(word.endswith('aint')):
                word = self.replace(word,'aint','')
            if(word.endswith('awdwr')):
                word = self.replace(word,'awdwr','')
            if(word.endswith('awd')):
                word = self.replace(word,'awd','')
            if(word.endswith('cyn')):
                word = self.replace(word,'cyn','')
            if(word.endswith('der')):
                word = self.replace(word,'der','')
            if(word.endswith('did')):
                word = self.replace(word,'did','')
            if(word.endswith('ddod')):
                word = self.replace(word,'ddod','')
            if(word.endswith('dod')):
                word = self.replace(word,'dod','')
            if(word.endswith('dra')):
                word = self.replace(word,'dra','')
            if(word.endswith('dwr') and word in('cryfdwr', 'glewdwr', 'sychdwr', 'tewdwr')):
                word = self.replace(word,'dwr','')
            if(word.endswith('aedd')):
                word = self.replace(word,'aedd','')
            if(word.endswith('edd')):
                word = self.replace(word,'edd','')
            if(word.endswith('fel')):
                word = self.replace(word,'fel','')
            if(word.endswith('iant')):
                word = self.replace(word,'iant','')
            if(word.endswith('id') and pos=='ans'):
                word = self.replace(word,'id','')
            if(word.endswith('ineb')):
                word = self.replace(word,'ineb','')
            if(word.endswith('deb')):
                word = self.replace(word,'deb','')
            if(word.endswith('eb')):
                word = self.replace(word,'yn','')
            if(word.endswith('mon') and not(word.endswith('ymon') or word.endswith('umon'))):
                word = self.replace(word,'mon','')
            if(word.endswith('or') and pos=='e' and number=='sg' and not word.endswith('for')):
                word = self.replace(word,'or','')
            if(word.endswith('rwydd') and pos=='e' and number=='sg'):
                word = self.replace(word,'rwydd','')
            if(word.endswith('wch') and pos=='e' and self.getM(word)>3 and word not in('aruwch','Cnuwch', 'cuwch', 'yfuwch', 'lluwch', 'mofuwch', 'ffluwch', 'odduwch')):
                word = self.replace(word,'wch','')
            if(word.endswith('ych')):
                word = self.replace(word,'ych','')
            if(word.endswith('yd') and pos in('ans','e')):
                word = self.replace(word,'yd','')
            if(word.endswith('ydd') and pos=='e'and not word.endswith('wydd') and not(word.startswith('caer') or word.startswith('cae') or word.startswith('aber') or word.startswith('carn') or word.startswith('cefn') or word.startswith('ffridd'))):
                word = self.replace(word,'ydd','')
            if(word.endswith('aid') and pos=='ans' and not(word.endswith('rhaid') or word.endswith('raid'))):
                word = self.replace(word,'aid','')
            if(word.endswith('an')):
                word = self.replace(word,'an','')
            if(word.endswith('ig')):
                word = self.replace(word,'ig','')
            if(word.endswith('og')):
                word = self.replace(word,'og','')
            if(word.endswith('yll')):
                word = self.replace(word,'yll','')
            if(word.endswith('os') and pos in('e','unk')):
                word = self.replace(word,'os','')
            if(word.endswith('adwy')):
                word = self.replace(word,'adwy','')
            if(word.endswith('iedig') and pos in('ans','unk')):
                word = self.replace(word,'iedig','')
            if(word.endswith('edig') and pos in('ans','unk')):
                word = self.replace(word,'edig','')
            if(word.endswith('ieiddio') and pos in('b','unk')):
                word = self.replace(word,'ieiddio','')
            if(word.endswith('eiddio') and pos in('b','unk')):
                word = self.replace(word,'eiddio','')
            if(word.endswith('io') and pos in('b','unk') and self.getM(word)>2):
                word = self.replace(word,'io','')
            if(word.endswith('o') and pos in('b','unk') and self.getM(word)>2):
                word = self.replace(word,'o','')
            if(word.endswith('us') and pos in('ans','unk')):
                word = self.replace(word,'us','')
            if(word.endswith('u') and pos in('b','e','unk')):
                #print('Inside u')
                word = self.replace(word,'u','')

        return word            
                    
            
    def step2(self, word, pos):
        token = word
        for punct in ['!','.',',',';','?']:
            if(word.endswith(punct)):
                word = self.replace(word,punct[0] ,'')
        #print('M value: ',word, self.getM(word),pos)
        if(self.getM(word)>1):
            if(word.startswith('ryn') or word.startswith('rhyn') or word.startswith('cyd') or word.startswith('gwrth') or word.startswith('hunan') or word.startswith('rhag') or word.startswith('ym') or word.startswith('af') or word.startswith('di') or word.startswith('an') or word.startswith('am') or word.startswith('ad') or word.startswith('cyf') or word.startswith('tra') or word.startswith('ail')):
                if(word.startswith('ryn-') or word.startswith('rhyn-') or word.startswith('cyd-') or word.startswith('gwrth-') or word.startswith('hunan-') or word.startswith('rhag-') or word.startswith('ym-') or word.startswith('af-') or word.startswith('di-') or word.startswith('an-') or word.startswith('am-') or word.startswith('ad-') or word.startswith('cyf-') or word.startswith('tra-') or word.startswith('ail-')):
                    if(word.startswith('cyd-') and pos in ('e','b','ans','unk')):
                        word = self.replaceStart(word,'cyd-','')
                    if(word.startswith('ryn-') and pos in ('e','b','ans','unk')):
                        word = self.replaceStart(word,'ryn-','')
                    if(word.startswith('rhyn-') and pos in ('e','b','ans','unk')):
                        word = self.replaceStart(word,'rhyn-','')
                    if(word.startswith('gwrth-')):
                        word = self.replaceStart(word,'gwrth-','')
                    elif(word.startswith('hunan-')):
                        word = self.replaceStart(word,'hunan-','')
                    if(word.startswith('rhag-') and self.getM(word)>1 and pos in('e','b','ans','unk')):
                        word = self.replaceStart(word,'rhag-','')
                    if(word.startswith('af-') and not(word.startswith('aff-') and pos=='ans')):
                        word = self.replaceStart(word,'af-','')
                    if(word.startswith('di-')):
                        word = self.replaceStart(word,'di-','')
                    if(word.startswith('an-') and pos in('e','b','ans','unk') and self.getM(word)>2):
                        if(word.startswith('an-gh')):
                            word = self.replaceStart(word,'an-gh','ngh')
                        else:
                            word = self.replaceStart(word,'an-','')
                    if(word.startswith('am-')):
                        if(word.startswith('am-h')):
                            word = self.replaceStart(word,'am-h','mh')
                    if(word.startswith('ad-')):
                        word = self.replaceStart(word,'ad-','')
                    if(word.startswith('cyf-')):
                        word = self.replaceStart(word,'cyf-','')
                    if(word.startswith('tra-') and pos in('b','unk') or word in('trabluddus','trachwant','traflyncu','trachefn')):
                        word = self.replaceStart(word,'tra-','')
                    if(word.startswith('ym-')):
                        word = self.replaceStart(word,'ym-','')
                    if(word.startswith('ail-') and self.getM(word)>2):
                        word = self.replaceStart(word,'ail-','')
                else:
                    #print('Inside else')
                    if(word.startswith('cyd') and pos in ('e','b','ans','unk') and word not in('cydio','cydiad','cydiol','cydiedig')):
                        word = self.replaceStart(word,'cyd','')
                    if(word.startswith('ryn') and pos in ('e','b','ans','unk')):
                        word = self.replaceStart(word,'ryn','')
                    if(word.startswith('rhyn') and pos in ('e','b','ans','unk')):
                        word = self.replaceStart(word,'rhyn','')
                    if(word.startswith('gwrth')):
                        word = self.replaceStart(word,'gwrth','')
                    if(word.startswith('hunan')):
                        word = self.replaceStart(word,'hunan','')
                    if(word.startswith('rhag') and self.getM(word)>1 and pos in('e','b','ans','unk')):
                        word = self.replaceStart(word,'rhag','')
                    if(word.startswith('af') and not(word.startswith('aff') and pos in('ans','unk'))):
                        word = self.replaceStart(word,'af','')
                    if(word.startswith('di')):
                        word = self.replaceStart(word,'di','')
                    if(word.startswith('an') and pos in('e','b','ans','unk')):
                        if(word.startswith('angen')):
                            if(word.startswith('angen-')):
                                word = self.replaceStart(word,'angen-','')
                            else:
                                word = self.replaceStart(word,'angen','')
                        if(word.startswith('anghen')):
                            if(word.startswith('anghen-')):
                                word = self.replaceStart(word,'anghen-','')
                            else:
                                word = self.replaceStart(word,'anghen','')
                        if(word.startswith('anian')):
                            if(word.startswith('anian-')):
                                word = self.replaceStart(word,'anian-','')
                            else:
                                word = self.replaceStart(word,'anian','')
                        if(word.startswith('anif')):
                            if(word.startswith('anif-')):
                                word = self.replaceStart(word,'anif-','')
                            else:
                                word = self.replaceStart(word,'anif','')
                        if(word.startswith('anim')):
                            if(word.startswith('anim-')):
                                word = self.replaceStart(word,'anim-','')
                            else:
                                word = self.replaceStart(word,'anim','')
                        if(word.startswith('android')):
                            if(word.startswith('android-')):
                                word = self.replaceStart(word, 'android-','')
                            else:
                                word = self.replaceStart(word,'android','')
                        if(word.startswith('annog')):
                            if(word.startswith('annog-')):
                                word = self.replaceStart(word,'annog-','')
                            else:
                                word = self.replaceStart(word,'annog','')
                        if(word.startswith('angh')):
                            word = self.replaceStart(word,'angh','ngh')
                        if(word.startswith('an')):
                            word = self.replaceStart(word,'an','')
                    if(word.startswith('am') and pos in ('e','b','ans','unk')):
                        if(word.startswith('amh')):
                            word = self.replaceStart(word,'amh','mh')
                        else:
                            word = self.replaceStart(word,'am','')
                    if(word.startswith('ad')):
                        word = self.replaceStart(word,'ad','')
                    if(word.startswith('cyf')):
                        word = self.replaceStart(word,'cyf','')
                    if(word.startswith('tra') and (pos in('b','unk') or word in('trabluddus','trachwant','traflyncu','trachefn')) and word not in('trasiedi')):
                        word = self.replaceStart(word,'tra','')
                    if(word.startswith('ym') and pos in('b','e','ans','unk','adf') and word not in('ymbarél','ymbarel','ymodi','ymodol','ymodideg','ymoei')):
                        #print('Inside ym')
                        if(word.startswith('ymh')):
                            word = self.replaceStart(word,'ymh','mh')
                        else:
                            word = self.replaceStart(word,'ym','')
                    if(word.startswith('ail') and self.getM(word)>2):
                        word = self.replaceStart(word,'ail','')
                
            #print('Before mutation: ',word)
                if(word==''):
                    word = token       
                #print('Word sent ',word)
                unmutated_candidates = self.lookup_mutation(word)
                if(len(unmutated_candidates) != 0):
                    #print('Unmutated candidates ',unmutated_candidates)
                    word = self.choose_unmutated(word,unmutated_candidates)
        else:
            pass
        return word
    
    def lookup_mutation(self,input_token):
        """ Return a list of all possible Welsh mutations of a given token """
        token = input_token.lower()
        unmutated = []
        if token[:2] == "ch":
            unmutated.append(("c{}".format(token[2:]), "am"))
        if token[:2] == "ph":
            unmutated.append(("p{}".format(token[2:]), "am"))
        if token[:2] == "th":
            unmutated.append(("t{}".format(token[2:]), "am"))
        if token[:3] == "ngh":
            unmutated.append(("c{}".format(token[3:]), "nm"))
        if token[:2] == "mh":
            unmutated.append(("p{}".format(token[2:]), "nm"))
        if token[:2] == "nh":
            unmutated.append(("t{}".format(token[2:]), "nm"))
        if token[:2] == "ng":
            unmutated.append(("g{}".format(token[2:]), "nm"))
        if token[:1] == "m":
            unmutated.append(("b{}".format(token[1:]), "nm"))
        if token[:1] == "n":
            unmutated.append(("d{}".format(token[1:]), "nm"))
        if token[:2] == "rh":
            unmutated.append(("tr{}".format(token[2:]), "nm"))
        if token[:1] == "g":
            unmutated.append(("c{}".format(token[1:]), "sm"))
        if token[:1] == "b":
            unmutated.append(("p{}".format(token[1:]), "sm"))
        if token[:1] == "d":
            unmutated.append(("t{}".format(token[1:]), "sm"))
        if token[:1] == "f" and token[:2]!="ff":
            unmutated.append(("b{}".format(token[1:]), "sm"))
            unmutated.append(("m{}".format(token[1:]), "sm"))
        if token[:1] == "l":
            unmutated.append(("ll{}".format(token[1:]), "sm"))
        if token[:1] == "r":
            unmutated.append(("rh{}".format(token[1:]), "sm"))
        if token[:2] == "dd":
            unmutated.append(("d{}".format(token[2:]), "sm"))
        if input_token[0].isupper():
            capitals = []
            for mutation in unmutated:
                    capitals.append(("{}{}".format(mutation[0][:1].upper(), mutation[0][1:]), mutation[1]))
            unmutated = unmutated + capitals
        return(unmutated)

    def stem(self, word, pos, number):
        word = self.step1(word,pos,number)
        word = self.step2(word,pos)
        return word

stemmer = PorterStemmer()
command = 'python3.7 CyTag/CyTag.py > POStagged.out'
#print(sys.argv[1])
os.system(command)
obj = []
with open("POStagged.out","r") as f:
    lines = ""
    for line in f:
        #print('Line: ',line.strip())
        token = line.strip().split("\t")[1].lower()
        lemma = line.strip().split("\t")[3].lower()
        pos = line.strip().split("\t")[4].lower()
        number = 'pl' if(line.strip().split("\t")[5].lower() in ('ebll','egll')) else 'sg'
        if('|' in lemma):
            lemma = lemma.split('|')[0].strip()
        if('|' in pos):
            pos = pos.split('|')[0].strip()
        if(pos=='atd'):            
            stem_output = lemma
        else:
            stem_output = stemmer.stem(lemma,pos,number)
        # print('Token :',token,' ==> Stem: ',stem_output,'\n')
        obj.append({'token': token, 'stem': stem_output})
    print(json.dumps(obj))