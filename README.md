# russianStressVariation-Jan2023

## Introduction
Russian stress is a notoriously complex phenomenon. Stress placement is very difficult to acquire for L2 learners, but there is also a substantial amount of variation in stress placement among L1 speakers. Russian exhibits not only inter-speaker variation (e.g., some speakers say _vésely_ 'cheerful (plural)', and some speakers say _veselý_), but also intra-speaker variation (the same speaker can sometimes say _vésely_ and sometimes _veselý_)

In Russian accentual-syllabic poetry, stresses of polysyllabic words are aligned with strong verse positions, i.e. stress of a polysyllabic word can only fall on a strong (S) but not a weak (W) position. For this reason, poetry is a valuable source of information on stress placement in Russian of the last 250 years and can be used for studying diachronic change and variation in the domain of stress placement.

For instance, from the following two lines by Nikolay Gumilev (1886–1921)

    Zveri menja dožidajutsja tam,
      S W  W  S  W W S W   W  S
    Pëstrye zveri za krepkoj rešëtkoj
     S   WW   S W  W   S  W   W S  W
    
    'The animals are waiting for me there, / Motley animals behind strong bars.'

one can infer stresses _zvéri_, _menjá_, _dožidájutsja_, _pë́strye_, _krépkoj_, _rešë́tkoj_.

However, consider the following two lines by the same author:

    Vy ž, kak vsegda, vesely na kanate
     S     W    W  S   W W S  W  W S W
    'You are as always cheerful on the rope'
    
    Kak vesely v plamennom Tibre galery!
     W   S W W     S W  W   S  W  W S W
    'How cheerful are the galleys in the fiery Tiber'

From these lines we can infer that Nikolay Gumilev had intra-speaker variation and used both _vésely_ and _veselý_.

A corpus study makes it possible to quantify the extent of intra-speaker variation for individual speakers, e.g. by computing the expected number of word types with variable stress per 10,000 tokens.

For more details, see: Piperski, A., and A. Kukhto. “Inferring Stress Placement Variability from a Poetic Corpus”. Journal of Slavic Linguistics, vol. 29, no. FASL 28 extra issue, Dec. 2021, pp. 1-15, http://ojs.ung.si/index.php/JSL/article/view/165.

## Repository contents

**/texts**: texts by four poets (Vladimir Narbut = В. И. Нарбут, Mikhail Zenkevich = М. А. Зенкевич, Nikolay Gumilev = Н. С. Гумилев, Sergey Gorodetsky = С. М. Городецкий) from the Poetic subcorpus of the Russian National Corpus (https://ruscorpora.ru/new/search-poetic.html). (Please do not redistribute these files!). 

**/meta**: metadata for these texts. (Please do not redistribute these files!)

**stressVariation.py**: a Python script to extract concordance lines for all tokens that might exhibit stress variation into a separate TSV file for each author and put these files into **/variationByAuthor** folder. After manual filtering, these files are put into **/variationByAuthor-checked**, and after that the expected number of word types with variable stress in a sample of 10,000 tokens is calculated for each author.

## Results

| Author | Corpus size | Types with <br> variable stress <br> (total) | Types with <br> variable stress <br> (per 10,000 tokens) |
| :--- | :--- | :--- | :--- |
| Narbut | 28,324 | 14 | 1.711 |
| Zenkevich | 26,220 | 11 | 2.402 |
| Gumilev | 56,992 | 57 | 3.554 |
| Gorodetsky | 26,653 | 14 | 2.313 |
