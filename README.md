# Literature Graph
## General overview
This repository contains some helper scripts I used to create my **personal literature graph for 
exploratory analysis**.

I store my literature in the desktop app [Papers](https://www.papersapp.com/) which I found to work 
best, when reading and annotating my literature on my tablet. If you work with the open source software 
[Zotero](https://www.zotero.org/), then it also directly supported. 
Just provide the path to your Papers or Zotero sqlite-Database file. The application is designed to recognise automatically 
which reference manager you use.
With some small adaptations, this script should work with other reference management tools as well. Feel free to 
contribute for your personally preferred reference management tool. 
                            
The database for this project is the desktop version of [Neo4j](https://neo4j.com/), but you can also 
use a community server installation or the Aura SaaS DB. The main reason I chose Neo4j is their 
excellent declarative query language Cypher which I believe to be much more intuitive than SparQL. Furthermore, 
Neo4J Bloom is a magnificent tool to visually explore you literature graph.

For consistency and easier object access from within python, I use the Object Graph Mapper (OGM) 
[Neomodel](https://github.com/neo4j-contrib/neomodel). 

## Roadmap
- Integrate semantic scholar information to depict cross-references between publications in the personal
  literature. 
- Maybe use Institutional Information to depict research groups.

## Installation
To be done

## Useful links
[Documentation of NeoModel](https://neomodel.readthedocs.io/en/latest/index.html)
