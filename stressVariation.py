action = 0 # to create tsv files for manual annotation, set action to 0; to estimate variation, set action to 1

import html, re, os, pandas as pd, csv, random, statistics
from transliterate import translit
from collections import Counter
from itertools import combinations
from scipy.stats import poisson

vowels = 'аеёиоуыэюя'

# read a poem and its metadata (the poems are stored in the texts folder, and the metadata in the meta folder)

class Poem():
    def __init__ (self, poem_id):
        self.id = poem_id
        with open('meta/{}.txt'.format(poem_id), 'r', encoding='utf-8') as f:
            metadata_file = f.read()
        self.metadata = {x[0]:x[1] for x in re.findall('<td>(.*?)</td>\n<td class="value">(.*?)</td>', metadata_file)}
        with open('texts/{}.txt'.format(poem_id), 'r', encoding='utf-8') as f:
            text_file = f.read()
        text = re.search('<span class="b-wrd-expl"[\s\S]*<span class="b-wrd-expl".*?</span>.*?<br>', text_file).group()
        text = re.sub('</?span.*?>','',text)
        text = re.sub('&#768;','@',text) #replace html escape sequence &#768; (= strong position) with an @ sign
        text = re.sub(' *<br> *','\n',text) #make 
        text = re.sub('<.*?>','',text) #remove tags
        text = html.unescape(text)
        self.accented_tokens = [(x.group(0), x.start()) for x in re.finditer('[@а-я-]+', text.lower())]
        self.text = re.sub('@', chr(768), text) #make stress marks more human-readable


# convert the string with @'s after potentially stressed vowels
# into a list of numbers of potentially stressed syllables,
# starting with 1, e.g.:
# "до@мик" = "do@mik" 'small house' -> [1]
# "мо@лодо@му" = "mo@lodo@mu" 'to the young one' -> [1, 3]

def atsToStresses(w):
    syllableCount = 0
    stressed = []
    for i, c in enumerate(w):
        if c in vowels:
            syllableCount += 1
            if w[i+1:i+2] == '@':
                stressed.append(syllableCount)
    return tuple(stressed)

# make a corpus from individual poems and convert it to a Pandas dataframe
def loadCorpus():
    # load all poems from texts and meta folders
    poems = {int(x[:-4]): Poem(x[:-4]) for x in os.listdir('texts')}
    # remove all poems whose meter ('Метр') is not among the codes for accentual-syllabic meters
    for x in list(poems.keys()):
        if poems[x].metadata['Метр'] not in ['Х', 'Я', 'Д', 'Аф', 'Ан']:
            poems.pop(x)
    columnNames = ['poem_id', 'author', 'token_id', 'start_position', 'token', 'stressed']
    corpus_list = []
    for poem_id in poems:
        corpus_list.extend([[poem_id, poems[poem_id].metadata['Автор'], i, t[1], t[0], atsToStresses(t[0])] for i, t in enumerate(poems[poem_id].accented_tokens)])
    corpus_df = pd.DataFrame(corpus_list,columns=columnNames)
    corpus_df['token_no_stress'] = [re.sub('@', '', x) for x in corpus_df['token']]
    return (corpus_df, poems)

# for a given subcorpus, find all word types with stress variation,
# i.e. word types represented by tokens with incompatible stress patterns.
# For instance, if the tokens of the word type "счастливый" = "ščastlivyj" 'happy'
# are sometimes annotated as "сча@стливы@й" = "šča@stlivy@j"
# and sometimes as "счастли@вый" = "ščastli@vyj", this word type exhibits stress variation.
# However, if there are only instances of "сча@стливы@й" = "šča@stlivy@j"
# and "сча@стливы@й" = "šča@stlivyj", this is not a proof of stress variation,
# because both annotations are compatible with initial stress.
# It is assumed that a word cannot have more than two possible stresses.

