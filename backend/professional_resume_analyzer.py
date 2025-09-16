"""
Professional Resume Analyzer - Comprehensive achievement and experience analysis
"""
import re
from datetime import datetime

def extract_detailed_achievements(resume_text):
    """Extract all types of achievements from resume"""
    achievements = {
        'technical': [],
        'awards': [],
        'publications': [],
        'certifications_earned': [],
        'performance_metrics': []
    }
    
    lines = resume_text.split('\n')
    
    for line in lines:
        line_lower = line.lower().strip()
        
        # Technical achievements
        if any(word in line_lower for word in ['developed', 'built', 'created', 'implemented', 'designed', 'optimized']):
            if any(tech in line_lower for tech in ['system', 'application', 'website', 'database', 'algorithm', 'model']):
                achievements['technical'].append(line.strip())
        
        # Awards and recognition
        if any(word in line_lower for word in ['award', 'recognition', 'honor', 'medal', 'prize', 'winner', 'champion']):
            achievements['awards'].append(line.strip())
        
        # Publications
        if any(word in line_lower for word in ['published', 'paper', 'journal', 'conference', 'research']):
            achievements['publications'].append(line.strip())
        
        # Performance metrics
        if re.search(r'\d+%|\$\d+|increased|improved|reduced|saved', line_lower):
            achievements['performance_metrics'].append(line.strip())
    
    return achievements

def extract_detailed_projects(resume_text):
    """Extract detailed project information"""
    projects = []
    lines = resume_text.split('\n')
    current_project = None
    
    for line in lines:
        line_stripped = line.strip()
        line_lower = line_stripped.lower()
        
        # Project headers
        if any(word in line_lower for word in ['project', 'built', 'developed']) and len(line_stripped) < 100:
            if current_project:
                projects.append(current_project)
            
            current_project = {
                'title': line_stripped,
                'description': '',
                'technologies': [],
                'complexity': 1
            }
        
        # Project details
        elif current_project and line_stripped:
            current_project['description'] += ' ' + line_stripped
            
            # Extract technologies
            tech_keywords = ['python', 'javascript', 'react', 'node', 'sql', 'aws', 'docker', 'java', 'c++']
            for tech in tech_keywords:
                if tech in line_lower and tech not in current_project['technologies']:
                    current_project['technologies'].append(tech.title())
            
            # Assess complexity
            complexity_indicators = ['machine learning', 'ai', 'distributed', 'microservices', 'cloud', 'scalable']
            if any(indicator in line_lower for indicator in complexity_indicators):
                current_project['complexity'] = 3
            elif any(indicator in line_lower for indicator in ['database', 'api', 'full stack']):
                current_project['complexity'] = 2
    
    if current_project:
        projects.append(current_project)
    
    return projects[:5]  # Return top 5 projects

def extract_internships(resume_text):
    """Extract internship and training experiences"""
    internships = []
    lines = resume_text.split('\n')
    
    for line in lines:
        line_lower = line.lower().strip()
        
        if any(word in line_lower for word in ['intern', 'trainee', 'apprentice', 'co-op', 'summer program']):
            # Extract company and duration if possible
            internship = {
                'title': line.strip(),
                'type': 'internship',
                'duration': extract_duration_from_line(line),
                'company': extract_company_from_line(line)
            }
            internships.append(internship)
        
        elif any(word in line_lower for word in ['training', 'workshop', 'bootcamp', 'course completed']):
            training = {
                'title': line.strip(),
                'type': 'training',
                'duration': extract_duration_from_line(line),
                'provider': extract_company_from_line(line)
            }
            internships.append(training)
    
    return internships

def analyze_work_impact(resume_text):
    """Analyze work impact and quantifiable results"""
    impact_score = 0
    impact_items = []
    
    # Look for quantifiable achievements
    percentage_matches = re.findall(r'(\d+)%', resume_text)
    for match in percentage_matches:
        if int(match) > 10:  # Significant percentage improvements
            impact_score += 2
            impact_items.append(f"{match}% improvement/increase")
    
    # Look for monetary impact
    money_matches = re.findall(r'\$(\d+(?:,\d+)*)', resume_text)
    for match in money_matches:
        impact_score += 3
        impact_items.append(f"${match} financial impact")
    
    # Look for scale indicators
    scale_words = ['million', 'thousand', 'users', 'customers', 'team of', 'managed']
    for word in scale_words:
        if word in resume_text.lower():
            impact_score += 1
            impact_items.append(f"Scale: {word}")
    
    return {
        'score': min(10, impact_score),
        'items': impact_items[:5]
    }

def extract_leadership_experience(resume_text):
    """Extract leadership roles and responsibilities"""
    leadership = []
    lines = resume_text.split('\n')
    
    leadership_keywords = [
        'lead', 'manager', 'supervisor', 'coordinator', 'head', 'director',
        'president', 'captain', 'mentor', 'team lead', 'project manager'
    ]
    
    for line in lines:
        line_lower = line.lower().strip()
        
        for keyword in leadership_keywords:
            if keyword in line_lower:
                leadership.append({
                    'role': line.strip(),
                    'type': keyword,
                    'scope': extract_team_size(line)
                })
                break
    
    return leadership

