from fastapi import FastAPI, HTTPException
from neo4j import GraphDatabase
from typing import List, Dict, Any
from dotenv import load_dotenv
import os

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD")

if not NEO4J_PASS:
    raise RuntimeError("NEO4J_PASSWORD is not set")

DRIVER = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
app = FastAPI(title="Job Knowledge Graph API", version="1.0.0")

@app.on_event("startup")
def startup_db_client():
    """Verify connectivity when the FastAPI server starts."""
    try:
        DRIVER.verify_connectivity()
        print("Neo4j Connection successful!")
    except Exception as e:
        print(f"Neo4j Connection FAILED. Check credentials/URI: {e}")
        
@app.on_event("shutdown")
def shutdown_db_client():
    DRIVER.close()
    print(" Neo4j Driver closed.")

@app.get("/jobs/", response_model=List[Dict[str, Any]], tags=["Job Retrieval"])
def get_all_jobs():
    """Retrieve all job postings (Job nodes) with their location and type."""
    query = """
    MATCH (j:Job)-[:LOCATED_AT]->(l:Location)
    RETURN j.title AS title, j.employment_type AS type, l.name AS location
    LIMIT 50
    """
    
    with DRIVER.session() as session:
        result = session.run(query)
        jobs = [record.data() for record in result]
        return jobs

@app.get("/jobs/search_by_skill/{skill_name}", response_model=List[Dict[str, Any]], tags=["Graph Traversal"])
def search_jobs_by_skill(skill_name: str):
    """
    Find all jobs that require a specific skill, demonstrating graph traversal.
    The query uses toLower() for case-insensitive matching.
    """
    query = """
    MATCH (s:Skill) WHERE toLower(s.name) CONTAINS toLower($skill)
    MATCH (s)<-[:REQUIRES_SKILL]-(j:Job)-[:LOCATED_AT]->(l:Location)
    RETURN j.title AS title, l.name AS location, s.name AS skill_match
    """
    
    with DRIVER.session() as session:
        result = session.run(query, skill=skill_name)
        jobs = [record.data() for record in result]
        
        if not jobs:
            raise HTTPException(status_code=404, detail=f"No jobs found requiring a skill matching: {skill_name}")
            
        return jobs

@app.get("/jobs/skills_and_tools/{job_title}", tags=["Detailed Retrieval"])
def get_job_details(job_title: str):
    """
    Retrieve all skills and tools required for a specific job title.
    """
    query = """
    MATCH (j:Job) 
    WHERE toLower(j.title) CONTAINS toLower($title)
    OPTIONAL MATCH (j)-[:REQUIRES_SKILL]->(s:Skill)
    OPTIONAL MATCH (j)-[:USES_TOOL]->(t:Tool)
    WITH j, collect(DISTINCT s.name) AS Skills, collect(DISTINCT t.name) AS Tools
    RETURN j.title AS JobTitle, Skills, Tools
    """
    
    with DRIVER.session() as session:
        result = session.run(query, title=job_title).single()
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Job title not found: {job_title}")
            
        return result.data()
