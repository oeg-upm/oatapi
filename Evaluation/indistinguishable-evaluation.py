from owlready2 import *
import pandas as pd
import analysis

def evaluate_CQs(sheet_name, onto_location):
    corpus_df = pd.read_excel("Indistinguishable/TestbedFromFieldResearchWork.xlsx", sheet_name=sheet_name, usecols=['CQ (en)'])
    onto = get_ontology(onto_location)
    print(corpus_df)
    analysis_method = analysis.Analysis(corpus_df, onto)  #load CQs and ontology for the analysis
    results, queries, ontology_name = analysis_method.cq_analysis() #execute the analysis
    corpus_df['API path suggested'] = results
    corpus_df['Query suggested'] = queries
    print(corpus_df)

    return corpus_df


# Evaluate CQs from each Excel sheet and its corresponding ontology
pd.set_option('display.max_colwidth', 200)
corpus_df1 = evaluate_CQs('OC-LocalBusiness', "http://vocab.ciudadesabiertas.es/def/comercio/tejido-comercial")
corpus_df2 = evaluate_CQs('ZGZ-AirQuality',"http://vocab.linkeddata.es/datosabiertos/def/medio-ambiente/calidad-aire")
corpus_df3 = evaluate_CQs('ZGZ-PublicProcurement',"http://contsem.unizar.es/def/sector-publico/pproc")

# Write the results from each evaluation into an Excel file.
with pd.ExcelWriter("Results/IndistinguishableEvaluationResults.xlsx") as writer:
    corpus_df1.to_excel(writer, sheet_name='OC-LocalBusiness')
    corpus_df2.to_excel(writer, sheet_name='ZGZ-AirQuality')
    corpus_df3.to_excel(writer, sheet_name='ZGZ-PublicProcurement')