# run_matching.py
from matching import get_top_job_matches_for_resume, driver

# 👈 put the resume ID you saw in Neo4j here
RESUME_ID = "8807753d-12c4-460b-a104-fe35b229f904"


def list_resumes():
    """Show some resumes in the DB so you can confirm the ID."""
    with driver.session() as session:
        result = session.run("""
            MATCH (r:Resume)
            RETURN r.id AS id, r.name AS name, r.email AS email
            LIMIT 10
        """)
        return [record.data() for record in result]


if __name__ == "__main__":
    print("=== Resumes currently in Neo4j ===")
    resumes = list_resumes()
    if not resumes:
        print("No Resume nodes found! Upload/parse a resume first.")
    else:
        for r in resumes:
            print(f"- id={r['id']} | name={r.get('name')} | email={r.get('email')}")

    print(f"\n=== Looking for matches for RESUME_ID = {RESUME_ID} ===")

    matches = get_top_job_matches_for_resume(RESUME_ID, limit=5)
    print(f"Found {len(matches)} matching jobs.\n")

    if not matches:
        print("No job matches found. Possible reasons:")
        print(" - The resume id is wrong or not in this database")
        print(" - There are Job nodes but they have no REQUIRES_SKILL edges")
        print(" - Resume skills and job skills do not overlap")
    else:
        for m in matches:
            print("------------------------------------------------")
            print(f"{m['title']} at {m['company']} ({m['location']})")
            print(f"Employment type: {m['employment_type']}")
            print(
                f"Skill overlap: {m['matching_skill_count']}/"
                f"{m['total_skill_required']} "
                f"({m['coverage']:.2f} coverage)"
            )
            print("Matching skills:", ", ".join(m['matching_skills']))
