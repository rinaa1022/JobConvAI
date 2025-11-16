src/jd_parser.py – parse JD → JSON (OpenAI)

src/jd_to_neo4j.py – write the JSON into Neo4j

src/run_pipeline.py – CLI: read file → parse → write graph

src/fastapi_app.py – optional API to query the graph


export OPENAI_API_KEY=
export NEO4J_PASSWORD=

Run job parser with job descriptions
python run_pipeline.py ./jd1.txt jd2.txt jd3.txt 
