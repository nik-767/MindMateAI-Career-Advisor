"""
Enhanced resume analysis helper functions for comprehensive professional resume analysis
"""
import re
from datetime import datetime

def analyze_profile_strength(resume_text, skills, experience_level, education, certifications):
    """Professional resume analysis - comprehensive profile strength evaluation"""
    
    # Import functions locally to avoid circular imports
    from professional_resume_analyzer import (
        extract_detailed_achievements, extract_detailed_projects, extract_internships,
        analyze_work_impact, extract_leadership_experience
    )
    
    # Extract detailed achievements
    achievements = extract_detailed_achievements(resume_text)
    projects = extract_detailed_projects(resume_text)
    internships = extract_internships(resume_text)
    work_impact = analyze_work_impact(resume_text)
    leadership = extract_leadership_experience(resume_text)
    
    strength_score = 0
    factors = []
    
    # Skills & Technical Competency (25%)
    skill_score = min(25, len(skills) * 1.5 + len(achievements.get('technical', [])) * 2)
    strength_score += skill_score
    factors.append(f"Technical skills: {len(skills)} identified")
    
    # Project Portfolio (20%)
    project_score = min(20, len(projects) * 4 + sum(p.get('complexity', 1) for p in projects))
    strength_score += project_score
    factors.append(f"Projects: {len(projects)} significant projects")
    
    # Professional Experience (20%)
    exp_scores = {'Entry': 10, 'Mid': 16, 'Senior': 20, 'Expert': 20}
    exp_score = exp_scores.get(experience_level, 5) + work_impact['score']
    strength_score += min(20, exp_score)
    factors.append(f"Experience: {experience_level} level with impact score {work_impact['score']}")
    
    # Education & Certifications (15%)
    edu_score = min(15, len(education) * 3 + len(certifications) * 2)
    strength_score += edu_score
    factors.append(f"Credentials: {len(education)} degrees, {len(certifications)} certifications")
    
    # Internships & Training (10%)
    intern_score = min(10, len(internships) * 3)
    strength_score += intern_score
    factors.append(f"Practical experience: {len(internships)} internships/training")
    
    # Leadership & Achievements (10%)
    leadership_score = min(10, len(leadership) * 2 + len(achievements.get('awards', [])) * 3)
    strength_score += leadership_score
    factors.append(f"Leadership: {len(leadership)} roles, {len(achievements.get('awards', []))} awards")
    
    # Determine professional level
    if strength_score >= 85:
        level = "Exceptional"
    elif strength_score >= 70:
        level = "Strong"
    elif strength_score >= 55:
        level = "Competitive"
    elif strength_score >= 40:
        level = "Developing"
    else:
        level = "Entry Level"
    
    return {
        'score': round(strength_score),
        'level': level,
        'factors': factors,
        'detailed_analysis': {
            'achievements': achievements,
            'projects': projects,
            'internships': internships,
            'work_impact': work_impact,
            'leadership': leadership
        }
    }

