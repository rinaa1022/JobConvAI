# ConvAgent - Intelligent Job Matching Platform

An AI-powered platform that analyzes resumes and job postings to provide intelligent job matching recommendations.

## 🏗️ Architecture

```
ConvAgent/
├── ResumeParser/          # Resume analysis and parsing module
│   ├── src/               # Core resume parsing code
         ├── app.py
         ├── neo4j_manager.py
         ├── resume_parser.py
         ├── resume_schema.py
│   ├── tests/             # Resume parsing tests
│   ├── docs/              # Resume parser documentation
│   └── main.py            # Resume parser standalone app
├── JobParser/             # Job fetching and parsing module
    ├── src/               # Core resume parsing code
         ├── jd_parser.py
         ├── jd_to_neo4j.py
         ├── jobs_api.py
         ├── run_pipeline.py
│   └── data               # Job descriptions
├── main_app.py            # Unified application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## 🚀 Features

### Resume Analysis
- **Multi-format Support**: PDF, DOCX, TXT files
- **AI-powered Parsing**: Uses OpenAI, Anthropic, or Google AI
- **Skill Extraction**: Identifies technical and soft skills
- **Experience Analysis**: Parses work history and education
- **Knowledge Graph**: Stores structured resume data in Neo4j

### Job Search & Analysis
- **Multiple APIs**: Adzuna, GitHub Jobs, RemoteOK
- **Intelligent Parsing**: Extracts skills, requirements, benefits
- **Job Classification**: Categorizes by industry, level, type
- **Knowledge Graph**: Stores job data with relationships

### Intelligent Matching
- **Skill-based Matching**: Matches resumes to jobs by skills
- **Scoring Algorithm**: Ranks matches by skill overlap
- **Recommendations**: Suggests job improvements and skill gaps
- **Analytics Dashboard**: Market trends and skill demand

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ConvAgent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Neo4j**
   - Install Neo4j Desktop
   - Create a new database
   - Note the connection details

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and Neo4j credentials
   ```

## 🎯 Usage

### Run the Unified Application
```bash
python run_matching.py
```

### Run Individual Modules

**Resume Parser Only:**
```bash
cd ResumeParser
python main.py
```

**Job Parser Only:**
```bash
cd JobParser/src
python run_pipeline.py
```

# Initialize job parser
job_parser = JobParser(neo4j_uri, neo4j_user, neo4j_password)

# Fetch and parse jobs
jobs = job_parser.fetch_and_parse_jobs("Python Developer", "New York", 50)

# Save to database
job_parser.save_jobs_to_neo4j(jobs)
```

## 🔧 Configuration

### Environment Variables
```env
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# API Keys (optional)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key

# Job APIs (optional)
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key
```

### Job API Setup

**Adzuna (Recommended)**
1. Sign up at https://developer.adzuna.com/
2. Get your App ID and App Key
3. Add to environment variables

**GitHub Jobs**
- No API key required (uses archived data)

**RemoteOK**
- No API key required

## 📊 Knowledge Graph Schema

### Resume Entities
- **Resume**: Personal information and summary
- **Person**: Individual with skills and experience
- **Company**: Work experience companies
- **Position**: Job positions held
- **Skill**: Technical and soft skills
- **Education**: Educational background
- **Project**: Personal projects

### Job Entities
- **Job**: Job posting details
- **Company**: Hiring companies
- **Position**: Job positions available
- **Skill**: Required skills
- **Location**: Job locations
- **SalaryRange**: Compensation information
- **Requirement**: Job requirements
- **Benefit**: Job benefits

### Relationships
- `HAS_SKILL`: Person/Job → Skill
- `REQUIRES_SKILL`: Position → Skill
- `WORKS_AT`: Person → Company
- `OFFERS_POSITION`: Company → Job
- `LOCATED_IN`: Job → Location

## 🔍 API Reference

### Resume Parser
```python
from ResumeParser.src.resume_parser import ResumeParser

parser = ResumeParser(api_key="your_key", provider="openai")
resume_data = parser.parse_resume("resume.pdf")
```

### Job Parser
```python
from JobParser.job_parser import JobParser

job_parser = JobParser(neo4j_uri, neo4j_user, neo4j_password)
jobs = job_parser.fetch_and_parse_jobs("Data Scientist", limit=50)
```

### Job Matching
```python
# Find job matches for resume skills
matches = job_parser.get_job_matches_for_resume(resume_skills, limit=10)
```

## 📈 Analytics

The platform provides insights into:
- **Skill Demand**: Most in-demand skills in job market
- **Market Trends**: Salary ranges and job availability
- **Skill Gaps**: Missing skills for target jobs
- **Match Quality**: Resume-job compatibility scores

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Neo4j for graph database
- Streamlit for web interface
- OpenAI, Anthropic, Google for AI capabilities
- Adzuna, GitHub Jobs, RemoteOK for job data

## 📞 Support

For questions or support, please open an issue on GitHub.