def extractTypesWithVariation(corpus):
    types_with_variation = {}
    frequency_list = Counter(corpus['token_no_stress'])
    for word_type in frequency_list:
        if frequency_list[word_type] >= 2:
            possible_stress_positions = Counter(corpus[corpus['token_no_stress']==word_type].stressed.values.tolist())
            syllable_count = len(re.findall('['+vowels+']', word_type))
            impossible_stresses = {x:0 for x in range(1, syllable_count+1)}
            for i in range(1, syllable_count+1):
                for x in possible_stress_positions:
                    if x != tuple() and not i in x:
                        impossible_stresses[i] += possible_stress_positions[x]
            if not 0 in impossible_stresses.values() and syllable_count > 0:
                impossible_stresses = {x:0 for x in combinations(range(1, syllable_count+1), 2)}
                for pair in impossible_stresses:
                    for x in possible_stress_positions:
                        if x != tuple() and not pair[0] in x and not pair[1] in x:
                            impossible_stresses[pair] += possible_stress_positions[x]
                best_guess = [x for x in impossible_stresses if impossible_stresses[x] == min(impossible_stresses.values())][0]
                types_with_variation[word_type] = (best_guess, {x:set(x) & set(best_guess) for x in possible_stress_positions})
    return types_with_variation


# for each author in the sample, create a tsv file for manual annotation
# of possible cases of stress variation

def extractVariationForManualCheck():
    stats_by_author = open('author_subcorpus_sizes.txt', 'w', encoding='utf-8')
    authors = pd.unique(corpus_df['author'])
    for author in authors:
        author_subcorpus_size = len(corpus_df[corpus_df['author']==author])
        stats_by_author.write('\t'.join([author, str(author_subcorpus_size)])+'\n')
        if author_subcorpus_size < 5000:
            continue
        print(author)
        subcorpus = corpus_df[corpus_df['author']==author]
        types_with_variation = extractTypesWithVariation(subcorpus)
        if not os.path.exists('variationByAuthor'):
            os.mkdir('variationByAuthor')
        with open('variationByAuthor/{}.txt'.format(author), 'w', encoding='utf-8', newline='') as f:
            snippet_id = 1
            tsv_writer = csv.writer(f, delimiter='\t')
            for i, word in enumerate(types_with_variation):
                positions = subcorpus.index[subcorpus['token_no_stress']==word]
                for p in positions:
                    kwic_start = subcorpus.start_position[p]
                    kwic_end = subcorpus.start_position[p]+len(subcorpus.token[p])
                    row = [snippet_id,
                           i,
                           word,
                           poems[subcorpus.poem_id[p]].text[kwic_start-40:kwic_start].replace('\n',' / '),
                           poems[subcorpus.poem_id[p]].text[kwic_start:kwic_end].replace('\n',' / '),
                           poems[subcorpus.poem_id[p]].text[kwic_end:kwic_end+40].replace('\n',' / ')]
                    if types_with_variation[word][1][subcorpus.stressed[p]] == set():
                        row.extend(['', 0])
                    else:
                        row.extend([list(types_with_variation[word][1][subcorpus.stressed[p]])[0], 1])
                    tsv_writer.writerow(row)
                    snippet_id += 1
    stats_by_author.close()

# load subcorpus sizes stored in a txt file
def loadSubcorpusSizes(filename):
    subcorpus_sizes = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            name, size = line.strip().split('\t')
            subcorpus_sizes[name] = int(size)
    return subcorpus_sizes

# estimate the number of word types with variable stress observable in a sample of 10,000 tokens
def estimateVariation():
    subcorpus_sizes = loadSubcorpusSizes('author_subcorpus_sizes.txt')
    for x in os.listdir('variationByAuthor-checked'):
        author = x[:-4]
        variable_stress_tokens = {}
        with open('variationByAuthor-checked/{}'.format(x), encoding='utf-8', newline='') as f:
            tsv_reader = csv.reader(f, delimiter='\t')
            for row in tsv_reader:
                if row[-1] == '1':
                    if row[2] not in variable_stress_tokens:
                        variable_stress_tokens[row[2]] = []
                    variable_stress_tokens[row[2]].append(int(row[-2]))
        estimate = 0
        sample_size = 10000
        variable_stress_types = 0
        for word_type in variable_stress_tokens:
            variant_forms_frequencies = Counter(variable_stress_tokens[word_type])
            variant_forms = list(variant_forms_frequencies.keys())
            if len(variant_forms) == 2:
                estimate += (1-poisson.pmf(0, variant_forms_frequencies[variant_forms[0]]*sample_size/subcorpus_sizes[author])) * (1-poisson.pmf(0, variant_forms_frequencies[variant_forms[1]]*sample_size/subcorpus_sizes[author]))
                variable_stress_types += 1
        print(author, translit(author, "ru", reversed=True), subcorpus_sizes[author], variable_stress_types, round(estimate, 3), sep='\t')       

if action == 0:
    corpus_df, poems = loadCorpus()
    extractVariationForManualCheck()
elif action == 1:
    estimateVariation()
