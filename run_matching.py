import argparse
from matching import get_top_job_matches_for_resume, driver

def list_resumes(limit: int = 25):
    q = """
    MATCH (r:Resume)
    OPTIONAL MATCH (r)-[hs:HAS_SKILL]->(:Skill)
    WITH r, count(hs) AS skill_count
    RETURN r.id AS id, r.name AS name, r.email AS email, skill_count
    ORDER BY coalesce(r.name, ''), coalesce(r.email, ''), coalesce(r.id, '')
    LIMIT $limit
    """
    with driver.session() as session:
        result = session.run(q, limit=limit)
        return [record.data() for record in result]

def print_resumes():
    rows = list_resumes()
    print("=== Resumes currently in Neo4j ===")
    if not rows:
        print("No Resume nodes found! Upload/parse a resume first.")
        return
    for r in rows:
        created = r.get("created")
        created_str = str(created) if created else "N/A"
        print(f"- id={r['id']} | name={r.get('name')} | email={r.get('email')}")

def get_resume_id_by_email(email: str):
    q = "MATCH (r:Resume {email: $email}) RETURN r.id AS id LIMIT 1"
    with driver.session() as session:
        rec = session.run(q, email=email).single()
        return rec["id"] if rec else None

def get_latest_resume_id():
    q = """
    MATCH (r:Resume)
    RETURN r.id AS id
    ORDER BY coalesce(r.created, datetime({epochMillis:0})) DESC
    LIMIT 1
    """
    with driver.session() as session:
        rec = session.run(q).single()
        return rec["id"] if rec else None

def main():
    ap = argparse.ArgumentParser(description="Find top job matches for a resume.")
    ap.add_argument("--email", help="Resume owner email to look up (preferred)")
    ap.add_argument("--resume-id", help="Resume node id (overrides --email)")
    ap.add_argument("--limit", type=int, default=5, help="How many matches to return")
    args = ap.parse_args()

    # Always print resume list (your requested behavior)
    print_resumes()
    print()

    # Resolve resume_id
    if args.resume_id:
        resume_id = args.resume_id
    elif args.email:
        resume_id = get_resume_id_by_email(args.email)
        if not resume_id:
            print(f"No resume found for email: {args.email}")
            return
    else:
        resume_id = get_latest_resume_id()
        if not resume_id:
            print("No Resume nodes found! Upload/parse a resume first.")
            return

    print(f"=== Looking for matches for RESUME_ID = {resume_id} ===")
    matches = get_top_job_matches_for_resume(resume_id, limit=args.limit)
    print(f"Found {len(matches)} matching jobs.\n")

    if not matches:
        print("No job matches found. Possible reasons:")
        print(" - The resume id is wrong or not in this database")
        print(" - There are Job nodes but they have no REQUIRES_SKILL edges")
        print(" - Resume skills and job skills do not overlap")
        return

    for m in matches:
        print("------------------------------------------------")
        title = m.get("title") or "Untitled"
        company = m.get("company") or "Unknown"
        location = m.get("location") or "Unknown"
        emp_type = m.get("employment_type") or "Not specified"
        overlap = m.get("matching_skill_count", 0)
        total = m.get("total_skill_required", 0)
        coverage = m.get("coverage", 0.0)
        skills = m.get("matching_skills") or []
        print(f"{title} at {company} ({location})")
        print(f"Employment type: {emp_type}")
        print(f"Skill overlap: {overlap}/{total} ({coverage:.2f} coverage)")
        print("Matching skills:", ", ".join(skills) if skills else "(none)")

if __name__ == "__main__":
    main()
