# Ontology Artefacts to Application Programming Interface (OATAPI)

OATAPI takes two ontology artefacts (a set of competency questions (CQs) and the related ontology serialization) and generates the API paths and SPARQL queries that allow these questions  to be solved.

To run OATAPI you need Python 3.7 (or a higher version). You can find the list of required packages [here](https://github.com/paoespinozarias/oatapis/blob/main/requirements.txt).

Then, you should be able to run it as follows:

```
python3 main.py \
     -cq "CQs.csv" \
     -o "ontology" \
     -r "results"
```
- The `-cq` parameter sets the location of the competency questions file.  It must be a CSV file with a column *CQ*. If the file is on the Web, you should specify the raw URL (e.g. GitHub URL https://raw.githubusercontent.com/.../CQs.csv, Dropbox URL https://www.dropbox.com/.../CQs.csv?raw=1, etc.).

- The `-o` parameter sets the location of the ontology serialization file or the ontology URI. The ontology should be an OWL file.

- The `-r` parameter sets the location where the results will get back as a CSV file. This file will contain the original CQs and two new columns. The first one will include the API paths generated with OATAPI and the second one will contain the SPARQL queries that each API path must support.

## Supported Competency Questions

In the current version, OATAPI supports simple CQs written in English. These simple queries must be composed of the same names of the ontology elements such as classes, object properties, or datatype properties. You can find some examples of the supported CQs in the *Data* directory from this repository.

To detect the correspondences between terms from the CQ and the ontology serialization, OATAPI takes the label annotations of the ontology elements. These annotations must be written in English. However, when an ontology element does not have a label OATAPI will get it from its URI.


## Running example

You can use the CQs and ontologies available at the *Data* and *Ontologies* directories from this repository. For example, you can run OATAPI with the artefacts of the Videogame ontology as follows:

```
python3 main.py -cq  "Data/CQs-VGO.csv" \
-o "Ontologies/vgo.owl" \
-r "Output/"
```

Or, if you prefer to provide the parameter entries via their location on the Web, you can run OATAPI as follows:

```
python3 main.py -cq  "https://raw.githubusercontent.com/paoespinozarias/oatapis/master/Data/CQs-VGO.csv" \
-o "http://vocab.linkeddata.es/vgo" \
-r "Output/"
```
After running OATAPI, you will get a CSV file with the results located in the *Output* directory. The file name will start with the name of the ontology. In the running example, you will obtain as a result the file *vgo-results.csv*
