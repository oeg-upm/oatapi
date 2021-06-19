import spacy
import lemminflect
from owlready2 import *
import networkx as nx
from rouge import Rouge
import statistics

import query_generator

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
        self.query_generator=query_generator.QueryGenerator()




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

       # for chunk in doc.noun_chunks:
       #     print(chunk.text, "ROOT:", chunk.root.text, "ROOT_POS:", chunk.root.dep_, "HEAD:",
       #           chunk.root.head.text)

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

    # Function to load the ontology into a directed graph that can store multiedges
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


    # Function to generate the API paths according to the ontology elements detected in the CQs.
    def generateAPIPath(self, target_resource):
        nodes_found = []
        resources = ""
        classes = []
        relation=[]
        relations = []
        query_type=0
       # doc_resource = self.nlp(target_resource)

        for ent in self.entities:
            # First, check if entities found correspond to ontology class labels
            classes_found = self.searchOntologyElements(owl_class, "label", ent.lemma_)
            for clas in classes_found:
                if not clas in classes:
                    classes.append(clas)

            # Second, check if entities correspond to ontology iris. This additional step is needed when classes do not have
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

      #  for ent in self.entities:
      #      for node in self.G.nodes():
      #          if ent.lemma_ == self.getOntologyElementName(node).lower():
      #              nodes_found.append(node)
      #  print(nodes_found)

        start_char=-1
        for chunk in self.doc.noun_chunks:
           # print(chunk.text, "ROOT:", chunk.root.text, "ROOT_POS:", chunk.root.dep_, "HEAD:",
           #       chunk.root.head.text)
            for clas in classes:

                # As Spacy does not treat the beginning of some CQs as noun_chunks, we need to
                # ensure that these cases can be analyzed.
                if not chunk.start_char == 0 and not start_char == 0:
                    cq_beginning = self.doc.char_span(0, chunk.start_char - 1)
                    print(cq_beginning.text)
                    start_char = 0
                    if len(cq_beginning)>1:
                        if cq_beginning[1].is_ancestor(cq_beginning[0]):
                            resource_found = cq_beginning[1].lemma_
                            if resource_found.lower() == self.getOntologyElementName(clas).lower():
                                if not clas in nodes_found:
                                    nodes_found.append(clas)

                # When noun chunks have more than two words, they can correspond to a class whose name
                # is composed of some words (e.g. local business)
                if len(chunk) > 2:
                    if re.search(str(chunk.root.lemma_).lower(), self.getOntologyElementName(clas).lower()):
                        if not clas in nodes_found:
                            if len(nodes_found)>0:
                                for node in nodes_found:
                                    if not re.sub(r"\s+", "", self.getOntologyElementName(node).lower()) ==  re.sub(r"\s+", "",self.getOntologyElementName(clas).lower()):
                                        nodes_found.append(clas)
                                        break
                            else:
                                nodes_found.append(clas)
                elif chunk.root.lemma_.lower()==self.getOntologyElementName(clas).lower():
                    if not clas in nodes_found:
                        nodes_found.append(clas)


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
                    relations.append(relation[data]['relation'])

                resources = resources + "/" + self.setPluralFormatResource(
                    result[0]) + "/{" + self.setSingularFormatResource(result[0]) + "-id}"
                resources = resources + "/" + self.setPluralFormatResource(result[len(result) - 1])

                nodes_found = result
                relation = relations
                query_type = 2

                if target_resource[-3:] == "-id":
                    target_resource = target_resource[0:-3]

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
                                                #    query_type = 2
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
                                                    query_type = 3
                                                    resources = resources + "/" + self.setPluralFormatResource(
                                                        node) + "/{" + self.setSingularFormatResource(node) + "-id}/" + self.setPluralFormatResource(key)
                                                    relation = op

                                                    if target_resource[-3:] == "-id":
                                                        target_resource = target_resource[0:-3]

                                                    break

                elif (len(data_properties)) > 0:
                    for dp in data_properties:
                        for clas in classes:
                            if clas in dp.domain:
                                query_type = 1

                                if target_resource[-3:]=="-id":
                                    resources = resources + "/" + self.setPluralFormatResource(
                                        clas) + "/{" + self.setSingularFormatResource(clas) + "-id}"
                                else:
                                    resources = resources + "/" + self.setPluralFormatResource(clas)


                              #  for token in doc_resource.doc:
                              #      if token.tag_=="NN":
                              #          resources = resources + "/" + self.setPluralFormatResource(clas) + "/{" + self.setSingularFormatResource(clas) + "-id}"
                              #          target_resource = target_resource +"-id"
                              #          break
                              #      elif token.tag_=="NNS":
                              #          resources = resources + "/" + self.setPluralFormatResource(clas)
                              #          break



                else:
                    query_type=1
                    if target_resource[-3:] == "-id":
                        resources = resources + "/" + self.setPluralFormatResource(
                            nodes_found[0]) + "/{" + self.setSingularFormatResource(nodes_found[0]) + "-id}"
                    else:
                        resources = resources + "/" + self.setPluralFormatResource(
                            nodes_found[0])
                    #for token in doc_resource.doc:
                    #    if token.tag_ == "NN":
                    #        resources = resources + "/" + self.setPluralFormatResource(
                    #            nodes_found[0]) + "/{" + self.setSingularFormatResource(nodes_found[0]) + "-id}"
                    #        target_resource = target_resource + "-id"
                    #        break
                    #    elif token.tag_ == "NNS":
                    #        resources = resources + "/" + self.setPluralFormatResource(
                    #            nodes_found[0])
                    #        break


        except:
            try:
                #print("ERROR")
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
        return resources, nodes_found, relation, query_type, target_resource

    # Function to calculate the precision, recall, and F1 measure of the API_path defined manually and those generated
    # with OATAPI. To this end, this function applies the ROUGE method
    def rougeTest(self, apiPath, apiPathFromCorpus,lastElement):

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

    # Function to analyze the CQs from the CSV.
    # If the CSV has a column with API paths defined manually, this function allows applying the Rouge Method
    # to get the precision, recall, and f_measure values
    def cq_analysis(self):
        i = 0
        results = []
        queries =[]
        while i < len(self.corpus_df):
            cq_text = self.corpus_df.iloc[i, 0]
            print("\nCQ: " + cq_text)
           # apiPathFromCorpus = self.corpus_df.iloc[i, 1]
           # print("API Path from corpus: " + str(apiPathFromCorpus))
            self.doc = self.nlp(cq_text)
            self.entities, self.relations, self.dataProperties = self.entity_relation_identification(self.doc)
            operation, target_resource = self.getOperations()
            apiPath, ontology_elements, relation, query_type, target_resource = self.generateAPIPath(target_resource)

            if len(apiPath) > 0:
                print("The suggested API path is: " + apiPath)
            else:
                print("OATAPI can't suggest an API path")

            results.append(apiPath)
           # self.rougeTest(apiPath, apiPathFromCorpus, i)

            query = self.query_generator.generateQuery(target_resource, ontology_elements, relation, query_type)
            queries.append(query)

            i += 1
            self.entities = []
            self.relations = []
            self.dataProperties = []
        return results, queries, self.onto.name


    # Function to search the target resource according to the ontology elements.
    # First it checks if the parameter element corresponds with a class, if not it checks if the element corresponds with
    # an object property, and finally it checks if it corresponds with a datatype property
    def searchResourceElement(self, element):
        class_found = []
        op_found =[]
        dp_found =[]
        target_resource =""
        class_found = self.searchOntologyElements(owl_class, "label", element)
        if len(class_found) > 0:
            #target_resource = element
            target_resource=self.getOntologyElementName(class_found[0]).lower()
            if len(target_resource.split()) > 1:  # if the name is composed by more than 1 word
                target_resource = "-".join(target_resource.split())
            return target_resource

        op_found = self.searchOntologyElements(owl_object_property, "label", element)
        if len(op_found) > 0:
            if not op_found[0].domain[0] == op_found[0].range[0]:
                target_resource = self.getOntologyElementName(op_found[0].range[0]).lower()
                return target_resource
            else: # When the object property relates the same class (e.g. Player--> isFriendWithPlayer --> Player)
                #target_resource = element
                target_resource = self.getOntologyElementName(op_found[0].range[0]).lower()
                return target_resource
        else:
            op_found = self.searchOntologyElements(owl_object_property, "iri", element)
            if len(op_found) > 0:
                target_resource = self.getOntologyElementName(op_found[0].range[0]).lower()
                return target_resource

        dp_found = self.searchOntologyElements(owl_object_property, "label", element)
        if len(dp_found) > 0:
            target_resource = self.getOntologyElementName(dp_found[0].domain[0]).lower()
            return target_resource
        else:
            dp_found = self.searchOntologyElements(owl_object_property, "iri", element)
            if len(dp_found) > 0:
                target_resource = self.getOntologyElementName(dp_found[0].domain[0]).lower()
                return target_resource
        return target_resource

    # Function to detect the operation that should be executed in the API
    def getOperations(self):
            operationTerms = ["what", "who", "get", "list", "which", "where", "when", "obtain", "give"]
            operation = ""
            target_resource = ""

            # for each chunk from the noun_chunks
            for chunk in self.chunks:
                print(chunk.text, "ROOT:", chunk.root.text, "ROOT_POS:", chunk.root.dep_, "HEAD:",chunk.root.head.text)

                # if question starts with an operation term denoting a GET operation
                if str(chunk[0].text).lower() in operationTerms and chunk[0].i == 0:
                    operation="GET"
                    if chunk.root.pos_ == "NOUN":
                        target_resource = self.searchResourceElement(chunk.root.lemma_)
                        if not target_resource == "":
                            # If chunk.root is a singular noun
                            if chunk.root.tag_ == "NN":
                                target_resource = target_resource+ "-id"
                            # Else if chunk.root is a plural noun
                          #  elif chunk.root.tag_ == "NNS":
                           #     target_resource = chunk.root.text
                            break

                # else if the operation was already detected and the next chunk.root is a noun
                # check if it corresponds to a class, object or datatype property. If the chunk.root corresponds
                # to an ontology element retrieve the target_resource properly.

                elif not operation=="" and chunk.root.pos_ == "NOUN":
                    target_resource =self.searchResourceElement(chunk.root.lemma_)
                    if not target_resource == "":
                        if chunk.root.tag_ == "NN":
                            target_resource = target_resource+ "-id"
                       # elif chunk.root.tag_ == "NNS":
                        #    target_resource = chunk.root.text
                        break

            # Sometimes Spacy does not treat the beginning of a CQ as a noun_chunk (e.g. What features does an item have?
            # therefore, we fix this issue by adding an additional analysis by token. In this way, we are able to analyze the
            # question and get the operation and the resource target that use to be an ancestor of the operation term token.

            if operation=="":
                for token in self.doc:
                    # when question starts with an operation term that denotes a GET operation
                    if token.text.lower() in operationTerms and token.i == 0:
                        operation = "GET"
                        if self.doc[1].is_ancestor(self.doc[0]):
                            target_resource = self.searchResourceElement(self.doc[1].lemma_)
                            break
                        else:
                            for chunk in self.doc.noun_chunks:
                                if chunk.root.pos_ == "NOUN":
                                    target_resource = self.searchResourceElement(chunk.root.lemma_)
                                    if not target_resource == "":
                                        if chunk.root.tag_=="NN":
                                            target_resource= target_resource+ "-id"
                                        #elif chunk.root.tag_=="NNS":
                                            #target_resource = chunk.root.text
                                        break
                            break

            print("Operation detected: " + operation)
            print("Resource target: "+ target_resource)
            return operation, target_resource