from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def get_top_job_matches_for_resume(resume_id: str, limit: int = 5):
    query = """
    // 1) Take the resume's skills and split comma-separated strings
    MATCH (r:Resume {id: $resume_id})-[:HAS_SKILL]->(rs:Skill)
    UNWIND split(rs.name, ",") AS rawSkill
    WITH DISTINCT trim(rawSkill) AS resume_skill_name

    // 2) Match jobs that require any of those skills
    MATCH (j:Job)-[:REQUIRES_SKILL]->(js:Skill)
    WHERE toLower(js.name) = toLower(resume_skill_name)

    OPTIONAL MATCH (j)<-[:POSTS]-(c:Company)
    OPTIONAL MATCH (j)-[:LOCATED_AT]->(l:Location)

    WITH j, c, l,
         collect(DISTINCT js.name) AS matching_skills,
         count(DISTINCT js.name)   AS skill_overlap

    // 3) Count total skills required by each job
    MATCH (j)-[:REQUIRES_SKILL]->(all_s:Skill)
    WITH j, c, l, matching_skills, skill_overlap,
         count(DISTINCT all_s) AS total_required

    WITH j, c, l, matching_skills, skill_overlap, total_required,
         CASE
             WHEN total_required = 0 THEN 0.0
             ELSE toFloat(skill_overlap) / total_required
         END AS coverage

    ORDER BY skill_overlap DESC, coverage DESC, j.title
    LIMIT $limit

    RETURN
        j.id                             AS job_id,
        j.title                          AS title,
        coalesce(c.name, "Unknown")      AS company,
        coalesce(l.name, "Unknown")      AS location,
        coalesce(j.employment_type, "Not specified") AS employment_type,
        matching_skills                  AS matching_skills,
        skill_overlap                    AS matching_skill_count,
        total_required                   AS total_skill_required,
        coverage                         AS coverage,
        skill_overlap                    AS score
    """

    with driver.session() as session:
        result = session.run(query, resume_id=resume_id, limit=limit)
        matches = [record.data() for record in result]

    return matches