def generate_career_recommendations(skills, experience_level, career_type, education):
    """Generate career recommendations based on holistic profile analysis"""
    recommendations = []
    
    if career_type == 'tech':
        # Tech career recommendations
        if 'Python' in skills or 'Data Science' in skills or 'Machine Learning' in skills:
            recommendations.append({
                'role': 'Data Scientist',
                'match': 85 if experience_level in ['Mid', 'Senior'] else 70,
                'reason': 'Strong data science and Python skills align well with this role'
            })
        
        if 'JavaScript' in skills or 'React' in skills or 'Node.js' in skills:
            recommendations.append({
                'role': 'Full Stack Developer',
                'match': 80 if experience_level in ['Mid', 'Senior'] else 65,
                'reason': 'Frontend and backend JavaScript skills are highly valuable'
            })
        
        if 'AWS' in skills or 'Docker' in skills or 'Kubernetes' in skills:
            recommendations.append({
                'role': 'DevOps Engineer',
                'match': 75 if experience_level in ['Mid', 'Senior'] else 60,
                'reason': 'Cloud and containerization skills are in high demand'
            })
    
    elif career_type == 'government':
        # Government career recommendations
        if any('banking' in skill.lower() for skill in skills):
            recommendations.append({
                'role': 'Bank PO',
                'match': 80,
                'reason': 'Banking knowledge and analytical skills suit this role'
            })
        
        if any('admin' in skill.lower() or 'management' in skill.lower() for skill in skills):
            recommendations.append({
                'role': 'Administrative Officer',
                'match': 75,
                'reason': 'Administrative and management skills are valuable for government roles'
            })
    
    elif career_type == 'nontech':
        # Non-tech career recommendations
        if any('marketing' in skill.lower() for skill in skills):
            recommendations.append({
                'role': 'Marketing Manager',
                'match': 80,
                'reason': 'Marketing skills and business acumen align with this role'
            })
        
        if any('finance' in skill.lower() or 'accounting' in skill.lower() for skill in skills):
            recommendations.append({
                'role': 'Financial Analyst',
                'match': 75,
                'reason': 'Financial skills and analytical thinking are key strengths'
            })
    
    # Add general recommendations if no specific matches
    if not recommendations:
        recommendations.append({
            'role': f'{career_type.title()} Specialist',
            'match': 60,
            'reason': 'Your skills show potential for growth in this field'
        })
    
    return recommendations[:3]  # Return top 3 recommendations

def identify_skill_gaps(skills, career_type, experience_level):
    """Identify skill gaps and improvement areas"""
    gaps = []
    
    if career_type == 'tech':
        essential_skills = ['Git', 'SQL', 'Problem Solving', 'System Design']
        advanced_skills = ['AWS', 'Docker', 'Microservices', 'Testing']
        
        for skill in essential_skills:
            if skill not in skills:
                gaps.append({
                    'skill': skill,
                    'priority': 'High',
                    'reason': f'{skill} is essential for most tech roles'
                })
        
        if experience_level in ['Mid', 'Senior']:
            for skill in advanced_skills:
                if skill not in skills:
                    gaps.append({
                        'skill': skill,
                        'priority': 'Medium',
                        'reason': f'{skill} is valuable for {experience_level.lower()}-level positions'
                    })
    
    elif career_type == 'government':
        essential_skills = ['Current Affairs', 'Quantitative Aptitude', 'Reasoning', 'English']
        
        for skill in essential_skills:
            if skill not in skills:
                gaps.append({
                    'skill': skill,
                    'priority': 'High',
                    'reason': f'{skill} is crucial for government exams'
                })
    
    elif career_type == 'nontech':
        essential_skills = ['Communication', 'Project Management', 'Leadership', 'Analytics']
        
        for skill in essential_skills:
            if skill not in skills:
                gaps.append({
                    'skill': skill,
                    'priority': 'High',
                    'reason': f'{skill} is important for business roles'
                })
    
    return gaps[:5]  # Return top 5 gaps

def calculate_role_matches(skills, career_type, experience_level):
    """Calculate match scores for different roles"""
    matches = []
    
    # Sample role matching logic
    if career_type == 'tech':
        roles = [
            {'name': 'Software Developer', 'required_skills': ['Programming', 'Problem Solving', 'Git']},
            {'name': 'Data Analyst', 'required_skills': ['SQL', 'Python', 'Analytics']},
            {'name': 'DevOps Engineer', 'required_skills': ['AWS', 'Docker', 'Linux']}
        ]
    elif career_type == 'government':
        roles = [
            {'name': 'Bank PO', 'required_skills': ['Banking', 'Quantitative Aptitude', 'Reasoning']},
            {'name': 'Civil Services', 'required_skills': ['General Knowledge', 'Current Affairs', 'Essay Writing']},
            {'name': 'SSC Officer', 'required_skills': ['English', 'Quantitative Aptitude', 'Reasoning']}
        ]
    else:  # nontech
        roles = [
            {'name': 'Business Analyst', 'required_skills': ['Analytics', 'Communication', 'Problem Solving']},
            {'name': 'Marketing Manager', 'required_skills': ['Marketing', 'Communication', 'Strategy']},
            {'name': 'HR Manager', 'required_skills': ['HR', 'Communication', 'Leadership']}
        ]
    
    for role in roles:
        skill_matches = sum(1 for req_skill in role['required_skills'] 
                          if any(req_skill.lower() in skill.lower() for skill in skills))
        match_percentage = (skill_matches / len(role['required_skills'])) * 100
        
        # Adjust based on experience level
        if experience_level == 'Senior' and match_percentage > 60:
            match_percentage = min(95, match_percentage + 10)
        elif experience_level == 'Entry' and match_percentage > 80:
            match_percentage = min(85, match_percentage - 5)
        
        matches.append({
            'role': role['name'],
            'match': round(match_percentage),
            'matched_skills': skill_matches,
            'total_required': len(role['required_skills'])
        })
    
    return sorted(matches, key=lambda x: x['match'], reverse=True)

