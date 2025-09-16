import os
import sys
import json
import logging
import time
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from database import init_db, get_roles, add_role
from resume_analysis_helpers import (
    analyze_profile_strength, generate_career_recommendations,
    identify_skill_gaps, calculate_role_matches,
    generate_actionable_insights, generate_overall_assessment
)
from professional_resume_analyzer import (
    extract_detailed_achievements, extract_detailed_projects, extract_internships,
    analyze_work_impact, extract_leadership_experience, generate_professional_summary
)

import psycopg2

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables from .env file
load_dotenv()

# Define paths for structured project
BACKEND_PATH = os.path.dirname(os.path.abspath(__file__))
FRONTEND_PATH = os.path.abspath(os.path.join(BACKEND_PATH, '..', 'frontend'))

# Correct Flask app initialization for structured folders
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app, origins=['http://localhost:5000', 'http://127.0.0.1:5000'])

# Database setup
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Gemini API Key (stored securely on the backend)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBvOkBwL7iMx9zF8nE3qR2sT5uY7wX1cV4")

# Simple API Key for backend access
API_KEY = os.getenv("BACKEND_API_KEY")

# UPDATED SYNONYMS
SYNONYMS = {
    'js': 'javascript',
    'node': 'nodejs',
    'node.js': 'nodejs',
    'react.js': 'react',
    'reactjs': 'react',
    'py': 'python',
    'ml': 'machine learning',
    'dl': 'deep learning',
    'sql': 'sql',
    'postgres': 'postgresql',
    'gcp': 'google cloud',
    'aws': 'amazon web services',
    'html5': 'html',
    'css3': 'css',
    # Non-Tech Additions
    'poli sci': 'indian polity & constitution',
    'polity': 'indian polity & constitution',
    'eco': 'economics & social development',
    'geography': 'geography',
    'history': 'modern indian history',
    'sales': 'business development representative / sales',
    'pr': 'brand / pr specialist',
    'hr': 'learning & development (l&d) specialist'
}

# --- Helper Functions ---
# In app.py
# In app.py, replace the whole function with this:

def normalize_skills(text):
    # First, split by comma, then strip whitespace from each skill
    skills = [s.strip() for s in text.lower().split(',')]
    # Normalize synonyms and remove any empty strings
    return list(set(
        SYNONYMS.get(skill, skill)
        for skill in skills if skill
    )) # <-- Corrected line with closing parentheses

def score_role(user_skills, role):
    required = role.get('requiredSkills', [])
    total_weight = sum(item.get('weight', 1) for item in required)
    matched_weight = 0
    matched_list = []
    missing_skills = []

    normalized_required = [SYNONYMS.get(item['skill'].lower(), item['skill'].lower()) for item in required]

    for item in required:
        skill = SYNONYMS.get(item['skill'].lower(), item['skill'].lower())
        if skill in user_skills:
            matched_weight += item.get('weight', 1)
            matched_list.append(item['skill'])
        else:
            missing_skills.append(item['skill'])

    score = round((matched_weight / total_weight) * 100, 2) if total_weight else 0
    return { 'score': score, 'matchedList': matched_list, 'missing': missing_skills }

def plan_for_gaps(gaps):
    plan = {
        'week1': 'Focus on foundational skills. Aim to spend 60-90 minutes daily on learning and practice.',
        'week2': 'Start a mini-project to apply your new skills. This will help you build a portfolio.'
    }
    return plan

# UPDATED RESOURCES
def resources_for_skill(skill):
    s = skill.lower()
    links = {
        'python': [
            {'title': 'Google: Crash Course on Python', 'url': 'https://grow.google/certificates/python/'},
            {'title': 'freeCodeCamp: Python', 'url': 'https://www.freecodecamp.org/learn/'}
        ],
        'sql': [
            {'title': 'Mode SQL Tutorial', 'url': 'https://mode.com/sql-tutorial/'},
            {'title': 'Kaggle: Intro to SQL', 'url': 'https://www.kaggle.com/learn/intro-to-sql'}
        ],
        'javascript': [
            {'title': 'MDN Web Docs: JavaScript Guide', 'url': 'https://developer.mozilla.org/docs/Web/JavaScript/Guide'}
        ],
        'react': [
            {'title': 'React Official Docs (Tutorial)', 'url': 'https://react.dev/learn'}
        ],
        'google cloud': [
            {'title': 'Google Cloud Skills Boost', 'url': 'https://www.cloudskillsboost.google/'}
        ],
        # Civil Services & Non-Tech Additions
        'indian polity & constitution': [
            {'title': 'Vision IAS: Indian Polity Notes', 'url': 'https://visionias.in/resources/'},
            {'title': 'Book: Indian Polity by M. Laxmikanth', 'url': 'https://www.amazon.in/Indian-Polity-M-Laxmikanth/dp/9352603630'}
        ],
        'current affairs': [
            {'title': 'The Hindu - Newspaper', 'url': 'https://www.thehindu.com/'},
            {'title': 'Insights on India - Daily Current Affairs', 'url': 'https://www.insightsonindia.com/current-affairs/'}
        ],
        'financial modeling': [
            {'title': 'Coursera: Business and Financial Modeling', 'url': 'https://www.coursera.org/specializations/wharton-business-financial-modeling'}
        ],
        'brand strategy': [
            {'title': 'HubSpot Academy: Brand Building', 'url': 'https://academy.hubspot.com/courses/brand-building'}
        ],
        'general studies': [
            {'title': 'NCERT Books Online', 'url': 'https://ncert.nic.in/textbook.php'},
            {'title': 'Vision IAS: General Studies Notes', 'url': 'https://visionias.in/resources/'}
        ],
        'banking awareness': [
            {'title': 'Bankersadda: Banking Awareness', 'url': 'https://www.bankersadda.com/'},
            {'title': 'Oliveboard: Banking Knowledge', 'url': 'https://www.oliveboard.in/'}
        ],
        'quantitative aptitude': [
            {'title': 'IndiaBix: Quantitative Aptitude', 'url': 'https://www.indiabix.com/aptitude/questions-and-answers/'},
            {'title': 'Khan Academy: Math', 'url': 'https://www.khanacademy.org/math'}
        ]
    }
    # Fallback for skills without specific links
    return links.get(s, [{'title': f'Search for "{skill}" courses on Coursera/Udemy', 'url': 'https://www.coursera.org/'}])

