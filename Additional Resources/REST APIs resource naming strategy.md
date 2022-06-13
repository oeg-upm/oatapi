# REST APIs resource naming strategy

REST APIs follow a resource identifier design (aka resource naming) strategy with URIs.  A generic URI syntax, according to [1], has the following structure:

`URI = scheme "://" authority "/" path [ "?" query ] [ "#" fragment ]`.

In this structure, _scheme_ refers to a specification to assign identifiers within that scheme. _Authority_ concerns to the naming authority which governs the name space defined in the remainder of the URI. _Path_ regards to data (usually organized in hierarchical form) that identifies a resource within the scheme and the authority. _Query_ refers to a set of optional parameters to identify the resource or provide additional capabilities. Finally, the optional _fragment_ component allows to identify a secondary resource by reference.

## Rules for naming REST APIs

Unlike ontology naming strategies, that do not follow a unified convention, in REST APIs the rules for naming resources are clearly specified, discussed and exemplified in several works. However, we provide a summary of the main decisions, provided in [2] and [3], that should be considered when naming resources for KG data consumption, i.e. to define the path component of the URI namely API path. This path terminates when there is a question mark (?), a hash character (#), or by the end of the URI. Next, we present the most relevant rules adopted for the API path design whether it is done manually or automated.

For illustrating purposes, we will use an example API throughout this section with the following URI scheme and authority components: `http://api.example.com`; however, we will omit to include this part in the examples provided.

1. Use lowercase letters for resource paths. For example, the path of a collection of countries `/countries`
1. Use forward slash separator (/) to indicate a hierarchical relationship. In addition, avoid using this separator at the end of the resource. For example, countries contain provinces therefore the path would be  `/countries/provinces`
1. Use singular nouns for naming single resources and plural nouns for collections of resources. For example, the resource path of a collection of countries would be `/countries` and for a single country would be `/spain`
1. Use hyphens (-) to improve the readability and avoid using underscores (_). For example, to represent the Czech Republic resource path would be `/czech-republic`
1. Use URI templates to include path segments that must be substituted before resolution. For example, `/countries/{countryId}` contains the template `{countryId}` that will be substituted by the REST API or its clients, and will adopt a specific numeric or alphanumeric identifier value like `/countries/1234` which refers to a country with ID 1234
1. Do not include file extensions. Instead, manage a content negotiation strategy to provide the requested files accordingly
1. Do not include CRUD operation names. Instead, use HTTP request methods to indicate what function should be performed

In addition, APIs use to include a query component. This component allows users to achieve the following functionality:
1. Filtering collections of resources. For example, the call `GET /countries?inhabitants-number>=10000000` requests for countries with inhabitants number major or equal to 10000000.
1. Paginating collection results. For example, the call `GET /countries?pageSize=25&pageStartIndex=50` will get back maximum 25 countries in the response (specified in the `pageSize` parameter) and the first in the response will be the fifty country (defined in the `pageStartIndex` parameter). In addition, other parameters can be specified to manage pagination, for example, `offset` to define the beginning page of results, `limit` to specify the maximum number of results in a specific page, `cursor` to indicate what is the resource from which the request should begin, among others.
1. Sorting collection results. For example, the call `GET /countries?sort=inhabitants-number` will bring back the countries ordered by inhabitants number. In addition, the sorting can be configured as ascendant or descendant, if desired.

## Rules for naming REST APIs based on ontology artefacts

Once we have explained the common practices for naming REST APIs, we propose additional rules that should be adopted to generate APIs based on ontology artefacts. To illustrate these rules we will use the [Video Game Ontology](http://vocab.linkeddata.es/vgo) and its [competency questions](https://doi.org/10.5281/zenodo.1967306).

1. Use the ontology class label to name the API paths. For example, the CQ _"List all players"_ would have the API path `/players` because the answer is represented by the class with label `Player`. Note that the path is in plural and lowercase as recommended in the common practices.
1. When the CQ involves more than one ontology class take into account the following alternatives:

   (a) If the CQ regards to two ontology classes and there is a directed relation between them, take the ontology domain class of this relation as the first level of the resource hierarchy and its range as the next level. For example, the CQ _"What games has the player played?"_ would have the API path `/players/{player-id}/games` because the answer is represented by the object property _has played_ with domain _Player_ and range _Game_. Note that there is needed the `{player-id}` template because the CQ ask for a specific player.

   (b) If the CQ regards to two ontology classes and there is not a directed relation between them the following scenarios can occur:

       (i) There are several classes and relations between them that allow finding a directed walk from the origin and target class. Therefore, define the API path considering only the origin and target ontology classes. For example, the CQ _"What are the items of a player?"_ would have the API path `/players/{player-id}/items`. Despite the walk to solve the CQ involves the relationships _Player ownsCharacter Character_ and _Character ownsItem Item_, the API path considers only the start and end classes of the solution walk.
       (ii) If there is an inverse relation between the origin and target classes, the CQ can be solved because this relation allows defining a SPARQL query to get the requested data. Therefore, define the API path taking only the origin class and use the target one to specify a query parameter. For example, the CQ _"List all games of a certain genre"_ would have the API path `/games?genre={genre-id}` because there is not a directed relation between _Genre_ and _Game_ classes but there is the inverse relation _has genre_ between _Game_ and _Genre_. The template `{genre-id}` should be substituted by the id value of the required genre.

1. When the origin and target are the same ontology class and there is a relation between them, define the API path as explained in rule 2a. In addition, insert the label of this relation in the path and between the classes it relates. For example, the CQ _"What are the friends of a player?"_ would have the API path `/players/{player-id}/is-friend-with-player/players` because the class _Player_ is related to itself to describe that a player has friends that are also players (this relation is represented by the object property _is friend with player_). Note that there is needed the `{player-id}` template because the CQ ask for a specific player.
1. Use ontology property labels to define the names of filter parameters for those cases when the CQs define specific criteria to search for a resource. For example, the CQ _"What are the games released after 5 January 2010?"_ would have the API path `/games?release-date>"05/01/2010"` because the class _Game_ has the datatype property _release date_ that represents when the game was released.
1. When the ontology elements do not have labels (for example, when the ontology reuse elements by referencing to other ontology) use the URI fragment of the ontology element to name the API path or query component, and format the label according to the common practices. Use the URI fragment only if it is not an opaque URI.
1. Avoid defining nested resources with more than two nested levels.

### References
[1] Berners-Lee, T., Fielding, R., and Masinter, L. (1998). RFC2396: Uniform resource identifiers (URI): generic syntax.

[2] Masse, M. (2011). REST API Design Rulebook: Designing Consistent RESTful Web Service Interfaces. O’Reilly Media, Inc.

[3] Richardson, L., Amundsen, M., and Ruby, S. (2013). RESTful Web APIs: Services for a Changing World. O’Reilly Media, Inc.
