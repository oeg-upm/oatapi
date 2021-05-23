# Ontology Artefacts to APIs (OATAPIs)

OATAPIs takes a set of competency questions (CQs) and the related ontology and it generates the APIs which allows solving these questions.

To run OATAPIs you need Python 3.7 (or a higher version). You can find the list of required packages [here](https://github.com/paoespinozarias/oatapis/blob/main/requirements.txt).

Then, you should be able to run it as follows:

```
python3 main.py \
     -cq "CQs.csv" \
     -o "ontology" \
     -r "results"
```
- The `-cq` parameter sets the location of the competency questions file.  It must be a CSV file with a column *CQ*. If the file is on the Web, you should specify the raw URL (e.g. GitHub URL https://raw.githubusercontent.com/.../CQs.csv, Dropbox URL https://www.dropbox.com/.../CQs.csv?raw=1, etc.).

- The `-o` parameter sets the location of the ontology file or the ontology URI. The ontology should be an OWL file.

- The `-r` parameter sets the location where the resulting API paths will be back as a CSV file.

## Examples

You can use the CQs and ontologies at *Data* an *Onto* directories from this repository. For example, you can run OATAPIs with the Videogame ontology artefacts as follows:

```
python3 main.py -cq  "Data/CQs-VGO.csv" \
-o "Onto/VideoGameOntology.owl" \
-r "Output/"
```

Or if you prefer to provide them through their access on the Web you can execute OATAPIs as follows:

```
python3 main.py -cq  "https://raw.githubusercontent.com/paoespinozarias/oatapis/master/Data/CQs-VGO.csv" \
-o "http://vocab.linkeddata.es/vgo" \
-r "Output/"
```
As a result you will get back a CSV file with the original CQs and a new column that contains the API paths generated with OATAPIs. In this example, the resulting CSV will be located at *Output* directory.