def format_professional_response(response):
    """Format AI response for better readability and professionalism"""
    if not response:
        return response
    
    # Clean up common formatting issues
    response = response.strip()
    
    # Ensure proper spacing after bullet points
    response = response.replace('•', '\n• ')
    response = response.replace('*', '\n• ')
    
    # Clean up multiple newlines
    import re
    response = re.sub(r'\n\s*\n\s*\n', '\n\n', response)
    
    return response

def get_gemini_response(prompt, max_tokens=500, temperature=0.7):
    """Enhanced Gemini API function with professional response formatting"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here" or len(api_key) < 20:
        return get_enhanced_fallback_response(prompt)
    
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    
    # Enhanced payload with professional response guidelines
    enhanced_prompt = f"""{prompt}

Please provide a professional, well-structured response that:
- Uses clear, concise language
- Provides specific, actionable advice
- Includes relevant examples where appropriate
- Maintains a helpful and encouraging tone
- Formats information in an organized manner
- Avoids unnecessary filler words or phrases"""
    
    payload = {
        "contents": [{"parts": [{"text": enhanced_prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": max_tokens,
            "stopSequences": [],
            "candidateCount": 1
        },
        "safetySettings": [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
    }

    try:
        response = requests.post(endpoint, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if 'candidates' in data and data['candidates']:
            content = data['candidates'][0].get('content', {})
            parts = content.get('parts', [])
            if parts:
                raw_response = parts[0].get('text', 'No response generated.')
                # Post-process response for better formatting
                return format_professional_response(raw_response)
        
        return get_enhanced_fallback_response(prompt)
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            app.logger.warning("Rate limit hit, using fallback response")
            return get_enhanced_fallback_response(prompt)
        app.logger.error(f"Gemini API HTTP error: {e}")
        return get_enhanced_fallback_response(prompt)
    except Exception as e:
        app.logger.error(f"Gemini API call failed: {e}")
        return get_enhanced_fallback_response(prompt)

def is_gemini_available():
    """Utility: determine if Gemini API key is configured and likely valid."""
    api_key = os.getenv("GEMINI_API_KEY")
    return bool(api_key and api_key != "your_gemini_api_key_here" and len(api_key) > 20)

def generate_skill_based_advice(user_skills, top_role, gaps, career_type='tech'):
    """Deterministic, local advice generator when Gemini is unavailable.
    Builds a concise plan based on user's skills, target role's missing skills, and career type.
    """
    strengths = user_skills[:5] if user_skills else []
    missing = gaps[:5] if gaps else []

    # Build resources for top missing skills
    resources = []
    for sk in missing[:3]:
        resources.append({
            'skill': sk,
            'links': resources_for_skill(sk)
        })

    # 30-60-90 day plan
    if career_type == 'government':
        plan_30 = "Build GS foundation (NCERTs 6-12), start daily current affairs, and schedule weekly mock tests."
        plan_60 = "Choose optional, begin structured notes, and practice answer writing 3x/week."
        plan_90 = "Full-length mocks, revise weak areas, and start interview preparation (communication, bio)."
    elif career_type == 'nontech':
        plan_30 = "Complete one certification aligned to target role and document achievements."
        plan_60 = "Execute a portfolio-worthy mini project; expand network (2 calls/week)."
        plan_90 = "Target 10 quality applications with tailored resumes; prepare STAR stories."
    else:
        plan_30 = "Cover fundamentals and one missing technology; solve 20-30 targeted problems."
        plan_60 = "Build a focused project showcasing missing skills; write a concise README."
        plan_90 = "Refactor and deploy; prepare interview topics and mock interviews."

    lines = []
    role_title = top_role['title'] if isinstance(top_role, dict) and top_role.get('title') else 'Target Role'
    lines.append(f"Recommended plan for {role_title}")
    if strengths:
        lines.append("\nStrengths to leverage:")
        for s in strengths[:5]:
            lines.append(f"• {s.title()}")
    if missing:
        lines.append("\nPriority skill gaps:")
        for m in missing[:5]:
            lines.append(f"• {m}")
    if resources:
        lines.append("\nFocused resources:")
        for r in resources:
            first = r['links'][0] if r['links'] else None
            if first:
                lines.append(f"• {r['skill']}: {first.get('title','Resource')} - {first.get('url','')}")
    lines.append("\n30-60-90 day roadmap:")
    lines.append(f"• Days 1-30: {plan_30}")
    lines.append(f"• Days 31-60: {plan_60}")
    lines.append(f"• Days 61-90: {plan_90}")
    lines.append("\nNext steps:")
    lines.append("• Block 60-90 mins daily; track progress weekly.")
    lines.append("• Build/Update resume with project outcomes and metrics.")
    lines.append("• Schedule mock interviews or peer reviews.")

    return "\n".join(lines)

def simple_chat_engine(message, context=None):
    """[FIXED] Local, conversational engine with better general responses."""
    ctx = context or {}
    career_type = ctx.get('careerType', 'tech')
    skills = ctx.get('skills', [])
    lower = message.lower().strip()

    if not lower:
        return "Could you please repeat that?"

    # General conversation handlers
    if any(g in lower for g in ["hello", "hi", "hey"]):
        return "Hello there! How can I help you with your career goals today? You can also ask me general questions."
    if any(q in lower for q in ["who are you", "what are you"]):
        return "I'm CareerPath AI, a friendly assistant designed to help you with career advice, learning paths, and more."
    if any(j in lower for j in ["joke", "funny"]):
        return "Why don't scientists trust atoms? Because they make up everything!"

    # Career-specific handlers
    if any(k in lower for k in ["career", "job", "role", "path", "opportunity"]):
        reply = ["Thinking about your career is a great step! Based on your profile:"]
        if skills:
            reply.append(f"• Your skills in {', '.join(skills[:3])} are a strong asset.")
        if career_type == 'government':
            reply.append("• For government roles, consistency in preparation is key. Focus on mastering the syllabus for your target exam (UPSC, SSC, etc.) and stay updated with current affairs.")
        else:
            reply.append("• For tech and business roles, building a portfolio of projects or case studies is crucial. It demonstrates practical ability.")
        reply.append("\nWhat specific career path are you curious about?")
        return "\n".join(reply)

    # Fallback for questions it can't answer
    return "That's an interesting question! My primary expertise is in career guidance. Can I help you with creating a learning plan, finding resources for a skill, or preparing for an interview?"


def get_gemini_advice(user_skills, top_role, gaps, career_type='tech'):
    """[FIXED] Generates highly personalized advice based on user skills and target role."""
    
    prompt = f"""You are an expert career coach. A user has provided their skills and has been matched with a top career goal. Provide personalized, actionable advice.

