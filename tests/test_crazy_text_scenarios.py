"""Test cases for crazy, complex text parsing scenarios"""
import pytest
from unittest.mock import patch
from src.resume_generator.services.advanced_resume_parser import AdvancedResumeParser
from src.resume_generator.services.resume_update_service import ResumeUpdateService


class TestCrazyTextScenarios:
    """Test the most complex, messy, real-world text scenarios"""
    
    @pytest.fixture
    def parser(self):
        """Create parser with mocked AI client"""
        with patch('src.resume_generator.services.advanced_resume_parser.APIClient'):
            return AdvancedResumeParser()
    
    @pytest.fixture
    def update_service(self):
        """Create update service with mocked dependencies"""
        with patch('src.resume_generator.services.resume_update_service.QdrantClient'), \
             patch('src.resume_generator.services.resume_update_service.VectorSearchClient'), \
             patch('src.resume_generator.services.resume_update_service.APIClient'):
            return ResumeUpdateService()
    
    def test_emoji_rich_linkedin_dump(self, update_service):
        """Test parsing LinkedIn profile dump with emojis and mixed formatting"""
        
        messy_text = """
        Just got promoted to Staff SWE at Google (Alphabet Inc) 🎉
        📧 john.doe.dev@gmail.com | 📱 +1-555-JOHN | LinkedIn: /in/johndoe
        Started as L4 SDE in 2021, now L6. Working on Search Infrastructure.
        Python🐍, Go, K8s, GCP, some ML stuff with TensorFlow
        Previously @ Meta (Facebook) 2019-2021 as SDE II
        Stanford CS '19, GPA 3.8 (Dean's List) 🎓
        Side project: Built TodoApp with React+Node, 10k+ users 🚀
        """
        
        # Mock AI response
        expected_response = """
        {
            "basics": {
                "name": "John Doe",
                "email": "john.doe.dev@gmail.com",
                "phone": "+1-555-JOHN",
                "summary": "Staff Software Engineer at Google with experience in search infrastructure and full-stack development"
            },
            "work": [
                {
                    "company": "Google",
                    "position": "Staff Software Engineer",
                    "startDate": "2021-01-01",
                    "endDate": null,
                    "summary": "Working on Search Infrastructure, promoted from L4 to L6",
                    "highlights": ["Search Infrastructure", "Python", "Go", "Kubernetes", "GCP", "Machine Learning", "TensorFlow"]
                },
                {
                    "company": "Meta",
                    "position": "Software Development Engineer II",
                    "startDate": "2019-01-01",
                    "endDate": "2021-01-01",
                    "summary": "Software development at Meta (formerly Facebook)",
                    "highlights": ["Full-stack development"]
                }
            ],
            "education": [
                {
                    "institution": "Stanford University",
                    "area": "Computer Science",
                    "studyType": "Bachelor",
                    "endDate": "2019-01-01",
                    "gpa": "3.8"
                }
            ],
            "skills": [
                {
                    "name": "Programming Languages",
                    "keywords": ["Python", "Go"]
                },
                {
                    "name": "Technologies",
                    "keywords": ["Kubernetes", "Google Cloud Platform", "TensorFlow", "Machine Learning"]
                }
            ],
            "projects": [
                {
                    "name": "TodoApp",
                    "description": "Built TodoApp with React and Node.js",
                    "highlights": ["React", "Node.js", "10k+ users"]
                }
            ]
        }
        """
        
        # Should detect as complex text
        assert update_service._is_complex_text(messy_text)
        
        # Mock the AI completion
        with patch.object(update_service.advanced_parser.ai_client, 'query') as mock_complete:
            mock_complete.return_value = expected_response
            
            with patch.object(update_service, '_get_existing_resume_context') as mock_context:
                mock_context.return_value = []
                
                result = update_service._parse_text_content(messy_text, None)
                
                # Verify structured output
                assert 'basics' in result
                assert 'work' in result
                assert 'education' in result
                assert 'skills' in result
                assert 'projects' in result
                
                # Verify basic info extraction
                basics = result['basics'][0]
                assert basics['email'] == 'john.doe.dev@gmail.com'
                assert 'Staff Software Engineer' in basics['summary']
    
    def test_conversational_memory_dump(self, update_service):
        """Test casual, conversational resume update"""
        
        casual_text = """
        Oh btw I forgot to mention - did some freelance work between Google and Meta, 
        like 6 months? Helped this YC startup with their backend. Also that bootcamp 
        I did before Stanford - Lambda School, graduated in 2018. And I think my 
        current salary is around 200k but don't put that on resume lol. 
        Recently got AWS certified too, should probably add that.
        """
        
        expected_response = """
        {
            "work": [
                {
                    "company": "YC Startup (Freelance)",
                    "position": "Backend Developer",
                    "startDate": "2021-06-01",
                    "endDate": "2021-12-01",
                    "summary": "Freelance backend development for Y Combinator startup",
                    "highlights": ["Backend development", "Startup experience"]
                }
            ],
            "education": [
                {
                    "institution": "Lambda School",
                    "area": "Software Engineering",
                    "studyType": "Bootcamp",
                    "endDate": "2018-01-01"
                }
            ],
            "skills": [
                {
                    "name": "Certifications",
                    "keywords": ["AWS Certified"]
                }
            ]
        }
        """
        
        # Should detect as complex/conversational
        assert update_service._is_complex_text(casual_text)
        
        with patch.object(update_service.advanced_parser.ai_client, 'query') as mock_complete:
            mock_complete.return_value = expected_response
            
            with patch.object(update_service, '_get_existing_resume_context') as mock_context:
                mock_context.return_value = []
                
                result = update_service._parse_text_content(casual_text, None)
                
                assert 'work' in result
                assert 'education' in result
                assert 'skills' in result
                
                # Should extract freelance work
                work = result['work'][0]
                assert 'YC Startup' in work['company']
                assert 'Freelance' in work['company']
    
    def test_fragmented_context_heavy_dump(self, update_service):
        """Test parsing context-heavy, fragmented information"""
        
        context_text = """
        After the pandemic started, went fully remote from my Seattle office.
        Got promoted twice since then - first to senior, then to staff level.
        The FAANG company where I'm at now has great WLB compared to my previous 
        unicorn (was employee #45). My manager says I'm up for Principal next year.
        Been doing a lot of ML stuff lately - NLP, CV, some LLM fine-tuning.
        """
        
        expected_response = """
        {
            "work": [
                {
                    "company": "FAANG Company",
                    "position": "Staff Software Engineer",
                    "startDate": "2018-01-01",
                    "summary": "Promoted twice during pandemic, working remotely from Seattle office",
                    "highlights": ["Remote work", "Rapid promotion", "Machine Learning", "NLP", "Computer Vision", "LLM fine-tuning"],
                    "location": "Seattle, WA"
                },
                {
                    "company": "Unicorn Startup",
                    "position": "Software Engineer",
                    "startDate": "2017-01-01",
                    "endDate": "2018-01-01",
                    "summary": "Early employee (#45) at unicorn startup",
                    "highlights": ["Early startup employee", "Startup experience"]
                }
            ],
            "skills": [
                {
                    "name": "Machine Learning",
                    "keywords": ["Natural Language Processing", "Computer Vision", "LLM fine-tuning"]
                }
            ]
        }
        """
        
        # Should detect as complex due to context references
        assert update_service._is_complex_text(context_text)
        
        with patch.object(update_service.advanced_parser.ai_client, 'query') as mock_complete:
            mock_complete.return_value = expected_response
            
            with patch.object(update_service, '_get_existing_resume_context') as mock_context:
                mock_context.return_value = []
                
                result = update_service._parse_text_content(context_text, None)
                
                assert 'work' in result
                assert 'skills' in result
                
                # Should infer timeline and context
                current_work = result['work'][0]
                assert 'Staff' in current_work['position']
                assert 'Seattle' in current_work['location']
    
    def test_technical_jargon_abbreviations(self, update_service):
        """Test parsing heavy technical jargon and abbreviations"""
        
        tech_text = """
        Current stack: K8s, TF, AWS Lambda, DDB, some serverless stuff
        Full-stack: MERN + some DevOps (CI/CD pipelines, Docker, etc.)
        Did some NLP/CV work with PyTorch, fine-tuned BERT models
        Also familiar with GCP, Azure, microservices architecture
        Recently started exploring LLMs - built a RAG system with embeddings
        """
        
        expected_response = """
        {
            "skills": [
                {
                    "name": "Cloud & Infrastructure",
                    "keywords": ["Kubernetes", "Terraform", "Amazon Web Services", "AWS Lambda", "DynamoDB", "Serverless", "Docker", "Google Cloud Platform", "Azure"]
                },
                {
                    "name": "Programming & Frameworks",
                    "keywords": ["MongoDB", "Express.js", "React", "Node.js", "MERN Stack"]
                },
                {
                    "name": "Machine Learning",
                    "keywords": ["Natural Language Processing", "Computer Vision", "PyTorch", "BERT", "Large Language Models", "RAG", "Embeddings"]
                },
                {
                    "name": "DevOps",
                    "keywords": ["CI/CD", "DevOps", "Microservices"]
                }
            ]
        }
        """
        
        # Should detect as complex due to abbreviations
        assert update_service._is_complex_text(tech_text)
        
        with patch.object(update_service.advanced_parser.ai_client, 'query') as mock_complete:
            mock_complete.return_value = expected_response
            
            with patch.object(update_service, '_get_existing_resume_context') as mock_context:
                mock_context.return_value = []
                
                result = update_service._parse_text_content(tech_text, None)
                
                assert 'skills' in result
                skills = result['skills']
                
                # Should normalize abbreviations
                cloud_skills = next((s for s in skills if s['name'] == 'Cloud & Infrastructure'), None)
                assert cloud_skills is not None
                assert 'Kubernetes' in cloud_skills['keywords']  # K8s normalized
                assert 'Terraform' in cloud_skills['keywords']   # TF normalized
    
    def test_mixed_timeline_reconstruction(self, update_service):
        """Test timeline reconstruction from fragmented information"""
        
        timeline_text = """
        Started at Google as new grad in 2020. Before that did internship 
        at Microsoft summer 2019. In between Google and current job (Meta), 
        took 3 months off to travel. Been at Meta since early 2022.
        Oh and did some contract work for Netflix in late 2021.
        """
        
        expected_response = """
        {
            "work": [
                {
                    "company": "Meta",
                    "position": "Software Engineer",
                    "startDate": "2022-02-01",
                    "endDate": null,
                    "summary": "Current position at Meta"
                },
                {
                    "company": "Netflix",
                    "position": "Contract Developer",
                    "startDate": "2021-10-01",
                    "endDate": "2021-12-31",
                    "summary": "Contract development work"
                },
                {
                    "company": "Google",
                    "position": "Software Engineer",
                    "startDate": "2020-06-01",
                    "endDate": "2021-09-30",
                    "summary": "New graduate software engineer position"
                },
                {
                    "company": "Microsoft",
                    "position": "Software Engineering Intern",
                    "startDate": "2019-06-01",
                    "endDate": "2019-08-31",
                    "summary": "Summer internship"
                }
            ]
        }
        """
        
        with patch.object(update_service.advanced_parser.ai_client, 'query') as mock_complete:
            mock_complete.return_value = expected_response
            
            with patch.object(update_service, '_get_existing_resume_context') as mock_context:
                mock_context.return_value = []
                
                result = update_service._parse_text_content(timeline_text, None)
                
                assert 'work' in result
                work_entries = result['work']
                
                # Should reconstruct logical timeline
                assert len(work_entries) == 4
                
                # Current job should have no end date
                current_job = next((w for w in work_entries if w['endDate'] is None), None)
                assert current_job is not None
                assert current_job['company'] == 'Meta'
    
    def test_contradictory_information_resolution(self, update_service):
        """Test handling contradictory information intelligently"""
        
        contradiction_text = """
        Actually, I started at Google in 2021, not 2020 like I said before.
        And my title was Senior SWE, not just SWE. The project I mentioned - 
        it wasn't just search, we also worked on ads infrastructure.
        Also my GPA was 3.9, not 3.8. Dean's List all 4 years.
        """
        
        # Mock existing data with contradictory info
        existing_data = [
            {
                'section': 'work',
                'company': 'Google',
                'position': 'Software Engineer',
                'startDate': '2020-01-01',
                'summary': 'Working on search infrastructure'
            },
            {
                'section': 'education',
                'institution': 'Stanford University',
                'gpa': '3.8'
            }
        ]
        
        expected_response = """
        {
            "work": [
                {
                    "company": "Google",
                    "position": "Senior Software Engineer",
                    "startDate": "2021-01-01",
                    "summary": "Working on search and ads infrastructure",
                    "highlights": ["Search infrastructure", "Ads infrastructure"]
                }
            ],
            "education": [
                {
                    "institution": "Stanford University",
                    "gpa": "3.9",
                    "honors": "Dean's List all 4 years"
                }
            ]
        }
        """
        
        with patch.object(update_service.advanced_parser.ai_client, 'query') as mock_complete:
            mock_complete.return_value = expected_response
            
            with patch.object(update_service, '_get_existing_resume_context') as mock_context:
                mock_context.return_value = existing_data
                
                result = update_service._parse_text_content(contradiction_text, None)
                
                assert 'work' in result
                assert 'education' in result
                
                # Should prefer newer, corrected information
                work = result['work'][0]
                assert work['startDate'] == '2021-01-01'  # Corrected date
                assert 'Senior' in work['position']       # Corrected title
                
                education = result['education'][0]
                assert education['gpa'] == '3.9'          # Corrected GPA
    
    def test_pdf_extraction_artifacts(self, update_service):
        """Test handling text with PDF extraction artifacts"""
        
        pdf_artifact_text = """
        John    Doe
        john.doe@email.com    |    555-123-4567
        
        EXPERIENCE
        Software    Engineer          Google    Inc.         2020-2023
        •   Built   scalable   APIs   using   Python   and   Flask
        •   Worked   with   K8s   and   microservices   architecture
        
        EDUCATION
        B.S.   Computer   Science        Stanford   University      2016-2020
        GPA:   3.8/4.0
        """
        
        # Should detect as complex due to spacing artifacts
        assert update_service._is_complex_text(pdf_artifact_text)
        
        # Test preprocessing cleans up the artifacts
        cleaned = update_service.advanced_parser._preprocess_text(pdf_artifact_text)
        
        # Should normalize excessive spacing
        assert 'John Doe' in cleaned
        assert 'john.doe@email.com' in cleaned
        assert not '    ' in cleaned  # Multiple spaces should be cleaned


