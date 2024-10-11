Build the docker image; 
`docker build -t cozo-db .`

Run the container: 
`docker run -d -p 5000:5000 cozo-db`


Run an example Datalog Query: 
```datalog
// Define a simple schema and insert data
[:add :person :name "Alice"]
[:add :person :name "Bob"]

// Query for all persons
[:find ?name :where [:person :name ?name]]
```