def extract_duration_from_line(line):
    """Extract duration information from a line"""
    # Look for patterns like "2023-2024", "6 months", "Jan 2023 - Mar 2023"
    duration_patterns = [
        r'\d{4}\s*-\s*\d{4}',
        r'\d+\s+months?',
        r'\d+\s+years?',
        r'[A-Za-z]{3}\s+\d{4}\s*-\s*[A-Za-z]{3}\s+\d{4}'
    ]
    
    for pattern in duration_patterns:
        match = re.search(pattern, line)
        if match:
            return match.group()
    
    return "Duration not specified"

def extract_company_from_line(line):
    """Extract company/organization name from a line"""
    # Simple heuristic - look for capitalized words that might be company names
    words = line.split()
    potential_companies = []
    
    for word in words:
        if word[0].isupper() and len(word) > 2 and word not in ['The', 'And', 'Of', 'In', 'At']:
            potential_companies.append(word)
    
    return ' '.join(potential_companies[:2]) if potential_companies else "Company not specified"

def extract_team_size(line):
    """Extract team size from leadership descriptions"""
    # Look for patterns like "team of 5", "5 members", "10-person team"
    size_patterns = [
        r'team of (\d+)',
        r'(\d+) members?',
        r'(\d+)-person team',
        r'managed (\d+)'
    ]
    
    for pattern in size_patterns:
        match = re.search(pattern, line.lower())
        if match:
            return f"{match.group(1)} people"
    
    return "Team size not specified"

def generate_professional_summary(profile_data):
    """Generate professional summary like a resume analyzer"""
    summary = {
        'profile_type': determine_profile_type(profile_data),
        'key_strengths': identify_key_strengths(profile_data),
        'career_stage': assess_career_stage(profile_data),
        'standout_achievements': get_standout_achievements(profile_data),
        'improvement_recommendations': get_improvement_recommendations(profile_data)
    }
    
    return summary

def determine_profile_type(profile_data):
    """Determine the type of professional profile"""
    skills = profile_data.get('skills', [])
    projects = profile_data.get('projects', [])
    experience = profile_data.get('experienceLevel', 'Entry')
    
    if len(projects) >= 3 and any('machine learning' in str(p).lower() for p in projects):
        return "Technical Specialist - Data Science/AI Focus"
    elif len(skills) >= 10 and experience in ['Mid', 'Senior']:
        return "Experienced Technical Professional"
    elif len(projects) >= 2 and experience == 'Entry':
        return "Emerging Technical Talent"
    else:
        return "Developing Professional"

def identify_key_strengths(profile_data):
    """Identify top 3-5 key strengths"""
    strengths = []
    
    skills_count = len(profile_data.get('skills', []))
    projects_count = len(profile_data.get('projects', []))
    certifications_count = len(profile_data.get('certifications', []))
    
    if skills_count >= 8:
        strengths.append(f"Diverse technical skill set ({skills_count} skills)")
    
    if projects_count >= 3:
        strengths.append(f"Strong project portfolio ({projects_count} projects)")
    
    if certifications_count >= 2:
        strengths.append(f"Professional certifications ({certifications_count} earned)")
    
    # Add more based on detailed analysis
    detailed = profile_data.get('profileStrength', {}).get('detailed_analysis', {})
    
    if detailed.get('work_impact', {}).get('score', 0) >= 5:
        strengths.append("Demonstrated measurable impact")
    
    if len(detailed.get('leadership', [])) >= 1:
        strengths.append("Leadership experience")
    
    return strengths[:5]

def assess_career_stage(profile_data):
    """Assess current career stage"""
    experience = profile_data.get('experienceLevel', 'Entry')
    skills_count = len(profile_data.get('skills', []))
    projects_count = len(profile_data.get('projects', []))
    
    if experience == 'Senior' and skills_count >= 12:
        return "Senior Professional - Ready for leadership roles"
    elif experience == 'Mid' and projects_count >= 3:
        return "Mid-level Professional - Growth trajectory"
    elif experience == 'Entry' and projects_count >= 2:
        return "Junior Professional - Strong foundation"
    else:
        return "Early Career - Building experience"

def get_standout_achievements(profile_data):
    """Identify standout achievements"""
    achievements = []
    
    detailed = profile_data.get('profileStrength', {}).get('detailed_analysis', {})
    
    # Technical achievements
    tech_achievements = detailed.get('achievements', {}).get('technical', [])
    if tech_achievements:
        achievements.extend(tech_achievements[:2])
    
    # Awards
    awards = detailed.get('achievements', {}).get('awards', [])
    if awards:
        achievements.extend(awards[:2])
    
    # Performance metrics
    metrics = detailed.get('work_impact', {}).get('items', [])
    if metrics:
        achievements.extend(metrics[:2])
    
    return achievements[:4]

def get_improvement_recommendations(profile_data):
    """Get specific improvement recommendations"""
    recommendations = []
    
    skills_count = len(profile_data.get('skills', []))
    projects_count = len(profile_data.get('projects', []))
    certifications_count = len(profile_data.get('certifications', []))
    
    if skills_count < 5:
        recommendations.append("Expand technical skill portfolio - aim for 8-10 core skills")
    
    if projects_count < 2:
        recommendations.append("Build project portfolio - showcase 3-4 significant projects")
    
    if certifications_count == 0:
        recommendations.append("Obtain relevant professional certifications")
    
    detailed = profile_data.get('profileStrength', {}).get('detailed_analysis', {})
    
    if not detailed.get('work_impact', {}).get('items'):
        recommendations.append("Quantify achievements with specific metrics and results")
    
    if not detailed.get('leadership'):
        recommendations.append("Seek leadership opportunities and team collaboration roles")
    
    return recommendations[:4]