**User Profile:**
* **Current Skills:** {', '.join(user_skills) if user_skills else 'Not specified'}
* **Target Career:** {top_role['title']}
* **Identified Skill Gaps:** {', '.join(gaps) if gaps else 'None'}

**Your Task:**
Generate a concise, encouraging, and structured advisory report with the following sections:

1.  **Analysis:** A brief opening statement confirming the user's profile and goal.
2.  **Leverage Your Strengths:** Explain how the user's CURRENT skills (pick 2-3 of the most relevant) are valuable for the '{top_role['title']}' role and how they can be highlighted.
3.  **Bridge Your Skill Gaps:** Create a clear, step-by-step plan to learn the most critical skill gaps. For each gap, suggest a type of learning resource (e.g., "an interactive online course," "a hands-on project").
4.  **Actionable Next Steps:** Provide 3-4 bullet points for what the user should do in the next 30 days.

Maintain a positive and motivational tone.
"""
    return get_gemini_response(prompt, max_tokens=500, temperature=0.6)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    mode = data.get('mode', 'quick')
    interest = data.get('domain', '')
    career_type = data.get('careerType', 'tech')  # New: get career type
    
    # FIX: The 'resume' mode should be handled like the 'quick' mode after skills are extracted by the frontend.
    if mode in ['quick', 'resume']:
        user_skills_raw = data.get('skills', '')
        if not user_skills_raw:
            return jsonify({'error': 'No skills provided'}), 400
        user_skills = normalize_skills(user_skills_raw)
    elif mode == 'detailed':
        skills_data = data.get('skills', [])
        if not skills_data:
            return jsonify({'error': 'No skills provided'}), 400
        user_skills = [skill['skill'].lower() for skill in skills_data if skill.get('proficiency', 0) > 0]
    else:
        return jsonify({'error': 'Invalid mode specified'}), 400

    # Enhanced: Filter roles by career type and domain
    roles = get_roles_by_type_and_domain(career_type, interest)
    
    # Debug logging
    app.logger.debug(f"Career type: {career_type}, Domain: {interest}, Found roles: {len(roles)}")
    
    if not roles:
        return jsonify({'error': f'No roles found for {career_type} careers with domain {interest}.'}), 404

    scored_roles = []
    for role in roles:
        score_data = score_role(user_skills, role)
        scored_roles.append({**role, **score_data})
    
    scored_roles.sort(key=lambda r: r['score'], reverse=True)
    
    top_roles = scored_roles[:3]
    top_role = top_roles[0] if top_roles else None

    learning_plan = []
    if top_role:
        for skill in top_role['missing'][:5]:
            learning_plan.append({
                'skill': skill,
                'resources': resources_for_skill(skill)
            })

    ai_advice = ""
    if top_role:
        if is_gemini_available():
            ai_advice = get_gemini_advice(user_skills, top_role, top_role['missing'][:5], career_type)
        else:
            ai_advice = generate_skill_based_advice(user_skills, top_role, top_role['missing'][:5], career_type)

    # Ensure all properties are properly structured for frontend
    formatted_roles = []
    for role in top_roles:
        formatted_role = {
            'title': role.get('title', 'Unknown Role'),
            'description': role.get('description', 'No description available'),
            'score': role.get('score', 0),
            'skills': role.get('matchedList', [])[:5],  # Limit to 5 skills for display
            'missing': role.get('missing', [])
        }
        formatted_roles.append(formatted_role)

    # Format learning plan properly
    formatted_learning_plan = []
    for item in learning_plan:
        if isinstance(item, dict) and 'skill' in item:
            formatted_learning_plan.append({
                'category': item['skill'].title(),
                'resources': item.get('resources', [])
            })

    response_data = {
        'bestRoles': formatted_roles,
        'userSkills': user_skills if user_skills else [],
        'skillGaps': top_role['missing'][:5] if top_role and 'missing' in top_role else [],
        'learningPlan': formatted_learning_plan,
        'actionPlan': plan_for_gaps(top_role['missing'][:5] if top_role and 'missing' in top_role else []),
        'aiAdvice': ai_advice if ai_advice else 'Complete your assessment to get personalized AI advice.',
        'careerType': career_type
    }
    
    return jsonify(response_data)

@app.route('/api/chat', methods=['POST'])
def chat():
    """[FIXED] Handle AI chat with a more conversational approach."""
    try:
        data = request.json
        message = data.get('message', '')
        context = data.get('context', {})
        chat_history = data.get('chatHistory', [])
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        career_type = context.get('careerType', 'general')
        skills = context.get('skills', [])

        if is_gemini_available():
            # Build conversation history for context
            history_context = ""
            for msg in chat_history[-3:]: # Use last 3 messages
                history_context += f"User: {msg.get('user', '')}\nAssistant: {msg.get('assistant', '')}\n"

            # A more conversational prompt
            chat_prompt = f"""You are a friendly, conversational AI assistant named CareerPath AI. Your primary goal is to be helpful and engaging. You have special expertise in career counseling.

Here is some context about the user (use it only if their question is related to careers):
- Career Focus: {career_type}
- User Skills: {', '.join(skills)}

Recent conversation history:
{history_context}

