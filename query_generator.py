from owlready2 import *

class QueryGenerator:

    def __init__(self):
        self.ent=""
        self.rel=""



    def generateQuery(self, target_resource, ontology_elements, relation, query_type):

        #query = u"SELECT DISTINCT {} {}".format("?" + target_resource+ ", ?predicate, ?object", self.where(query_type, target_resource, ontology_elements, relation))
      #  property_triples = " ?" + target_resource + " ?predicate ?object "

        select = "SELECT DISTINCT {} {}".format("?" + target_resource,
                                                self.where(query_type, target_resource, ontology_elements, relation))
        query = u"CONSTRUCT { ?" + target_resource + " ?predicate ?object } WHERE { { " + select
        return query

    # Function to configure the where clause
    def where(self, query_type, target_resource, ontology_elements, relation):
        property_triples = " } ?" + target_resource + " ?predicate ?object }"

        # when only a class is required
        if query_type==1:
            ent = self.formatUri(ontology_elements[len(ontology_elements)-1])
            where = u"WHERE {{ {} {a} {ent} }}".format("?" + target_resource, a="a", ent=ent)
            where = where +property_triples

        # when more than one class is required
        elif query_type==2:
            # if only two classes are required
            if len(ontology_elements)<3:
                ent = "?" + self.getOntologyElementName(ontology_elements[len(ontology_elements) - 2]) + "-id"
                rel = self.formatUri(relation[0])
                where = u"WHERE {{ {ent} {rel} {}}}".format("?" + target_resource, ent=ent, rel=rel)
                where = where + property_triples
            # if more than two classes are required because there are various nodes in the solution path
            else:
                print(ontology_elements)
                i = 1
                where = u"WHERE {"
                while i<len(ontology_elements):
                    rel = self.formatUri(relation[i-1])
                    ent = "?" + self.getOntologyElementName(ontology_elements[i - 1])
                    ent1 = "?" + self.getOntologyElementName(ontology_elements[i])
                    print (ent + rel + ent1)
                    if i == len(ontology_elements)-1:
                        where = where +"{ent} {rel} {}".format("?" + target_resource, ent=ent, rel=rel)
                    else:
                        if i ==1:
                            where = where + "{ent} {rel} {ent1} .".format(ent1=ent1, ent=ent+"-id", rel=rel)
                        else:
                            where = where + "{ent} {rel} {ent1} .".format(ent1=ent1, ent=ent, rel=rel)
                    i = i + 1
                where = where +" }"+ property_triples

        # when the target class name is not detected in the CQ. E.g What is the creator of the game -> the target class is Agent
        elif query_type == 3:
            ent = "?" + self.getOntologyElementName(ontology_elements[len(ontology_elements) - 1]) + "-id"
            rel=self.formatUri(relation)
            where = u"WHERE {{ {ent} {rel} {} }}".format("?" + target_resource, ent=ent, rel=rel)
            where = where + property_triples

        elif query_type==0:
            print("Query type not detected")
            where=""

        return where


    def query_prefix(self, ontology):
        onto = ontology.load()
        query_prefix="PREFIX escom:<http://vocab.ciudadesabiertas.es/def/comercio/tejido-comercial#>"
        return query_prefix


    def formatUri(self, ontology_element_uri):
        return "<"+ontology_element_uri.iri+">"


    def getOntologyElementName(self,element):
        name =""
        try:
            if len(element.label.en) > 0:
                for lab in element.label.en:
                    name = lab
            elif len(element.label) > 0:
                for lab in element.label:
                    name = lab
            else:
                name = element.name

            if len(name.split()) > 1:  # if the name is composed by more than 1 word
                name = "-".join(name.split())

            return name.lower()

        except:
            return name