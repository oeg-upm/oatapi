from owlready2 import *
import pandas as pd
import argparse
import analysis

parser = argparse.ArgumentParser()
parser.add_argument("-cq", "--competencyQuestion", default="Data/CQs-VGO.csv",help="A set of competency questions in CSV format")
parser.add_argument("-o", "--ontology", default="http://vocab.linkeddata.es/vgo",help="the ontology URI or OWL file")
parser.add_argument("-r", "--results", default= "Output/",help="the file location of OATAPIs results")
args=parser.parse_args()

if args.competencyQuestion and args.ontology:
    pd.set_option('display.max_colwidth', 200)
    corpus_df = pd.read_csv(args.competencyQuestion, sep=';', usecols=['CQ'])
    onto = get_ontology(args.ontology)
    analysis = analysis.Analysis(corpus_df, onto)
    results, queries, ontology_name = analysis.cq_analysis()
    corpus_df['API path suggested by OATAPI']=results
    corpus_df['queries'] = queries
    print(corpus_df)
    results_location= args.results + ontology_name+ "-results.csv"
    corpus_df.to_csv(results_location, index=False)
else:
    print("Incomplete arguments")