Now, please provide a natural and helpful response to the user's latest message: "{message}"
If the user asks a general question (e.g., about jokes, weather, facts), answer it naturally. Do not force career advice into every response.
"""
            ai_response = get_gemini_response(chat_prompt, max_tokens=300, temperature=0.8)
        else:
            # Use the improved local chat engine
            ai_response = simple_chat_engine(message, context)
        
        return jsonify({
            'response': ai_response,
            'timestamp': time.time()
        })
        
    except Exception as e:
        app.logger.error(f"Chat error: {e}")
        return jsonify({
            'response': 'I apologize, but I encountered an error. Please try asking your question again.',
            'timestamp': time.time()
        })


def get_roles_by_type_and_domain(career_type, domain):
    """Enhanced function to filter roles by career type and domain"""
    all_roles = get_roles('')  # Get all roles
    
    if not all_roles:
        return []
    
    filtered_roles = []
    
    for role in all_roles:
        role_tags = role.get('tags', [])
        
        # Filter by career type first
        career_match = False
        
        if career_type == 'tech':
            # Tech roles: exclude roles tagged with 'nontech' or 'government'
            if not any(tag in role_tags for tag in ['nontech', 'government']):
                career_match = True
        elif career_type == 'nontech':
            # Non-tech roles: include roles tagged with 'nontech' or traditional business domains
            if any(tag in role_tags for tag in ['nontech', 'healthcare', 'finance', 'education', 'marketing', 'hr', 'consulting', 'operations', 'legal']):
                career_match = True
        elif career_type == 'government':
            # Government roles: include roles tagged with 'government' or specific government domains
            # Expanded matching criteria for better coverage
            government_tags = ['government', 'ias', 'banking', 'railway', 'defense', 'ssc', 'psu', 'judiciary', 'teaching', 
                             'upsc', 'civil', 'public', 'administrative', 'clerk', 'officer', 'exam', 'competitive',
                             'central', 'state', 'municipal', 'local', 'service', 'commission']
            if any(tag in role_tags for tag in government_tags):
                career_match = True
            # Also match if role title contains government-related keywords
            role_title_lower = role.get('title', '').lower()
            government_keywords = ['government', 'civil', 'public', 'administrative', 'clerk', 'officer', 
                                 'ias', 'ips', 'bank', 'railway', 'defense', 'ssc', 'upsc', 'psu', 'nabard', 'rbi']
            if any(keyword in role_title_lower for keyword in government_keywords):
                career_match = True
        
        # If career type matches, then check domain
        if career_match:
            if domain and domain != 'general':
                # Domain specified - must match exactly
                if domain in role_tags:
                    filtered_roles.append(role)
            else:
                # No domain specified - include all career type matches
                filtered_roles.append(role)
    
    return filtered_roles

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'version': '2.0.0',
        'features': ['skill_assessment', 'career_roadmap', 'ai_insights', 'multi_career_types']
    })

# Serve React app
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


def generate_chat_response(message, context):
    """Enhanced conversational chat response generation with detailed career guidance"""
    skills = context.get('skills', [])
    domain = context.get('domain', '')
    career_type = context.get('careerType', 'tech')
    top_role = context.get('topRole', '')
    recent_messages = context.get('recentMessages', [])
    
    # Build comprehensive context information
    context_info = ""
    if career_type:
        context_info += f"Career focus: {career_type}. "
    if skills:
        context_info += f"User's skills: {', '.join(skills[:5])}. "
    if domain:
        context_info += f"Preferred domain: {domain}. "
    if top_role:
        context_info += f"Top career match: {top_role}. "
    
    # Enhanced conversational prompt based on career type
    if career_type == 'government':
        prompt = f"""You are a friendly, knowledgeable AI career advisor specializing in government careers and civil services in India. {context_info}
        
        User question: {message}
        
        Respond as a conversational mentor who:
        - Provides detailed, step-by-step guidance
        - Shares specific resources, books, and study materials
        - Gives practical exam preparation strategies
        - Explains career paths in government service
        - Offers motivation and encouragement
        - Answers questions about UPSC, SSC, Banking, Railway, Defense, PSU jobs
        - Provides current affairs guidance and study tips
        - Explains interview preparation and personality development
        
        Be conversational, encouraging, and provide specific actionable advice. Include relevant resources, timelines, and detailed explanations. Keep responses comprehensive but engaging (300-400 words)."""
        
    elif career_type == 'nontech':
        prompt = f"""You are a friendly, experienced AI career advisor for non-technical careers. {context_info}
        
        User question: {message}
        
        Respond as a conversational mentor who:
        - Provides detailed industry insights and career paths
        - Shares specific skills to develop and certifications to pursue
        - Explains networking strategies and professional development
        - Offers guidance on transitioning between industries
        - Discusses salary expectations and growth opportunities
        - Provides specific resources, courses, and learning paths
        - Answers questions about business, finance, marketing, HR, healthcare, education, etc.
        
        Be conversational, practical, and provide specific actionable advice. Include relevant resources, timelines, and detailed explanations. Keep responses comprehensive but engaging (300-400 words)."""
        
    else:
        prompt = f"""You are a friendly, experienced AI career advisor for technology careers. {context_info}
        
        User question: {message}
        
        Respond as a conversational mentor who:
        - Provides detailed technical guidance and learning paths
        - Shares specific technologies to learn and project ideas
        - Explains industry trends and emerging technologies
        - Offers portfolio building and networking strategies
        - Discusses salary expectations and career progression
        - Provides specific resources, courses, and coding challenges
        - Answers questions about software development, data science, AI/ML, cloud, etc.
        
        Be conversational, technical but accessible, and provide specific actionable advice. Include relevant resources, project ideas, and detailed explanations. Keep responses comprehensive but engaging (300-400 words)."""
    
    # Try Gemini API first
    if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here" and len(GEMINI_API_KEY) > 20:
        try:
            endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            response = requests.post(endpoint, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "I'm here to help!")
        except Exception as e:
            app.logger.error(f"Gemini API error: {e}")
    
    # Enhanced local chat fallback
    return simple_chat_engine(message, {
        'careerType': career_type,
        'domain': domain,
        'skills': skills
    })

def get_fallback_response(message, career_type='tech'):
    """Enhanced fallback responses based on career type"""
    message_lower = message.lower()
    
    if career_type == 'government':
        if any(word in message_lower for word in ['exam', 'upsc', 'ssc', 'banking', 'preparation']):
            return "For government exam preparation, I recommend creating a structured study plan, focusing on current affairs daily, and practicing previous year questions. Which specific exam are you preparing for?"
        elif any(word in message_lower for word in ['career', 'path', 'job']):
            return "Government careers offer excellent job security and growth opportunities. Popular options include IAS/IPS through UPSC, banking through IBPS/SBI, and various PSU positions. What area interests you most?"
        elif any(word in message_lower for word in ['study', 'preparation', 'strategy']):
            return "Effective government exam preparation requires consistent daily study, current affairs reading, and regular mock tests. Focus on your strengths while gradually improving weak areas."
    elif career_type == 'nontech':
        if any(word in message_lower for word in ['career', 'transition', 'change']):
            return "Non-tech career transitions often involve leveraging transferable skills and gaining industry-specific knowledge. Consider professional certifications and networking within your target industry."
        elif any(word in message_lower for word in ['skill', 'develop', 'improve']):
            return "For non-tech careers, focus on developing both hard skills (industry-specific) and soft skills (communication, leadership). Professional certifications can significantly boost your credibility."
        elif any(word in message_lower for word in ['finance', 'marketing', 'hr', 'consulting']):
            return "These are excellent non-tech career paths! Each has specific skill requirements and growth trajectories. Would you like detailed guidance for any particular field?"
    else:  # tech careers
        if any(word in message_lower for word in ['career', 'path', 'direction']):
            return "I can help you explore tech career paths! Based on your skills, I can suggest roles that match your background. What specific technology area interests you most?"
        elif any(word in message_lower for word in ['skill', 'learn', 'develop']):
            return "For tech careers, I recommend focusing on both technical skills and problem-solving abilities. What specific technologies are you looking to learn?"
        elif any(word in message_lower for word in ['programming', 'coding', 'development']):
            return "Programming is a great career path! Popular areas include web development, mobile apps, data science, AI/ML, and cloud computing. What type of development interests you?"
        elif any(word in message_lower for word in ['data science', 'machine learning', 'ai']):
            return "Data science and AI are exciting fields! Key skills include Python, statistics, machine learning algorithms, and data visualization. Would you like specific learning recommendations?"
    
    # Default response
    return "I'm here to help with your career journey! I can assist with career advice, skill development, job market insights, exam preparation, and much more. What would you like to explore?"

def get_enhanced_fallback_response(prompt_or_message, career_type='tech', context=None):
    """Professional fallback responses with comprehensive career guidance"""
    # Handle both direct messages and prompts
    if isinstance(prompt_or_message, str):
        if 'User message:' in prompt_or_message or 'User:' in prompt_or_message:
            # Extract message from prompt
            lines = prompt_or_message.split('\n')
            message = ''
            for line in lines:
                if line.startswith('User message:') or line.startswith('User:'):
                    message = line.split(':', 1)[1].strip()
                    break
            if not message:
                message = prompt_or_message
        else:
            message = prompt_or_message
    else:
        message = str(prompt_or_message)
    
    message_lower = message.lower()
    skills = context.get('skills', []) if context else []
    
    # Handle simple greetings and general conversation
    greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
    if any(greeting in message_lower for greeting in greetings):
        return "**Welcome to Your Career Advisory Session**\n\nI'm your professional AI career consultant, equipped with expertise across technology, non-technical, and government sectors. I provide:\n\n• **Personalized Career Guidance** - Tailored advice based on your skills and goals\n• **Industry Insights** - Current market trends and opportunities\n• **Skill Development Plans** - Strategic learning roadmaps\n• **Exam Preparation Support** - Comprehensive preparation strategies\n• **Professional Development** - Career advancement strategies\n\nHow may I assist you with your career objectives today?"
    
    # Handle general questions
    if any(word in message_lower for word in ['how are you', 'what can you do', 'help me']):
        return "**Professional Career Advisory Services**\n\nI specialize in providing comprehensive career guidance across multiple domains:\n\n**🔧 Technology Careers:**\n• Software development, data science, AI/ML, cloud computing\n• Technical skill assessments and learning roadmaps\n• Industry certifications and project portfolio guidance\n\n**💼 Non-Technical Careers:**\n• Business, finance, marketing, healthcare, education\n• Professional certifications and networking strategies\n• Industry transition and skill development plans\n\n**🏛️ Government & Civil Services:**\n• UPSC, SSC, banking, railway, defense examinations\n• Comprehensive preparation strategies and study materials\n• Career progression in public service\n\nWhat specific career area would you like to explore?"
    
    # Government career responses
    if career_type == 'government':
        if any(word in message_lower for word in ['upsc', 'civil services', 'ias', 'ips']):
            return """🎯 **UPSC Civil Services Preparation Guide**

