import spacy
import lemminflect
from owlready2 import *
import networkx as nx
from rouge import Rouge
import statistics

class Analysis:

    def __init__(self, corpus, ontology):
        self.nlp = spacy.load("en_core_web_sm")
        self.onto = ontology.load()
        self.corpus_df = corpus
        self.entities = []
        self.relations = []
        self.dataProperties = []
        self.G = self.loadOntologyAsGraph(self.onto)

        self.f_measure = []
        self.precision = []
        self.recall = []


        self.chunks =[]



    # Function to extract the candidate concepts and relationships from the CQ
    def entity_relation_identification(self,doc):
        excluded_POS = ["PRON", "DET", "CCONJ", "ADV", "PUNCT", "ADP", "AUX"]
        for token in doc:
            # if token.pos_ not in excluded_POS and not token.is_stop: #do not examine the excluded POS and stop words
            if token.pos_ not in excluded_POS:  # do not examine the excluded POS and stop words
                if token.pos_ == "NOUN":
                    self.entities.append(token)

                if token.pos_ == "VERB":
                    self.relations.append(token)
                    self.entities.append(token)

                if token.pos_ == "ADJ":
                    self.dataProperties.append(token)
                    self.entities.append(token)

        print(self.entities)

        for chunk in doc.noun_chunks:
            print(chunk.text, "ROOT:", chunk.root.text, "ROOT_POS:", chunk.root.dep_, "HEAD:",
                  chunk.root.head.text)

        self.chunks = doc.noun_chunks

        return (self.entities, self.relations, self.dataProperties)


    # Function to search for ontology elements by labels/iris
    def searchOntologyElements(self, ontology_element_type, search_parameter, search_value):
        if search_parameter == "label":
            ontology_elements = self.onto.search(type=ontology_element_type, label="*" + search_value + "*",
                                            _case_sensitive=False)
        # else if ontology elements do not have a label we must to search in their IRIs
        elif search_parameter == "iri":
            ontology_elements = self.onto.search(type=ontology_element_type, iri="*" + search_value, _case_sensitive=False)
        return ontology_elements

    # Function to search for data properties by labels/iris. This version considers that dataproperties have a Domain
    # data_properties: list of data properties found in the process
    # token: token to search
    # classes: ontology classes already found in the CQ analysis
    def searchDataPropertiesFromOntology(self, data_properties, token, classes):
        dataproperties_found = self.searchOntologyElements(owl_data_property, "label", token.lemma_)
        for dp in dataproperties_found:
            for dom in dp.domain:
                if dom in classes:
                    if not dp in data_properties:
                        data_properties.append(dp)

        dataproperties_found_with_iri = self.searchOntologyElements(owl_data_property, "iri", token.lemma_)
        for dp in dataproperties_found_with_iri:
            if not dp in dataproperties_found:
                for dp in dataproperties_found_with_iri:
                    for dom in dp.domain:
                        if dom in classes:
                            if not dp in data_properties:
                                data_properties.append(dp)
        return data_properties

    # Function to search for data properties depending on the type of token found in the CQ.
    def getDataProperties(self, classes):
        data_properties = []
        # Check if there are datatype_properties in the ontology that match nouns found in the CQ
        # and check if them are not part of the ontology classes found.
        for ent in self.entities:
            for clas in classes:
                if not re.search(ent.lemma_, self.getOntologyElementName(clas).lower()):
                    data_properties = self.searchDataPropertiesFromOntology(data_properties, ent, classes)

        # Check if there are datatype properties in the ontology that match dataProperties found in the CQ
        for dat in self.dataProperties:
            data_properties = self.searchDataPropertiesFromOntology(data_properties, dat, classes)

        return data_properties

    def searchObjectPropertiesFromOntology(self,object_properties, token):
        objectproperties_found = self.searchOntologyElements(owl_object_property, "label", token.lemma_)
        for obj in objectproperties_found:
            if not obj in object_properties:
                object_properties.append(obj)

        objectproperties_found_with_iri = self.searchOntologyElements(owl_object_property, "iri", token.lemma_)
        for obj in objectproperties_found_with_iri:
            if str(obj.name).lower() == token.lemma_:
                if not obj in objectproperties_found:
                    if not obj in object_properties:
                        object_properties.append(obj)

        return object_properties

    def getOntologyElementName(self,element):
        try:
            if len(element.label.en) > 0:
                for lab in element.label.en:
                    return lab
            elif len(element.label) > 0:
                for lab in element.label:
                    return lab
            else:
                return element.name
        except:
            return ""

    def getObjectProperties(self,classes):
        object_properties = []
        for ent in self.entities:
            for clas in classes:
                if not re.search(ent.lemma_, self.getOntologyElementName(clas).lower()):
                    object_properties = self.searchObjectPropertiesFromOntology(object_properties, ent)

        for rel in self.relations:
            object_properties = self.searchObjectPropertiesFromOntology(object_properties, rel)

        return object_properties


    # Load spacy's dependency tree into a networkx graph
    def loadDependencyTree(self,doc):
        edges = []
        for token in doc:
            # if  token.pos_ not in excluded_POS:
            for child in token.children:
                edges.append(('{0}'.format(token.lemma_),
                              '{0}'.format(child.lemma_)))
        return nx.Graph(edges)


    def loadOntologyAsGraph(self,onto):
        Gonto = nx.MultiDiGraph()
        onto_objectProperties = onto.object_properties()
        onto_classes = onto.classes()

        for clas in onto_classes:
            if not clas in Gonto.nodes():
                Gonto.add_node(clas)

        for prop in onto_objectProperties:
            for domain in prop.domain:
                if isinstance(domain, And) | isinstance(domain, Or):
                    for d in domain.Classes:
                        for range in prop.range:
                            if isinstance(range, And) | isinstance(range, Or):
                                for r in range.Classes:
                                    Gonto.add_edge(d, r, relation=prop)
                            else:
                                Gonto.add_edge(d, range, relation=prop)
                else:
                    for range in prop.range:
                        if isinstance(range, And) | isinstance(range, Or):
                            for r in range.Classes:
                                Gonto.add_edge(domain, r, relation=prop)
                        else:
                            Gonto.add_edge(domain, range, relation=prop)
        return Gonto


    # Function that gets the resource name in its singular form.
    def setSingularFormatResource(self, resName):
        resource = self.getOntologyElementName(resName).lower()
        if len(resource.split()) > 1:  # if the resource name is composed by more than 1 word
            resource = "-".join(resource.split())

        return resource

    # Function that gets the resource name in its plural form.
    # It uses the lemminflect library to apply the inflect method for the corresponding token of the resource name
    def setPluralFormatResource(self, resName):
        doc1 = self.nlp(self.getOntologyElementName(resName).lower())
        resource = doc1[len(doc1)-1]._.inflect('NNS')
        if len(doc1) > 1:  # if the resource name is composed by more than 1 word
            resource = str(doc1[0]) + "-"+resource

        return resource


    def generateAPIPath(self):
        nodes_found = []
        resources = ""
        classes = []

        for ent in self.entities:
            # First, check if entities found correspond with ontology class labels
            classes_found = self.searchOntologyElements(owl_class, "label", ent.lemma_)
            for clas in classes_found:
                if not clas in classes:
                    classes.append(clas)

            # Second, check if entities correspond with ontology iris. This additional step is needed when classes do not have
            # labels, for example, when reusing ontology classes by reference.
            classes_found_with_iri = self.searchOntologyElements(owl_class, "iri", ent.lemma_)
            for clas in classes_found_with_iri:
                if not clas in classes_found:
                    classes.append(clas)
        print("Clases:")
        print(classes)
        data_properties = self.getDataProperties(classes)
        print(data_properties)
        object_properties = self.getObjectProperties(classes)
        print(object_properties)

        for ent in self.entities:
            for node in self.G.nodes():
                if ent.lemma_ == self.getOntologyElementName(node).lower():
                    nodes_found.append(node)
        print(nodes_found)

       # for chunk in self.chunks:
       #     print(chunk.text, "ROOT:", chunk.root.text, "ROOT_POS:", chunk.root.dep_, "HEAD:",
       #           chunk.root.head.text)
       #     for clas in classes:
       #         if re.search(str(chunk.root.text).lower(), self.getOntologyElementName(clas).lower()):
       #             for node in nodes_found:
       #                 if not self.getOntologyElementName(node).lower() == self.getOntologyElementName(clas).lower():
       #                     nodes_found.append(clas)
        try:
            if len(nodes_found) > 1:
                print("The shortest paths between " + self.getOntologyElementName(
                    nodes_found[1]) + " and " + self.getOntologyElementName(
                    nodes_found[0]) + " are:")
                all_paths = nx.all_simple_paths(self.G, nodes_found[1], nodes_found[0])
                for path in sorted(all_paths, key=len):
                    j = 0
                    result = nx.bidirectional_shortest_path(self.G, nodes_found[1], nodes_found[0])
                    if len(result) == len(path):
                        while j < len(path) - 1:
                            relation = self.G.get_edge_data(path[j], path[j + 1], key=None)
                            for data in relation:
                                print(self.getOntologyElementName(path[j]) + " --" + self.getOntologyElementName(
                                    relation[data]['relation']) + "--> " + self.getOntologyElementName(path[j + 1]))
                            j += 1
                        print("\n")
                result = nx.bidirectional_shortest_path(self.G, nodes_found[1], nodes_found[0])
                print("The random shortest path selected is:")
                print(result)
                i = 0
                while i < len(result) - 1:
                    relation = self.G.get_edge_data(result[i], result[i + 1], key=None)
                    for data in relation:
                        print(self.getOntologyElementName(result[i]) + " --" + self.getOntologyElementName(
                            relation[data]['relation']) + "--> " + self.getOntologyElementName(result[i + 1]))
                    i += 1

                resources = resources + "/" + self.setPluralFormatResource(
                    result[0]) + "/{" + self.setSingularFormatResource(result[0]) + "-id}"
                resources = resources + "/" + self.setPluralFormatResource(result[len(result) - 1])

            else:
                if (len(object_properties)) > 0:
                    for node in nodes_found:
                        neighbours = self.G[node]
                        for key in neighbours:
                            for op in object_properties:
                                edge_data = self.G.get_edge_data(node, key, key=None)
                                for data in edge_data:
                                    if self.getOntologyElementName(edge_data[data]['relation']) == self.getOntologyElementName(
                                            op):
                                        for rel in self.relations:
                                            if re.search(rel.lemma_, self.getOntologyElementName(op).lower()):
                                                if self.getOntologyElementName(node) in [self.getOntologyElementName(range) for
                                                                                    range in op.range]:
                                                    target = self.setPluralFormatResource(op)
                                                else:
                                                    target  = self.setPluralFormatResource(key)
                                                resources = resources + "/" + self.setPluralFormatResource(
                                                    node) + "/{" + self.setSingularFormatResource(node) + "-id}/" + target
                                                break
                                        for ent in self.entities:
                                            if not ent in self.relations:
                                                if re.search(ent.lemma_, self.getOntologyElementName(op).lower()):
                                                    resources = resources + "/" + self.setPluralFormatResource(
                                                        node) + "/{" + self.setSingularFormatResource(node) + "-id}/" + self.setPluralFormatResource(key)
                                                    break

                elif (len(data_properties)) > 0:
                    for dp in data_properties:
                        for clas in classes:
                            if clas in dp.domain:
                                resources = resources + "/" + self.setPluralFormatResource(clas) + "/{" + self.setSingularFormatResource(clas) + "-id}"
                else:
                    resources = resources + "/" + self.setPluralFormatResource(nodes_found[0]) + "/{" + self.setSingularFormatResource(nodes_found[0]) + "-id}"

        except:
            try:
                result = nx.bidirectional_shortest_path(self.G, nodes_found[0], nodes_found[1])
                if len(result) > 0:
                    print("The ontology does not have a directed relation between " + str(
                        self.getOntologyElementName(result[0])) + " and " + str(
                        self.getOntologyElementName(nodes_found[1])) + " classes.")
                    print("However, OATAPIs suggest you an alternative path")
                    resources = resources + "/" + self.setPluralFormatResource(
                        result[0]) + "/{" + self.setSingularFormatResource(result[0]) + "-id}?" + self.setSingularFormatResource(
                        nodes_found[1]) + "=" + self.setSingularFormatResource(nodes_found[1]) + "-id"
            except:
                print("There is not a path between the nodes found")
        return resources


    def rougeTest(self, apiPath, apiPathFromCorpus,lastElement):
        # Retrieve the precision, recall, and F1 measure of the generated API_path according to the ROUGE method
        rouge = Rouge()
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
                self.f_measure.append(rouge_values[key])
            elif key == "p":
                self.precision.append(rouge_values[key])
            elif key == "r":
                self.recall.append(rouge_values[key])

        if lastElement ==  len(self.corpus_df)-1:
            print("\nThe mean of the Rouge values is:")
            print("Total precision: ")
            print(statistics.mean(self.precision))
            print("Total recall: ")
            print(statistics.mean(self.recall))
            print("Total f_measure: ")
            print(statistics.mean(self.f_measure))

        return

    def cq_analysis(self):
        i = 0
        results = []
        while i < len(self.corpus_df):
            cq_text = self.corpus_df.iloc[i, 0]
            print("\nCQ: " + cq_text)
           # apiPathFromCorpus = self.corpus_df.iloc[i, 1]
           # print("API Path from corpus: " + str(apiPathFromCorpus))
            self.doc = self.nlp(cq_text)
            self.entities, self.relations, self.dataProperties = self.entity_relation_identification(self.doc)
            apiPath = self.generateAPIPath()

            if len(apiPath) > 0:
                print("The suggested API path is: " + apiPath)
            else:
                print("OATAPI can't suggest an API path")

            results.append(apiPath)
           # self.rougeTest(apiPath, apiPathFromCorpus, i)
            i += 1
            self.entities = []
            self.relations = []
            self.dataProperties = []

        return results