class TestComplexityDetection:
    """Test the complexity detection logic"""
    
    @pytest.fixture
    def update_service(self):
        """Create update service with mocked dependencies"""
        with patch('src.resume_generator.services.resume_update_service.QdrantClient'), \
             patch('src.resume_generator.services.resume_update_service.VectorSearchClient'), \
             patch('src.resume_generator.services.resume_update_service.APIClient'):
            return ResumeUpdateService()
    
    def test_simple_text_not_complex(self, update_service):
        """Test that simple, clean text is not flagged as complex"""
        
        simple_texts = [
            "John Doe, Software Engineer with 5 years experience in Python development",
            "Worked at Google from 2020 to 2023 as a Senior Software Engineer",
            "Skills include Python, JavaScript, React, and Node.js",
            "Bachelor of Science in Computer Science from Stanford University"
        ]
        
        for text in simple_texts:
            assert not update_service._is_complex_text(text), f"Incorrectly flagged as complex: {text}"
    
    def test_complex_indicators_detected(self, update_service):
        """Test that various complexity indicators are properly detected"""
        
        complex_texts = [
            # Emojis
            "Just got promoted! 🎉 Now Senior SWE at Google",
            
            # Casual language
            "btw forgot to mention my side project lol",
            
            # Tech abbreviations
            "Current stack: K8s, TF, AWS, some ML stuff",
            
            # Industry jargon
            "Joined this unicorn startup as employee #50",
            
            # Casual timeline
            "Been remote since the pandemic started",
            
            # Mixed formatting
            "Name: John | Email: john@email.com | Phone: 555-1234",
            
            # Multiple companies
            "Previously at Google, now at Meta, considering Amazon",
            
            # Educational + work context
            "Stanford CS '20, now SWE at Google with 3.9 GPA"
        ]
        
        for text in complex_texts:
            assert update_service._is_complex_text(text), f"Failed to detect complexity: {text}"


