import string, nltk

question_to_id_mapping, id_to_question_mapping, ans_id_mappings = {}, {}, {}
TfIdfVector, tfidf_values = [], []

DEFAULT_ANSWER = "No Answers found"

def lemma_normalize(text):
    def lemmatize_tokens(lemmatizer, tokens):
        return [lemmatizer.lemmatize(token) for token in tokens]

    global punctuation_dictionary, lemmatizer
    return lemmatize_tokens(lemmatizer, nltk.word_tokenize(text.lower().translate(punctuation_dictionary)))

def compute_similarity(query):
    global sentence_tokens, DEFAULT_ANSWER
    global TfIdfVector, tfidf_values
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    tfidf_query = TfIdfVector.transform([query])[0]
    similarity_values = cosine_similarity(tfidf_query, tfidf_values)
    flattened = similarity_values.flatten()
    flattened.sort()
    req_tfidf = flattened[-2]
    
    if req_tfidf == 0:
        return DEFAULT_ANSWER
    else:
        indexes = similarity_values.argsort()[0][::-1][:10]
        return list(map(lambda idx: sentence_tokens[idx], indexes))

def get_answers(query):
    global question_to_id_mapping, ans_id_mappings

    print('Almost done...', end='\r')
    questions = compute_similarity(query)
    if questions == DEFAULT_ANSWER:
        return DEFAULT_ANSWER
    
    ids = list(map(lambda qn: question_to_id_mapping[qn[:-1]], questions))
    results = {}
    for question_id in ids:
        try:
            results[question_id] = ans_id_mappings[question_id]
        except:
            pass
    
    return results

def read_data():
    global sentence_tokens, question_to_id_mapping, id_to_question_mapping, ans_id_mappings
    global TfIdfVector, tfidf_values
    import pickle

    print('Hold on...', end='\r')
    question_to_id_mapping, ans_id_mappings, sentence_tokens = pickle.load(open('data/data.pickle', 'rb'))
    id_to_question_mapping = pickle.load(open('data/mapping.pickle', 'rb'))
    TfIdfVector, tfidf_values = pickle.load(open('data/model.pickle', 'rb'))

def beautify_print(matches):
    global id_to_question_mapping
    import html2text

    for question_id in matches.keys():
        question = id_to_question_mapping[question_id]

        if question_id not in ans_id_mappings:
            continue
        
        print('-'*60)
        print('Question title: ', end='')
        print(question['title'] + '\nDescription: \n' + html2text.html2text(question['body']))

        for i, answer in enumerate(ans_id_mappings[question_id]):
            print('Answer ' + str(i+1) + ':', end='\n\n')
            print(html2text.html2text(answer['body']))
            print()

        print('-'*60)

def PyStuck(your_code):
    exception = False
    try:
        your_code()
    except Exception as err:
        import traceback, sys

        traceback.print_exc(file=sys.stderr)
        exception = str(err)

        if input('Get help from stackoverflow? [y/n]: ').lower() == 'y':
            print('-'*60, end='\n')
            read_data()
            matches = get_answers(exception)
            print("Here's some content from StackOverflow")
            print('-'*60, end='\n\n')

            for question_id in id_to_question_mapping.keys():
                if question_id not in ans_id_mappings:
                    continue
                for i, answer1 in enumerate(ans_id_mappings[question_id]):
                    for j, answer2 in enumerate(ans_id_mappings[question_id]):
                        if answer1['score'] < answer2['score']:
                            temp = ans_id_mappings[question_id][i]
                            ans_id_mappings[question_id][i] = ans_id_mappings[question_id][j]
                            ans_id_mappings[question_id][j] = temp

            beautify_print(matches)
        else:
            print('Good luck with your error!')