**Phase 1: Foundation (Months 1-6)**
- **NCERT Books**: Complete 6th to 12th standard NCERTs for all subjects
- **Current Affairs**: Read The Hindu daily, make notes
- **Prelims Practice**: Start with previous year papers
- **CSAT**: Focus on quantitative aptitude and logical reasoning

**Phase 2: Mains Preparation (Months 7-12)**
- **Optional Subject**: Choose based on your background and interest
- **Answer Writing**: Practice daily, join test series
- **Essay Writing**: Practice on diverse topics
- **Ethics Paper**: Study case studies and examples

**Phase 3: Interview (Months 13-15)**
- **Mock Interviews**: Join coaching or online platforms
- **Personality Development**: Work on communication skills
- **Current Affairs**: Stay updated with recent developments

**📚 Essential Resources:**
- NCERT Books (6th-12th)
- The Hindu newspaper
- Vision IAS current affairs
- Previous year question papers
- Test series from coaching institutes

**💡 Pro Tips:**
- Consistency is key - study 8-10 hours daily
- Make your own notes
- Practice answer writing regularly
- Stay motivated and focused

Would you like specific guidance on any particular exam or subject?"""

        elif any(word in message_lower for word in ['banking', 'sbi', 'ibps', 'po', 'clerk']):
            return """🏦 **Banking Career Preparation Guide**