def generate_actionable_insights(skills, experience_level, career_type, skill_gaps):
    """Generate actionable insights for career development"""
    insights = []
    
    # Skill development insights
    if skill_gaps:
        high_priority_gaps = [gap for gap in skill_gaps if gap['priority'] == 'High']
        if high_priority_gaps:
            insights.append({
                'category': 'Skill Development',
                'insight': f"Focus on developing {', '.join([gap['skill'] for gap in high_priority_gaps[:3]])} to strengthen your profile",
                'action': 'Enroll in online courses or certification programs'
            })
    
    # Experience level insights
    if experience_level == 'Entry':
        insights.append({
            'category': 'Experience Building',
            'insight': 'Build practical experience through projects and internships',
            'action': 'Create portfolio projects and contribute to open source'
        })
    elif experience_level == 'Mid':
        insights.append({
            'category': 'Career Growth',
            'insight': 'Consider leadership roles and advanced certifications',
            'action': 'Seek mentorship opportunities and lead team projects'
        })
    
    # Career-specific insights
    if career_type == 'tech':
        insights.append({
            'category': 'Technical Growth',
            'insight': 'Stay updated with latest technologies and frameworks',
            'action': 'Follow tech blogs, attend conferences, and practice coding regularly'
        })
    elif career_type == 'government':
        insights.append({
            'category': 'Exam Preparation',
            'insight': 'Consistent preparation and current affairs knowledge are crucial',
            'action': 'Create a study schedule and practice mock tests regularly'
        })
    
    return insights

def generate_overall_assessment(profile_strength, skills, experience_level, career_type):
    """Generate comprehensive overall assessment"""
    
    assessment = {
        'summary': f"Your profile shows {profile_strength['level'].lower()} potential in {career_type} careers.",
        'strengths': [],
        'areas_for_improvement': [],
        'next_steps': []
    }
    
    # Identify strengths
    if len(skills) >= 10:
        assessment['strengths'].append("Diverse skill set across multiple domains")
    if experience_level in ['Mid', 'Senior', 'Expert']:
        assessment['strengths'].append(f"Solid {experience_level.lower()}-level professional experience")
    if profile_strength['score'] >= 70:
        assessment['strengths'].append("Well-rounded professional profile")
    
    # Areas for improvement
    if len(skills) < 5:
        assessment['areas_for_improvement'].append("Expand technical skill repertoire")
    if experience_level == 'Entry':
        assessment['areas_for_improvement'].append("Gain more hands-on experience")
    if profile_strength['score'] < 50:
        assessment['areas_for_improvement'].append("Strengthen overall professional profile")
    
    # Next steps
    if career_type == 'tech':
        assessment['next_steps'].append("Build a strong portfolio showcasing your projects")
        assessment['next_steps'].append("Stay current with industry trends and technologies")
    elif career_type == 'government':
        assessment['next_steps'].append("Focus on exam-specific preparation and current affairs")
        assessment['next_steps'].append("Practice quantitative aptitude and reasoning regularly")
    else:
        assessment['next_steps'].append("Develop leadership and communication skills")
        assessment['next_steps'].append("Gain industry-specific knowledge and certifications")
    
    return assessment
