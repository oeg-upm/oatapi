# API Specification template
This ad-hoc template allows describing the relevant details of an API.

#### General information

| General parameters |            Information |
| ------------------------ | ------------------------ |
| API name:                |   |
| API version:             |   |
| Base URL:                |  |
| API description:         |  |
| License:                 |  |
| Authorization:           |  |
| Contact support:         |  |


#### Details of each API path
| API path | Operation | Input | Output |
| ---------| ----------------------- | ------------------------ | ------------------------ |
|                          |  |  |  |
|                          |  |  |  |
|                          |  |  |  |
|                          |  |  |  |
|                          |  |  |  |

#### Status codes
| Code                     | Description | Detail |
| ------------------------ |-----------| -----------|
|                          |  |  |
|                          |  |  |
|                          |  |  |
|                          |  |

Regarding the sections of this template, the *general information section* contains several fields that allows describing metadata such as the name, version, description, license, and the base URL of the API. In addition, the authorization field allows describing whether credentials or token are or not required for consuming the API. Moreover, the contact field allows providing information on who contact for API support.

As for the *details of API path section*, it allows listing the paths and the available operations for each path together with their inputs and outputs. Finally, the *status codes section* allows defining which code numbers will be delivered to application developers based on the status of the executed operation. These codes should be provided along with their description and detail. These codes are those HTTP status codes defined by [RFC7231](https://datatracker.ietf.org/doc/html/rfc7231\#section-6), HTTP status codes are the common codes used in REST APIs.


## API specification example

The following example corresponds to the specification for some of the CQs of the Local Business Census Ontology.

#### General information
|   General parameters    | Information |
| ------------------------ | ------------------------ |
| API name:                                       | Local Business Census API |
| API version:                                    | 0.1 |
| Base URL                                        | [http://api.example.com](https://api.example.com/) |
| API description:                                | This API provides the operations which allows answering the competency questions defined for the development of the Local Business Census ontology. |
| License                                         | [https://www.apache.org/licenses/LICENSE-2.0.html](https://www.apache.org/licenses/LICENSE-2.0.html) |
| Authorization:                                  | Accessing this API does not require any authorization mechanism |
| Contact support:                                | support@example.com |

#### Details of each API path
| API path | Operation | Input | Output |
| ---------|------------------------ | ------------------------ | ------------------------ |
| /local-businesses/ {local-business-id}          | GET | local-business-id |  a local business instance with specific id (it will retrieve its attribute values of business sign, capacity, cadastral reference, among others.) |
| /local-businesses/ {local-business-id}/ terraces | GET | local-business-id | an array of terrace instances (each instance will retrieve its attribute values of area, table number, opening hours, number of authorized chairs, among others.) |

#### Status codes
| Code                     | Description | Detail |
| ------------------------ | -----------| -----------|
| 200                                             | OK | The request succeded. |
| 400                                             | Bad request | The request cannot be accepted because the server detected a syntax error |
| 404                                             | Not found | The requested resource was not found |
| 500                                             | Server error | Something wrong happen on the server side |
