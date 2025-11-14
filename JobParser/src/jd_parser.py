import json
from pathlib import Path
from typing import Any, Dict
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv

# Load .env so OPENAI_API_KEY is visible
load_dotenv()
client = OpenAI()  # reads OPENAI_API_KEY from env

class ParsedJobDescription(BaseModel):
    job_title: str = Field(description="The primary title of the job, e.g., 'Software Engineer'.")
    company: str = Field(description="The name of the company posting the job.")
    location: str = Field(description="The city, state, or 'Remote' for the job.")
    employment_type: str = Field(description="The type of employment, e.g., 'Full-time', 'Contract', 'Hybrid'.")
    experience_required: str = Field(description="The minimum years of experience required, e.g., '1+ years' or 'Not specified'.")
    salary_range: str = Field(description="The salary or compensation range, e.g., '$102,000 - $163,000 USD'.")
    education_required: list[str] = Field(description="A list of required degrees or certifications.")
    certifications_required: list[str] = Field(description="A list of professional certifications mentioned.")
    skills_required: list[str] = Field(description="A list of all technical skills/languages mentioned (e.g., Python, Java, React).")
    tools_and_technologies: list[str] = Field(description="A list of specific software/tools (e.g., Docker, Kubernetes).")
    responsibilities: list[str] = Field(description="A list of key duties extracted as bullet points or short phrases.")

SCHEMA_JSON = ParsedJobDescription.model_json_schema()
SCHEMA_JSON["additionalProperties"] = False

SYSTEM_PROMPT = (
    "You are an expert HR data parser. Extract ALL required entities from the following "
    "job description and return ONLY a JSON object that conforms exactly to the provided schema. "
    "If a field is missing, infer if reasonable, otherwise use 'Not specified' or an empty list. "
    "Do not include any text outside the JSON."
)

def parse_jd_file(file_path: str) -> dict:
    """Reads a job description from a file and sends it to the OpenAI API for parsing."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")

    try:
        job_desc_text = path.read_text(encoding="utf-8")
    except Exception as e:
        raise IOError(f"An error occurred while reading the file: {e}")

    try:
        # OpenAI Responses API with structured output via text.format
        response = client.responses.create(
            model="gpt-4o-mini",
            input=f"{SYSTEM_PROMPT}\n\nHere is the job description:\n\n{job_desc_text}",
            text={
                "format": {
                    "type": "json_schema",
                    "name": "ParsedJobDescription",  # label
                    "schema": SCHEMA_JSON            # MUST be a dict
                }
            },
            max_output_tokens=1200  # Responses API uses max_output_tokens
        )

        json_text = response.output_text
        json_data = json.loads(json_text)

        validated = ParsedJobDescription.model_validate(json_data)
        return validated.model_dump()

    except ValidationError as e:
        return {"error": "Validation Failed", "details": str(e)}
    except Exception as e:
        return {"error": "API Call Failed", "details": str(e)}

if __name__ == "__main__":
    sample_file = Path(__file__).parent.parent / "data" / "sample_jd.txt"
    parsed = parse_jd_file(str(sample_file))
    print(json.dumps(parsed, indent=2))