**Popular Banking Exams:**
- **SBI PO/Clerk**: State Bank of India
- **IBPS PO/Clerk**: Institute of Banking Personnel Selection
- **RBI Grade B**: Reserve Bank of India
- **NABARD**: National Bank for Agriculture and Rural Development

**📚 Syllabus & Preparation:**
1. **Quantitative Aptitude** (40% weightage)
   - Number systems, percentages, ratios
   - Data interpretation, time & work
   - Practice: R.S. Aggarwal, Arun Sharma

2. **English Language** (30% weightage)
   - Grammar, vocabulary, comprehension
   - Reading comprehension, cloze test
   - Practice: Wren & Martin, Norman Lewis

3. **Reasoning Ability** (30% weightage)
   - Logical reasoning, puzzles
   - Coding-decoding, blood relations
   - Practice: R.S. Aggarwal, Kiran's book

4. **General Awareness**
   - Banking awareness, current affairs
   - Economic news, RBI policies
   - Practice: Banking awareness books, newspapers

**⏰ Study Plan:**
- **Daily**: 6-8 hours of focused study
- **Weekly**: Take mock tests
- **Monthly**: Analyze performance and improve weak areas

**📖 Recommended Books:**
- Quantitative Aptitude: R.S. Aggarwal
- English: Wren & Martin + Norman Lewis
- Reasoning: R.S. Aggarwal + Kiran's
- Banking Awareness: Arihant publications

**💼 Career Growth:**
- Clerk → Officer → Manager → AGM → DGM
- Salary: ₹25,000 - ₹80,000+ per month
- Job security and excellent benefits

Need help with any specific banking exam preparation?"""

        elif any(word in message_lower for word in ['ssc', 'cgl', 'chsl', 'mts']):
            return """📋 **SSC (Staff Selection Commission) Preparation Guide**

**SSC Exams Overview:**
- **SSC CGL**: Combined Graduate Level (Officer posts)
- **SSC CHSL**: Combined Higher Secondary Level (Clerk posts)
- **SSC MTS**: Multi-Tasking Staff
- **SSC CPO**: Central Police Organization

**📚 CGL Syllabus & Strategy:**
1. **General Intelligence & Reasoning** (50 questions)
   - Analogies, similarities, differences
   - Spatial visualization, problem solving
   - Practice: R.S. Aggarwal, Kiran's book

2. **General Awareness** (50 questions)
   - Current affairs, history, geography
   - Science, economics, polity
   - Practice: Lucent GK, newspapers

3. **Quantitative Aptitude** (50 questions)
   - Arithmetic, algebra, geometry
   - Trigonometry, statistics
   - Practice: R.S. Aggarwal, Arun Sharma

4. **English Comprehension** (50 questions)
   - Grammar, vocabulary, comprehension
   - One-word substitution, idioms
   - Practice: Wren & Martin, Norman Lewis

**⏰ Tier 2 Preparation:**
- **Quantitative Abilities**: Advanced math
- **English Language**: Essay, précis, letter writing
- **Statistics**: For Statistical Investigator posts
- **General Studies**: For Assistant Audit Officer posts

**📖 Essential Resources:**
- **Books**: R.S. Aggarwal (Math), Lucent GK, Wren & Martin
- **Online**: SSC official website, mock test platforms
- **Current Affairs**: The Hindu, Pratiyogita Darpan

**💡 Success Tips:**
- Solve previous year papers (last 5 years)
- Take regular mock tests
- Focus on accuracy over speed initially
- Make short notes for revision

**🎯 Career Opportunities:**
- Income Tax Inspector
- Assistant Audit Officer
- Statistical Investigator
- Assistant Section Officer
- Various ministries and departments

Which SSC exam are you targeting? I can provide specific guidance!"""

        else:
            return "I'm here to help you with government careers in India! Whether you're interested in civil services (UPSC), banking exams (SBI/IBPS), SSC positions, railway jobs, defense services, or PSU careers, I can provide detailed guidance on exam preparation, study strategies, and career paths. What specific government career or exam interests you?"

    # Non-tech career responses
    elif career_type == 'nontech':
        if any(word in message_lower for word in ['business', 'management', 'mba']):
            return """💼 **Business & Management Career Guide**

**🎓 MBA Preparation & Career Paths:**

**Top MBA Specializations:**
- **Finance**: Investment banking, corporate finance, financial analysis
- **Marketing**: Brand management, digital marketing, sales
- **Operations**: Supply chain, logistics, process improvement
- **Human Resources**: Talent acquisition, organizational development
- **Consulting**: Management consulting, strategy consulting

**📚 MBA Entrance Exams:**
- **CAT**: Common Admission Test (IIMs)
- **XAT**: Xavier Aptitude Test (XLRI)
- **SNAP**: Symbiosis National Aptitude Test
- **MAT**: Management Aptitude Test
- **CMAT**: Common Management Admission Test

**💡 Career Progression:**
- **Entry Level**: Management Trainee, Analyst
- **Mid Level**: Manager, Senior Manager
- **Senior Level**: Director, VP, C-Suite

**📖 Essential Skills:**
- Leadership and team management
- Strategic thinking and problem solving
- Communication and presentation skills
- Data analysis and decision making
- Networking and relationship building

**💰 Salary Expectations:**
- **Entry Level**: ₹6-12 LPA
- **Mid Level**: ₹12-25 LPA
- **Senior Level**: ₹25-50+ LPA

**🎯 Industry Options:**
- Consulting (McKinsey, BCG, Bain)
- Banking & Finance (Goldman Sachs, JP Morgan)
- Technology (Google, Microsoft, Amazon)
- FMCG (Unilever, P&G, Nestle)
- Healthcare, Education, Real Estate

**📚 Recommended Resources:**
- **Books**: How to Crack CAT, Arun Sharma
- **Online**: Coursera, edX for business courses
- **Networking**: LinkedIn, industry events

Which business field interests you most? I can provide specific guidance!"""

        elif any(word in message_lower for word in ['marketing', 'digital marketing', 'social media']):
            return """📱 **Marketing & Digital Marketing Career Guide**

