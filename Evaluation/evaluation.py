from rouge import Rouge
import statistics
from owlready2 import *
import pandas as pd
import sys
sys.path.append('./')
import analysis


# Function to calculate the precision, recall, and F1 measure of the API_path defined manually (following the
# REST APIs resource naming strategy) and those generated with OATAPI. To this end,
# this function applies the ROUGE method
def rougeTest(apiPath, apiPathFromCorpus,lastElement, corpus_df):
    rouge = Rouge()
    f_measure = []
    precision = []
    recall = []
    if isinstance(apiPathFromCorpus, float):
        if apiPath == "":
            scores = rouge.get_scores("not generated", "undefined")
        else:
            scores = rouge.get_scores(apiPath, "undefined")
    else:
        if apiPath == "":
            scores = rouge.get_scores("not generated", apiPathFromCorpus)
        else:
            scores = rouge.get_scores(apiPath, apiPathFromCorpus)
    rouge_values = scores[0]['rouge-1']
    print("ROUGE score of the predicted API: " + str(rouge_values))
    for key in rouge_values:
        if key == "f":
            f_measure.append(rouge_values[key])
        elif key == "p":
            precision.append(rouge_values[key])
        elif key == "r":
            recall.append(rouge_values[key])

    if lastElement ==  len(corpus_df)-1:
        print("\nThe mean of the Rouge values is:")
        print("Total precision: ")
        print(statistics.mean(precision))
        print("Total recall: ")
        print(statistics.mean(recall))
        print("Total f_measure: ")
        print(statistics.mean(f_measure))
    return precision, recall, f_measure


# Function to calculate the Rouge metrics to evaluate the similarity between
# API paths manually and automatically generated
def evaluate_similarity(ontology_name):
    results_precision =[]
    results_recall = []
    results_f_measure = []
    i=0
    corpus_df = pd.read_excel("Similarity/CorpusWithAPIs-AutomaticallyGenerated.xlsx", sheet_name=ontology_name,
                                  usecols=['CQ', 'Expected API path', 'API paths suggested by OATAPI'])
    while i < len(corpus_df):
        apiPathFromCorpus = corpus_df.iloc[i, 1]
        precision, recall, f_measure=rougeTest(corpus_df.iloc[i, 2], apiPathFromCorpus, i, corpus_df)
        results_precision.append(precision)
        results_recall.append(recall)
        results_f_measure.append(f_measure)
        i += 1
    corpus_df['precision'] = results_precision
    corpus_df['recall'] = results_recall
    corpus_df['f_measure'] = results_f_measure

    return corpus_df


# Function to generate automatically the API paths from the CQs written in natural language
def generate_API_Paths(sheet_name, onto_location):
    i = 0
    CQ = []
    APIs = []
    raw_corpus_df = pd.read_excel("Similarity/CorpusWithAPIs-ManuallyGenerated.xlsx", sheet_name=sheet_name, usecols=['CQ','Expected API path'])
    while i < len(raw_corpus_df):
        API_expected = raw_corpus_df.iloc[i, 1]
        if API_expected!="undefined": #we do not evaluate those undefined API paths
            CQ.append(raw_corpus_df.iloc[i, 0])
            APIs.append(API_expected)
        i += 1

    data={'CQ': CQ, 'Expected API path':APIs}
    corpus_df = pd.DataFrame(data, columns=['CQ','Expected API path'])
    onto = get_ontology(onto_location)
    analysis_method = analysis.Analysis(corpus_df, onto)  #load CQs and ontology for the analysis
    results, queries, ontology_name = analysis_method.cq_analysis() #execute the analysis
    corpus_df['API paths suggested by OATAPI'] = results

    return corpus_df


# Generate API paths for each CQ from specific Excel sheet and its corresponding ontology
pd.set_option('display.max_colwidth', 200)
corpus_df1 = generate_API_Paths('VGO', "http://vocab.linkeddata.es/vgo")
corpus_df2 = generate_API_Paths('ESCOM', "http://vocab.ciudadesabiertas.es/def/comercio/tejido-comercial")
corpus_df3 = generate_API_Paths('SWO', "http://purl.obolibrary.org/obo/swo.owl")
corpus_df4 = generate_API_Paths('SAREF4ENVI', "https://saref.etsi.org/saref4envi/v1.1.2/saref4envi.rdf")
corpus_df5 = generate_API_Paths('NOISE', "http://vocab.ciudadesabiertas.es/def/medio-ambiente/contaminacion-acustica")
corpus_df6 = generate_API_Paths('PPROC',"http://contsem.unizar.es/def/sector-publico/pproc")
corpus_df7 = generate_API_Paths('ESAIR',"http://vocab.linkeddata.es/datosabiertos/def/medio-ambiente/calidad-aire")
corpus_df8 = generate_API_Paths('ESBICI',"http://vocab.ciudadesabiertas.es/def/transporte/bicicleta-publica")


# Write the results of the APIs generation in an Excel file.
with pd.ExcelWriter("Similarity/CorpusWithAPIs-AutomaticallyGenerated.xlsx") as writer:
    corpus_df1.to_excel(writer, sheet_name='VGO')
    corpus_df2.to_excel(writer, sheet_name='ESCOM')
    corpus_df3.to_excel(writer, sheet_name='SWO')
    corpus_df4.to_excel(writer, sheet_name='SAREF4ENVI')
    corpus_df5.to_excel(writer, sheet_name='NOISE')
    corpus_df6.to_excel(writer, sheet_name='PPROC')
    corpus_df7.to_excel(writer, sheet_name='ESAIR')
    corpus_df8.to_excel(writer, sheet_name='ESBICI')


# Calculate the Rouge metrics
pd.set_option('display.max_colwidth', 200)
evaluated_corpus_df1 = evaluate_similarity('VGO')
evaluated_corpus_df2 = evaluate_similarity('ESCOM')
evaluated_corpus_df3 = evaluate_similarity('SWO')
evaluated_corpus_df4 = evaluate_similarity('SAREF4ENVI')
evaluated_corpus_df5 = evaluate_similarity('NOISE')
evaluated_corpus_df6 = evaluate_similarity('PPROC')
evaluated_corpus_df7 = evaluate_similarity('ESAIR')
evaluated_corpus_df8 = evaluate_similarity('ESBICI')

with pd.ExcelWriter("Results/SimilarityEvaluation.xlsx") as writer:
    evaluated_corpus_df1.to_excel(writer, sheet_name='VGO')
    evaluated_corpus_df2.to_excel(writer, sheet_name='ESCOM')
    evaluated_corpus_df3.to_excel(writer, sheet_name='SWO')
    evaluated_corpus_df4.to_excel(writer, sheet_name='SAREF4ENVI')
    evaluated_corpus_df5.to_excel(writer, sheet_name='NOISE')
    evaluated_corpus_df6.to_excel(writer, sheet_name='PPROC')
    evaluated_corpus_df7.to_excel(writer, sheet_name='ESAIR')
    evaluated_corpus_df8.to_excel(writer, sheet_name='ESBICI')
