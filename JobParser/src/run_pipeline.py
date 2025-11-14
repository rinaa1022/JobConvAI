from pathlib import Path
from jd_parser import parse_jd_file
from jd_to_neo4j import create_job_graph
import json
import sys

# Directory where your JD .txt files live
data_dir = Path(__file__).parent.parent / "data"

# Take file names from command line: python script.py jd1.txt jd2.txt jd3.txt
# If none are given, fall back to sample_jd.txt
jd_filenames = sys.argv[1:] or ["sample_jd.txt"]

for filename in jd_filenames:
    jd_path = data_dir / filename

    if not jd_path.exists():
        print(f"[WARN] File not found, skipping: {jd_path}")
        continue

    print(f"\n=== Processing: {jd_path.name} ===")
    print("Parsing JD -> JSON ...")
    parsed = parse_jd_file(str(jd_path))

    print("Parsed JSON:")
    print(json.dumps(parsed, indent=2))

    print("\nPushing to Neo4j ...")
    create_job_graph(parsed)
    print("Done.")

print("\nAll requested files processed.")
