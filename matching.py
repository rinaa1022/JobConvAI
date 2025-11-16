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
    // 1) Resume skills -> split comma list into individual names
    MATCH (resume:Resume {id: $resume_id})-[:HAS_SKILL]->(resumeSkillNode:Skill)
    UNWIND split(resumeSkillNode.name, ",") AS rawSkill
    WITH DISTINCT trim(rawSkill) AS resumeSkill
    WHERE resumeSkill <> ""

    // 2) Jobs that require any of those skills (join by name, case-insensitive)
    MATCH (job:Job)-[:REQUIRES_SKILL]->(jobSkill:Skill)
    WHERE toLower(jobSkill.name) = toLower(resumeSkill)

    OPTIONAL MATCH (job)<-[:POSTS]-(company:Company)
    OPTIONAL MATCH (job)-[:LOCATED_AT]->(location:Location)

    WITH job, company, location,
         collect(DISTINCT jobSkill.name) AS matching_skills,
         count(DISTINCT jobSkill)        AS skill_overlap

    // 3) Total skills required by the job
    MATCH (job)-[:REQUIRES_SKILL]->(allJobSkill:Skill)
    WITH job, company, location, matching_skills, skill_overlap,
         count(DISTINCT allJobSkill) AS total_required

    WITH job, company, location, matching_skills, skill_overlap, total_required,
         CASE WHEN total_required = 0
              THEN 0.0
              ELSE toFloat(skill_overlap) / total_required
         END AS coverage

    ORDER BY skill_overlap DESC, coverage DESC, job.title
    LIMIT $limit

    RETURN
        job.id                               AS job_id,
        job.title                            AS title,
        coalesce(company.name,  "Unknown")   AS company,
        coalesce(location.name, "Unknown")   AS location,
        coalesce(job.employment_type, "Not specified") AS employment_type,
        matching_skills                      AS matching_skills,
        skill_overlap                        AS matching_skill_count,
        total_required                       AS total_skill_required,
        coverage                             AS coverage,
        skill_overlap                        AS score
    """

    with driver.session() as session:
        result = session.run(query, resume_id=resume_id, limit=limit)
        matches = [record.data() for record in result]

    return matches
