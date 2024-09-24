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

# How to use: 
1. Start the Neo4j database via: 
```shell
docker-compose up -d
```

2. Install all needed packages from  the `requirements.txt`
3. Fill the Neo4j database with the (demo) data
   In case you want to work with the demo data, just run the `populate_KG_with_demo_data` function in `src/KG_Building_Handler.py`.

et voilà, visit http://localhost:7474/browser/ and enjoy the show


## Logic-based Reasoning:
Logic-bases reasoning  as described below, can be applied to the KG by running the `run_logic_based_reasoning()` function in `src/perform_analysis.py`.
The results will be presented in a dedicated streamlit dashboard that can started by running `streamlit run src/dashboards/LBR_dashboard.py`


## Graph Neural Networks
Deep neural network reasoning  as described below, can be applied to the KG by running the `run_GNN_reasoning()` function in `src/perform_analysis.py`.
The results will be presented in a dedicated streamlit dashboard that can started by running `streamlit run src/dashboards/GNN_dashboard.py`

# About

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

#### Analytical Base Table
The ABT consists of the following columns: 
| Column Name         | Data Type      | Source |
|---------------------|----------------|--------|
| Booking_ID  (PK)    | INT            | KROSS        |
| Start_date_of_stay  | TIME STAMP     |  KROSS      |
| Appartement         | STRING         |  KROSS      |
| Cleaner             | STRING         |  TIMETAC      |
| Review Text         | TEXT           |  KROSS      |

that have been derived (as depicted later on in the architecture section) from two APIs:
1. **KROSS**: A plattform that works as datahub for the management of hotels/appartements. In this case, it is used to get access to all booking relevant data
2. **TimeTac**: A plattform that allows to track process times of (cleaning) people. In this case, it is being used to track/access data on how has cleaned which appartement when.

##### Review Data
For advanced analytics, the collected reviews have been analyzed with modern NLP-Techniques.
1. **Translation:**
   As the customers of the appartments can (and have been) writing reviews in more then 150 different languages, we have to start out by translating them
   For this purpose, I used the `src/review_process_utils/review_translor.py` script that utilizes Google Translator to translate all reviews (when possible) to english.
2. **Entity Extraction**:
   In order to identify about what things the customers are happy/complaining about in the first place, reviews have been scanned for predefined keywords like *"mold"*, *"dust"*, *"bathroom"*,...
   The entire list including the corresponding code be found in `src/review_process_utils/ER_extractor.py`
3. **Identify Adjectives for Entities:**

4. **Sentiment Analysis**: 
   In order to provide the hotel managers another tool for effective review filtering/pre selection, a sentiment analysis utilizing BERT
   has been implemented to categorize the reviews along the following dimensions.

   ** TBD ***

This eventually yielded the following additional review data for the knowledge graph: 

| Column Name                | Data Type |
|----------------------------|-----------|
| Booking_ID  (PK)           | INT       |
| Review_Text                | TEXT      |  
| Sentiment Scores           | TEXT      | 
| Issue_Entities             | TEXT      |  
| Issue_Entities_Adjectives  | TEXT      | 

For simplification purposes this table is also stored in the AWS RDS. Of course arguments for storing this data in a NoSQL Table like MongoDB or AWS Dynamo DB could be made, but
due to the limited scope of this project I have decided to keep the overhead low and not setup another DB.



Eventually, this results in the following ABT `BASE_TABLE_KG_GENERATION` that will be used for building the Knowledge Graph: 

| Column Name               | Data Type  | Source    |
|---------------------------|------------|-----------|
| Booking_ID  (PK)          | INT        | KROSS     |
| Start_date_of_stay        | TIME STAMP | KROSS     |
| Appartement               | STRING     | KROSS     |
| Cleaner                   | STRING     | TIMETAC   |
| Review Text               | TEXT       | KROSS     |
| Sentiment Scores          | TEXT       | ML Model  |
| Issue_Entities            | TEXT       | ML Model  |
| Issue_Entities_Adjectives | TEXT       | ML_Model  | 



**Side Node:**
For this demonstration purpose, the production data has been used and been anonymized using `src/data_anonimizer.py` and stored in `data\demo_data.csv`


### Architecture
This application utilizes data that has been fetched from KROSS and TimeTac via their internal APIs  is currently stored in a AWS RDS in multiple tables using the architecture displayed below:
<br>
<br>
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






