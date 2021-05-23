from owlready2 import *
import pandas as pd
import argparse
import Analysis


parser = argparse.ArgumentParser()
parser.add_argument("-cq", "--competencyQuestion", help="A set of competency questions in CSV format")
parser.add_argument("-o", "--ontology", help="the ontology URI or OWL file")
parser.add_argument("-r", "--results", help="the file location of OATAPIs results")
args=parser.parse_args()

if args.competencyQuestion and args.ontology:
    pd.set_option('display.max_colwidth', 200)
   # corpus_df=pd.read_csv(args.competencyQuestion,sep=';', usecols=['CQ', 'API_path']) #If the CSV has the API paths defined manually
    corpus_df = pd.read_csv(args.competencyQuestion, sep=';', usecols=['CQ'])
    print(corpus_df)
    onto = get_ontology(args.ontology)
    analysis = Analysis.Analysis(corpus_df, onto)
    results=analysis.cq_analysis()
    corpus_df['API paths suggested by OATAPIs']=results
    print(corpus_df)
    results_location= args.results + "results.csv"
    corpus_df.to_csv(results_location, index=False)
else:
    print("Incomplete arguments")

