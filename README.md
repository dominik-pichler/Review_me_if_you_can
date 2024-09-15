# Knowledge Graphs for the win! 

```
                                   /\
                              /\  //\\
                       /\    //\\///\\\        /\
                      //\\  ///\////\\\\  /\  //\\
         /\          /  ^ \/^ ^/^  ^  ^ \/^ \/  ^ \
        / ^\    /\  / ^   /  ^/ ^ ^ ^   ^\ ^/  ^^  \
       /^   \  / ^\/ ^ ^   ^ / ^  ^    ^  \/ ^   ^  \       *
      /  ^ ^ \/^  ^\ ^ ^ ^   ^  ^   ^   ____  ^   ^  \     /|\
     / ^ ^  ^ \ ^  _\___________________|  |_____^ ^  \   /||o\
    / ^^  ^ ^ ^\  /______________________________\ ^ ^ \ /|o|||\
   /  ^  ^^ ^ ^  /________________________________\  ^  /|||||o|\
  /^ ^  ^ ^^  ^    ||___|___||||||||||||___|__|||      /||o||||||\
 / ^   ^   ^    ^  ||___|___||||||||||||___|__|||          | |
/ ^ ^ ^  ^  ^  ^   ||||||||||||||||||||||||||||||oooooooooo| |ooooooo
ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
```

## 1. Scenario
Short-Term Renting business is hard, but without the right monitoring tools for customer satisfaction, it is even harder(then it has to be).
This Repo utilizes modern Knowledge-Graph Approaches to assist hotels and short-term rental businesses in identifying problems regarding their cleaning services. 
In particular, it is aiming at identifying if certain appartements or cleaning personals form clusters of exceptionally good or bad customer experiences.
Hence the thereby modeled KG should provided the user with a good structure for all general queries. 

### Presentation Layer
For this reason, this repo provides a presentation layer that displays the following information in a streamlit app to the user: 
- A list of cleaning personal with best/worst customer experiences. This insight could then be used to infer insights for improvements in cleaning protocols for other appartements.
- A list of apartments that are linked to the best/worst customer experiences.
- A analysis if certain cleaning people became a central node of the network.
- If certain clusters of apartments, cleaning personals or bookings exist with good or bad customer experiences exist.

and in addition, a graph query console will maybe be integrated to where the user can benefit from several advantages of KG over traditional RDBs. More specifically: 
- Identification of guest preferences
- Easier mapping between bookings, apartments and cleaners in general 
- The user can explore complex relationships, such as identifying which bookers tend to book for large groups or which cleaners are associated with the most positive reviews. This kind of query can be cumbersome in a traditional RDBMS due to the need for multiple joins and complex query logic.
- Cross-Entity Analysis: With a knowledge graph, you can analyze cross-entity relationships, such as how booking durations correlate with review sentiment or how the time of year affects booking patterns and guest satisfaction. This holistic view can be difficult to achieve with a traditional relational database structure.



## 2. KG Construction 

### Data Source
The ABT (Analytical Base Table) consists of the following columns: 
| Column Name         | Data Type      | Source |
|---------------------|----------------|--------|
| Booking_ID  (PK)    | INT            | KROSS        |
| Duration_of_stay    | FLOAT          |  KROSS      |
| Start_date_of_stay  | TIME STAMP     |  KROSS      |
| Booker              | STRING         |  KROSS      |
| Guests              | STRING         |  KROSS      |
| Appartement         | STRING         |  KROSS      |
| Cleaner             | STRING         |  TIMETAC      |
| Review Text         | TEXT           |  KROSS      |

that have been derived (as depicted later on in the architecture section) from two APIs:
1. **KROSS**: A plattform that works as datahub for the management of hotels/appartements. In this case, it is used to get access to all booking relevant data
2. **TimeTac**: A plattform that allows to track process times of (cleaning) people. In this case, it is being used to track/access data on how has cleaned which appartement when.

For this demonstration purpose, the production data has been used and been anonymized using `data_anonimizer.py` and stored in `data\demo_data.csv`


### Architecture
This application utilizes data that has been fetched from KROSS and TimeTac via their internal APIs  is currently stored in a AWS RDS in multiple tables using the architecture displayed below:
<br>
![Application_Architecture.png](drawings/Application_Architecture.png)

<br>
<br>


Original the data is being fetched from the two API's utilizing a python script (`ADD ME `) that runs in a AWS Lamda that is being executed once per day.
The data fetched, is then stored in extraction tables in an PostGres DB stored in AWS RDS (serving as central source of truth) and then automatically (via AWS Lamda again) processed into the bespoken ABT.

In the meantime, an adapter (running on-premise as docker container), is daily fetching new booking data in the ABT, sends the reviews to a sentiment model (`sentiment_model.py`) that returns sentiment scores for each review.
After that, the data gets transformed into a graph-structure and then added to an on-premise Neo4J Database (Dockerized) to store the KG.

Through this procedure described above, the KG is continuously fed with the newest data available and therefore constantly evolving.
![KG_Architecture.png](drawings/KG_Architecture.png)

<br>

### Technologies used: 
Starting out, the **AWS Suite** (running Python and PostGRES) was chosen for data fetching, job scheduling and classic RDBS (using PostGRES as Single Source of Truth). 
Part of the decision for this technology suit was it's general purpose, high scalability and wide array of utilities. 
In addition it provides a strong architectural backbone for all kind of ML-Application, being it classic, or graph based, allowing them to flourish in harmony and synergy.


**Neo4j** was then chose as a database for storing the built Knowledge Graph(s), while other database have been investigated, some being: 
- Amazons's own solution - Neptune
- Microsoft's Azure Cosmos DB
- Dgraph
- ArangoDB
- OrientDB
- ....



While each DB provided individual advantages and disadvantages, Neo4j was convincing for this project, mainly due to it's great support for graph data structure, Cypher's amazing syntax, the efficient querying and the docker support, leading to great flexibility, solid performance, and eas of use that was really appealing.
The opportunity to add Neo4j in a docker container to the existing technical infrastructure in AWS (leveraging EC2) underlines the flexibility and scalability of this technology.






Eventually **PyTorch Geometric** was choosen over other Frameworks like DGl and Graphnets 