class TestEntityNormalization:
    """Test entity recognition and normalization"""
    
    @pytest.fixture
    def parser(self):
        """Create parser with mocked AI client"""
        with patch('src.resume_generator.services.advanced_resume_parser.APIClient'):
            return AdvancedResumeParser()
    
    def test_company_name_normalization(self, parser):
        """Test company name aliases are properly normalized"""
        
        test_text = "Worked at Alphabet Inc, then moved to Meta Platforms, now at MSFT"
        entities = parser._extract_and_normalize_entities(test_text)
        
        companies = entities['companies']
        assert 'Google' in companies      # Alphabet Inc -> Google
        assert 'Meta' in companies        # Meta Platforms -> Meta  
        assert 'Microsoft' in companies   # MSFT -> Microsoft
    
    def test_technology_abbreviation_expansion(self, parser):
        """Test technology abbreviations are expanded"""
        
        test_text = "Experience with K8s, TF, and some ML/AI work using PyTorch"
        entities = parser._extract_and_normalize_entities(test_text)
        
        technologies = entities['technologies']
        assert 'Kubernetes' in technologies       # K8s -> Kubernetes
        assert 'Terraform' in technologies        # TF -> Terraform
        assert 'Machine Learning' in technologies # ML -> Machine Learning
        assert 'Artificial Intelligence' in technologies # AI -> Artificial Intelligence
    
    def test_location_normalization(self, parser):
        """Test location aliases are normalized"""
        
        test_text = "Based in SF, previously in NYC, considering Seattle area"
        entities = parser._extract_and_normalize_entities(test_text)
        
        locations = entities['locations']
        assert 'San Francisco' in locations  # SF -> San Francisco
        assert 'New York' in locations       # NYC -> New York
        assert 'Seattle' in locations        # Seattle area -> Seattle
    
    def test_contact_extraction(self, parser):
        """Test contact information extraction"""
        
        test_text = "Contact me at john.doe@gmail.com or +1-555-123-4567"
        entities = parser._extract_and_normalize_entities(test_text)
        
        assert 'john.doe@gmail.com' in entities['emails']
        assert any('555-123-4567' in phone for phone in entities['phones'])