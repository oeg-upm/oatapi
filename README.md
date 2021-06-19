# Ontology Artefacts to Application Programming Interface (OATAPI)

OATAPI takes two ontology artefacts (a set of competency questions (CQs) and the related ontology), and generates the API paths and SPARQL queries that allow solving these questions.

To run OATAPI you need Python 3.7 (or a higher version). You can find the list of required packages [here](https://github.com/paoespinozarias/oatapis/blob/main/requirements.txt).

Then, you should be able to run it as follows:

```
python3 main.py \
     -cq "CQs.csv" \
     -o "ontology" \
     -r "results"
```
- The `-cq` parameter sets the location of the competency questions file.  It must be a CSV file with a column *CQ*. If the file is on the Web, you should specify the raw URL (e.g. GitHub URL https://raw.githubusercontent.com/.../CQs.csv, Dropbox URL https://www.dropbox.com/.../CQs.csv?raw=1, etc.).

- The `-o` parameter sets the location of the ontology file or the ontology URI. The ontology should be an OWL file.

- The `-r` parameter sets the location where the results will get back as a CSV file. This file will contain the original CQs and two new columns. The first contains the API paths generated with OATAPI and the second contains the SPARQL queries to be supported by each API path.

## Supported Competency Questions

In the current version, OATAPI supports simple CQs written in English. These simple queries must be composed by the same names of the ontology elements such as classes, object properties or datatype properties. You can find some examples of the supported CQs at the *Data* directory from this repository.

To detect the correspondences between terms from the CQ and the ontology, OATAPI takes the label annotations of the ontology elements. However, when an ontology element does not have a label OATAPI will get it from its URI.


## Execution example

You can use the CQs and ontologies at the *Data* and *Onto* directories from this repository. For example, you can run OATAPI with the Videogame ontology artefacts as follows:

```
python3 main.py -cq  "Data/CQs-VGO.csv" \
-o "Onto/VideoGameOntology.owl" \
-r "Output/"
```

Or if you prefer to provide the parameter inputs as their access on the Web you can execute OATAPI as follows:

```
python3 main.py -cq  "https://raw.githubusercontent.com/paoespinozarias/oatapis/master/Data/CQs-VGO.csv" \
-o "http://vocab.linkeddata.es/vgo" \
-r "Output/"
```
As a result, you will get back a CSV file with the results located at the *Output* directory. The file name will start with the ontology name. In the execution example, your will obtain as a result the file *vgo-results.csv*