**🎯 Marketing Career Paths:**

**Traditional Marketing:**
- Brand Management
- Product Marketing
- Market Research
- Advertising & PR
- Sales & Business Development

**Digital Marketing:**
- Social Media Marketing
- SEO/SEM Specialist
- Content Marketing
- Email Marketing
- Performance Marketing
- Marketing Analytics

**📚 Essential Skills:**
- **Technical**: Google Analytics, Facebook Ads, SEO tools
- **Creative**: Content creation, graphic design basics
- **Analytical**: Data analysis, ROI measurement
- **Communication**: Copywriting, presentation skills

**🎓 Certifications to Pursue:**
- **Google**: Google Analytics, Google Ads, Digital Marketing
- **Facebook**: Facebook Blueprint
- **HubSpot**: Content Marketing, Inbound Marketing
- **Hootsuite**: Social Media Marketing
- **SEMrush**: SEO and SEM

**💼 Career Progression:**
- **Entry**: Marketing Coordinator, Social Media Manager
- **Mid**: Marketing Manager, Digital Marketing Manager
- **Senior**: Marketing Director, CMO

**💰 Salary Ranges:**
- **Entry Level**: ₹3-6 LPA
- **Mid Level**: ₹6-15 LPA
- **Senior Level**: ₹15-30+ LPA

**📖 Learning Resources:**
- **Courses**: Coursera, Udemy, Google Digital Garage
- **Books**: "Digital Marketing" by Dave Chaffey
- **Tools**: Google Analytics, SEMrush, Hootsuite
- **Practice**: Start your own blog or social media accounts

**🎯 Industry Opportunities:**
- E-commerce (Amazon, Flipkart)
- Technology (Google, Facebook, Microsoft)
- FMCG (Unilever, P&G)
- Startups and agencies
- Freelancing and consulting

**💡 Pro Tips:**
- Build a portfolio with real campaigns
- Stay updated with latest trends
- Network with industry professionals
- Start with free tools and gradually upgrade