### Building the knowledge Graph: 
As introduced before, the `BASE_TABLE_KG_GENERATION` Table will be used as a starting point for the generation of a  **Knowledge Graph**
In order to do so, the data of the table above will be transformed into a Knowledge Graph based on the Ontology sketched in *Image 2*.
This has been achieved with the help of `KG_Building_Handler.py` that sets up the KG and continuously integrates new data into it. In order to be able to potentially manage multiple KG's, each KG is built inside an own Schema.
For further separation, multiple instances can be created due to the Docker based architecture.





## 3. Logic Based Reasoning on the KG

To start out, I want to connect all nodes that share the same node name by running the following `Cypher` Query
```cypher
MATCH (a), (b)
WHERE id(a) < id(b)
CREATE (a)-[:CONNECTED_TO]->(b)
```


After that, I want ot identify the most dense regions in the graph: 

```cypher
MATCH (n)-[r]->(m)
WITH n, count(r) AS degree
WHERE degree > 3 // Adjust threshold based on your data
RETURN n, degree
ORDER BY degree DESC
```

Following up, I want to figure out if certain cleaners are linked more often/central nodes to worse than average customer ratings.
I identified this via: 

```cypher
MATCH (b:Booking)-[:CLEANED_BY]->(c:Cleaner)
WITH avg(toFloat(b.`Sentiment Scores`)) AS averageSentimentScore, c, b
WHERE toFloat(b.`Sentiment Scores`) < averageSentimentScore
RETURN c.name AS CleanerName, count(b) AS belowAverageCount, size((c)--()) AS degree
ORDER BY belowAverageCount DESC, degree DESC
```

#### Results



## 4. GNNs on the KG
The first analysis concerns the high density regions, and hence grouping, meaning, I want know if the entire graph can be clustered into interesting clusters
For this task I have oriented on the paper of Tsitsulin et.al. (2023) [Link to paper](https://www.jmlr.org/papers/volume24/20-998/20-998.pdf)
In this paper, the authors have compared the following different methods, including their basic properties and introduced their own Methode *Deep Modularity Networks* (**DMoN**). 

| Method   | End-to-end | Unsup. | Node pooling | Sparse | Soft assign. | Stable | Complexity |
|----------|------------|--------|--------------|--------|--------------|--------|------------|
| Graclus  | ✘          | ✔      | ✔            | ✔      | ✘            | ✔      | O(dn + m)  |
| DiffPool | ✔          | ✔      | ✔            | ✘      | ✔            | ✘      | O(dn²)     |
| AGC      | ✘          | ✔      | ✔            | ✘      | ✘            | ✘      | O(dn²k)    |
| DAEGC    | ✘          | ✔      | ✔            | ✘      | ✘            | ✘      | O(dnk)     |
| SDCN     | ✘          | ✔      | ✔            | ✔      | ✘            | ✘      | O(d²n + m) |
| NOCD     | ✔          | ✔      | ✔            | ✘      | ✔            | ✔      | O(dn + m)  |
| Top-k    | ✔          | ✘      | ✘            | ✔      | ✘            | ✔      | O(dn + m)  |
| SAG      | ✘          | ✘      | ✔            | ✘      | ✘            | ✘      | O(dn + m)  |
| MinCut   | ✔          | ✔      | ✔            | ✔      | ✔            | ✘      | O(d²n + m) |
| DMoN     | ✔          | ✔      | ✔            | ✔      | ✔            | ✔      | O(d²n + m) |


Intrigued by their claims, I wanted to test **DMoN** on my own knowledge graph. 


Therefore, with the help of **PyTorch Geometric** I wrote a script to run this method on my onw KG.
This script can be found in `src/GNN_Handler.py`.
 **PyTorch Geometric** was chosen over other Frameworks like DGl and Graphnets due its high compatability (seamless integration into the PyTorch ecosystem), its dedicated CUDA kernels for sparse data and mini-batch, its strong community support and its research-orientation.

#### Results: 





## Presentation Layer: 
In order to present the determined results, I decided to use *Streamlit* to create a small dashboard, that can then be used 
in an real life application as **customer satisfaction and cleaning quality monitor**
I chose *Streamlit* mainly due to its ease of use, its excellece when it comes to rapid prototyping that still comes with very good user experience that can be designed in a typical pythonic way.
The thereby built dashboard can be found under `src/dashboards/monitoring_dashboard.py`
# TO READ:
 https://distill.pub/2021/gnn-intro/