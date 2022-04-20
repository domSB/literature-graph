# Literature Graph
## General overview
This repository contains some helper scripts I used to create my **personal literature graph for 
exploratory analysis**.

I store my literature in the desktop app [Papers](https://www.papersapp.com/) which I found to work 
best, when reading and annotation my literature on my tablet. With some small adaptations, this script 
should work as well with other reference management tools.

The database for this project is the desktop version of [Neo4j](https://neo4j.com/), but you can also 
use a community server installation or the Aura SaaS DB. The main reason I chose Neo4j is their 
excellent declarative query language Cypher which I believe to be much more intuitive than SparkQL. 

For consistency and easier object access from within python, I use the Object Graph Mapper (OGM) 
[Neomodel](https://github.com/neo4j-contrib/neomodel). 

## Roadmap
- Integrate semantic scholar information to depict cross-references between publications in the personal
  literature. 

## Installation

## Useful links
[Documentation of NeoModel](https://neomodel.readthedocs.io/en/latest/index.html)