Which aspect of marketing interests you most? I can provide detailed guidance!"""

        else:
            return "I'm here to help you explore non-technical career opportunities! Whether you're interested in business and management, finance, marketing, human resources, healthcare, education, or other traditional industries, I can provide guidance on career paths, required skills, certifications, and growth opportunities. What specific non-tech field interests you?"

    # Tech career responses
    else:
        if any(word in message_lower for word in ['web development', 'frontend', 'backend', 'full stack']):
            return "Web development is a great career choice! You can specialize in frontend (user interfaces), backend (server-side), or full-stack development. Key skills include HTML, CSS, JavaScript, and frameworks like React or Angular. Would you like specific guidance on any particular area of web development?"

        elif any(word in message_lower for word in ['data science', 'machine learning', 'ai', 'analytics']):
            return "Data science and AI are exciting fields! Career paths include Data Analyst, Data Scientist, ML Engineer, and AI Research Scientist. Key skills include Python, statistics, machine learning, and SQL. The field offers excellent growth opportunities with salaries ranging from 4-50+ LPA. Would you like specific guidance on any particular area?"
        else:
            return "I can help you explore various tech career paths including web development, data science, mobile development, cloud computing, cybersecurity, and more. What specific technology area interests you most?"

    return "I'm here to help with your career journey! Ask me about career paths, skill development, exam preparation, or industry insights. What would you like to know?"

@app.route('/api/resume/analyze', methods=['POST'])
def analyze_resume():
    """API endpoint for comprehensive resume analysis"""
    try:
        data = request.json
        resume_text = data.get('text', '')
        career_type = data.get('careerType', 'tech')
        
        if not resume_text:
            return jsonify({'error': 'No resume text provided'}), 400
        
        # Perform deep holistic analysis
        analysis_result = perform_deep_resume_analysis(resume_text, career_type)
        
        return jsonify(analysis_result)
        
    except Exception as e:
        app.logger.error(f"Resume analysis error: {e}")
        return jsonify({'error': 'Failed to analyze resume'}), 500

def perform_deep_resume_analysis(resume_text, career_type):
    """Perform comprehensive holistic resume analysis"""
    
    # Extract all components
    skills = extract_skills_from_resume(resume_text, career_type)
    experience_level = extract_experience_level(resume_text)
    education = extract_education_from_resume(resume_text)
    certifications = extract_certifications_from_resume(resume_text)
    projects = extract_projects_from_resume(resume_text)
    work_experience = extract_work_experience_from_resume(resume_text)
    
    # Analyze overall profile strength
    profile_strength = analyze_profile_strength(resume_text, skills, experience_level, education, certifications)
    
    # Generate career recommendations based on holistic analysis
    career_recommendations = generate_career_recommendations(skills, experience_level, career_type, education)
    
    # Identify skill gaps and improvement areas
    skill_gaps = identify_skill_gaps(skills, career_type, experience_level)
    
    # Calculate comprehensive match scores for different roles
    role_matches = calculate_role_matches(skills, career_type, experience_level)
    
    # Generate actionable insights
    actionable_insights = generate_actionable_insights(skills, experience_level, career_type, skill_gaps)
    
    # Overall assessment
    overall_assessment = generate_overall_assessment(profile_strength, skills, experience_level, career_type)
    
    # Generate professional summary like a resume analyzer
    professional_summary = generate_professional_summary({
        'skills': skills,
        'projects': projects,
        'experienceLevel': experience_level,
        'certifications': certifications,
        'profileStrength': profile_strength
    })
    
    return {
        'skills': skills,
        'experienceLevel': experience_level,
        'education': education,
        'certifications': certifications,
        'projects': projects,
        'workExperience': work_experience,
        'profileStrength': profile_strength,
        'careerRecommendations': career_recommendations,
        'skillGaps': skill_gaps,
        'roleMatches': role_matches,
        'actionableInsights': actionable_insights,
        'overallAssessment': overall_assessment,
        'professionalSummary': professional_summary,
        'analysisDate': time.time(),
        'totalSkills': len(skills),
        'totalProjects': len(projects),
        'totalInternships': len(profile_strength['detailed_analysis']['internships']),
        'impactScore': profile_strength['detailed_analysis']['work_impact']['score']
    }

def extract_skills_from_resume(text, career_type='tech'):
    """Extract skills from resume text based on career type"""
    # Enhanced skill extraction based on career type
    common_skills = []
    
    if career_type == 'tech':
        common_skills = [
            'Python', 'JavaScript', 'Java', 'C++', 'React', 'Vue', 'Angular', 'Node.js',
            'SQL', 'MongoDB', 'PostgreSQL', 'AWS', 'Docker', 'Kubernetes', 'Git',
            'Machine Learning', 'Data Science', 'AI', 'TensorFlow', 'PyTorch',
            'HTML', 'CSS', 'Bootstrap', 'jQuery', 'Express', 'Django', 'Flask',
            'TypeScript', 'Next.js', 'Vue.js', 'Svelte', 'Laravel', 'Spring Boot',
            'Redis', 'Elasticsearch', 'GraphQL', 'REST API', 'Microservices'
        ]
    elif career_type == 'nontech':
        common_skills = [
            'Project Management', 'Strategic Planning', 'Business Analysis', 'Financial Analysis',
            'Digital Marketing', 'SEO', 'Social Media', 'Content Marketing', 'Sales',
            'Excel', 'QuickBooks', 'SAP', 'CRM', 'Market Research', 'Brand Management',
            'Patient Care', 'Healthcare Administration', 'Medical Coding',
            'Curriculum Development', 'Instructional Design', 'E-learning',
            'Recruitment', 'HR Analytics', 'Performance Management',
            'Leadership', 'Communication', 'Problem Solving', 'Team Management',
            'Budget Management', 'Risk Assessment', 'Quality Assurance'
        ]
    elif career_type == 'government':
        common_skills = [
            'Indian History', 'Geography', 'Polity', 'Economics', 'Current Affairs',
            'Mathematics', 'Logical Reasoning', 'Data Interpretation',
            'English Grammar', 'Essay Writing', 'Public Speaking',
            'Public Administration', 'Policy Making', 'Governance',
            'Indian Constitution', 'Legal Reasoning', 'Administrative Law',
            'MS Office', 'Data Entry', 'Digital Literacy'
        ]
    
    # Add common soft skills
    common_skills.extend(['Communication', 'Leadership', 'Problem Solving', 'Teamwork', 'Time Management'])
    
    # Extract skills from text
    found_skills = []
    lower_text = text.lower()
    
    for skill in common_skills:
        if skill.lower() in lower_text:
            found_skills.append(skill)
    
    return list(set(found_skills))

def extract_experience_level(text):
    """Extract experience level from resume text"""
    experience_keywords = {
        'entry': ['entry', 'junior', 'intern', 'graduate', 'new', 'recent', 'fresher'],
        'mid': ['mid', 'intermediate', '2-3 years', '3-4 years', 'experienced', '2 years', '3 years'],
        'senior': ['senior', 'lead', 'principal', '5+ years', 'expert', 'architect', '5 years', '6 years'],
        'executive': ['director', 'manager', 'head', 'vp', 'cto', 'ceo', 'executive']
    }
    
    lower_text = text.lower()
    max_level = 'entry'
    max_count = 0
    
    for level, keywords in experience_keywords.items():
        count = sum(1 for keyword in keywords if keyword in lower_text)
        if count > max_count:
            max_count = count
            max_level = level
    
    return max_level.capitalize()

def calculate_resume_match_score(skills, career_type):
    """Calculate match score for resume"""
    base_score = min(95, len(skills) * 8)
    return round(base_score + (hash(career_type) % 20))

def extract_education_from_resume(text):
    """Extract education information from resume"""
    education_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college', 'b.tech', 'm.tech', 'mba', 'bca', 'mca']
    lower_text = text.lower()
    education = []
    
    for keyword in education_keywords:
        if keyword in lower_text:
            start_index = lower_text.index(keyword)
            segment = text[start_index:start_index + 100]
            education.append(segment.split('\n')[0])
    
    return list(set(education))[:3]

def extract_certifications_from_resume(text):
    """Extract certifications from resume"""
    cert_keywords = ['certified', 'certification', 'certificate', 'aws', 'azure', 'google cloud', 'cisco', 'microsoft']
    lower_text = text.lower()
    certifications = []
    
    for keyword in cert_keywords:
        if keyword in lower_text:
            start_index = lower_text.index(keyword)
            segment = text[start_index:start_index + 80]
            certifications.append(segment.split('\n')[0])
    
    return list(set(certifications))[:5]

def extract_projects_from_resume(text):
    """Extract projects from resume"""
    project_keywords = ['project', 'built', 'developed', 'created', 'implemented']
    lower_text = text.lower()
    projects = []
    
    for keyword in project_keywords:
        if keyword in lower_text:
            start_index = lower_text.index(keyword)
            segment = text[start_index:start_index + 120]
            projects.append(segment.split('\n')[0])
    
    return list(set(projects))[:4]

def extract_work_experience_from_resume(text):
    """Extract work experience from resume"""
    work_keywords = ['experience', 'worked', 'employed', 'position', 'role', 'company']
    lower_text = text.lower()
    work_experience = []
    
    for keyword in work_keywords:
        if keyword in lower_text:
            start_index = lower_text.index(keyword)
            segment = text[start_index:start_index + 100]
            work_experience.append(segment.split('\n')[0])
    
    return list(set(work_experience))[:3]

@app.route('/api/add_role', methods=['POST'])
def handle_add_role():
    role_data = request.json
    if not role_data or 'title' not in role_data:
        return jsonify({'error': 'Invalid role data'}), 400
    try:
        add_role(role_data)
        return jsonify({'message': 'Role added successfully'}), 201
    except Exception as e:
        app.logger.error(f"Failed to add role: {e}")
        return jsonify({'error': 'Failed to add role'}), 500

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    try:
        init_db()
    except Exception as e:
        app.logger.error(f"Database init raised: {e}")

    print('Starting Flask app on http://localhost:5000/', flush=True)
    app.run(host='localhost', port=5000, debug=True)