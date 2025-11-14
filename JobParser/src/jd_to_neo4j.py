from neo4j import GraphDatabase
from dotenv import load_dotenv
from typing import Dict, Any, List
import os
import uuid

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD")

if not NEO4J_PASS:
    raise RuntimeError("Set NEO4J_PASSWORD in .env file")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def create_job_graph(job_json: Dict[str, Any]) -> None:
    """
    Takes a parsed job description dictionary and creates a full graph structure.
    Accepts keys from ParsedJobDescription as-is.
    """

    params = {
        "job_id": job_json.get("job_id") or str(uuid.uuid4()),
        "title": job_json.get("job_title") or "Untitled Role",
        "company": (job_json.get("company") or "Unknown Company"),
        "location": (job_json.get("location") or "Unknown"),
        "employment_type": job_json.get("employment_type") or "Not specified",
        "experience_required": job_json.get("experience_required") or "Not specified",
        "salary_range": job_json.get("salary_range") or "Not specified",
    }

    #fixed --> List[str]
    skills: List[str] = job_json.get("skills_required") or []
    certs: List[str] = job_json.get("certifications_required") or []
    education: List[str] = job_json.get("education_required") or []
    tools: List[str] = job_json.get("tools_and_technologies") or []
    responsibilities: List[str] = job_json.get("responsibilities") or []

    with driver.session() as session:
        session.run("""
            MERGE (j:Job {id:$job_id})
            SET j.title = $title,
                j.employment_type = $employment_type,
                j.experience_required = $experience_required,
                j.salary_range = $salary_range
        """, **params)

        # Company (skip null/empty)
        session.run("""
            MATCH (j:Job {id: $job_id})
            FOREACH (_ IN CASE WHEN $company IS NULL OR $company = '' THEN [] ELSE [1] END |
                MERGE (c:Company {name: $company})
                MERGE (c)-[:POSTS]->(j)
            )
        """, job_id=params["job_id"], company=params["company"])

        # Location (skip null/empty)
        session.run("""
            MATCH (j:Job {id: $job_id})
            FOREACH (_ IN CASE WHEN $location IS NULL OR $location = '' THEN [] ELSE [1] END |
                MERGE (l:Location {name: $location})
                MERGE (j)-[:LOCATED_AT]->(l)
            )
        """, job_id=params["job_id"], location=params["location"])

        for skill in skills:
            if not skill:
                continue
            session.run("""
                MATCH (j:Job {id:$job_id})
                MERGE (s:Skill {name:$skill_name})
                MERGE (j)-[:REQUIRES_SKILL]->(s)
            """, job_id=params["job_id"], skill_name=skill)

        for cert in certs:
            if not cert:
                continue
            session.run("""
                MATCH (j:Job {id:$job_id})
                MERGE (c:Certification {name:$cert_name})
                MERGE (j)-[:REQUIRES_CERT]->(c)
            """, job_id=params["job_id"], cert_name=cert)

        for edu in education:
            if not edu:
                continue
            session.run("""
                MATCH (j:Job {id:$job_id})
                MERGE (e:Education {name:$edu_name})
                MERGE (j)-[:REQUIRES_EDU]->(e)
            """, job_id=params["job_id"], edu_name=edu)

        for t in tools:
            if not t:
                continue
            session.run("""
                MATCH (j:Job {id:$job_id})
                MERGE (t:Tool {name:$tool_name})
                MERGE (j)-[:USES_TOOL]->(t)
            """, job_id=params["job_id"], tool_name=t)

        for r in responsibilities:
            if not r:
                continue
            session.run("""
                MATCH (j:Job {id:$job_id})
                MERGE (resp:Responsibility {desc:$desc_text})
                MERGE (j)-[:HAS_RESPONSIBILITY]->(resp)
            """, job_id=params["job_id"], desc_text=r)

    print(f"Created/Merged Job node (id={params['job_id']}) title='{params['title']}'")
