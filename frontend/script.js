class CareerPathAI {
    constructor() {
        // State properties
        this.currentMode = 'quick';
        this.selectedCareerType = 'tech';
        this.selectedDomain = null;
        this.skillAssessment = {};
        this.analysisResults = null;
        this.extractedSkills = [];

        this.init();
    }

    // --- INITIALIZATION ---
    init() {
        this.setupEventListeners();
        this.updateDomainOptions();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => this.handleNavLink(e));
        });

        // Career Type Selection
        document.querySelectorAll('.career-type-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchCareerType(e.currentTarget.dataset.type));
        });

        // Assessment Mode Switching
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchMode(e.currentTarget.dataset.mode));
        });

        // Domain Selection (delegated)
        document.getElementById('domainOptionsContainer').addEventListener('click', (e) => {
            const domainOption = e.target.closest('.domain-option');
            if (domainOption) {
                this.selectDomain(domainOption.dataset.domain);
            }
        });

        // Detailed Assessment Proficiency (delegated)
        document.getElementById('skillCategories').addEventListener('click', (e) => {
            if (e.target.classList.contains('proficiency-level')) {
                this.updateProficiency(e.target);
            }
        });
        
        // Resume Upload
        const resumeUploadArea = document.getElementById('resumeUploadArea');
        const resumeFile = document.getElementById('resumeFile');
        resumeUploadArea.addEventListener('click', () => resumeFile.click());
        resumeUploadArea.addEventListener('dragover', (e) => { e.preventDefault(); resumeUploadArea.classList.add('dragover'); });
        resumeUploadArea.addEventListener('dragleave', () => resumeUploadArea.classList.remove('dragover'));
        resumeUploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            resumeUploadArea.classList.remove('dragover');
            if (e.dataTransfer.files.length) {
                this.handleResumeFile(e.dataTransfer.files[0]);
            }
        });
        resumeFile.addEventListener('change', (e) => {
            if (e.target.files.length) {
                this.handleResumeFile(e.target.files[0]);
            }
        });

        // Main Action Buttons
        document.getElementById('analyzeBtn').addEventListener('click', () => this.performAnalysis());
        document.getElementById('clearBtn').addEventListener('click', () => this.resetAssessment());
        
        // Chat
        document.getElementById('sendMessage').addEventListener('click', () => this.sendChatMessage());
        document.getElementById('chatInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendChatMessage();
        });
        document.querySelector('.chat-suggestions').addEventListener('click', (e) => {
            if (e.target.classList.contains('suggestion-btn')) {
                this.sendSuggestedMessage(e.target.textContent);
            }
        });
    }

    // --- UI SWITCHING & NAVIGATION ---
    handleNavLink(e) {
        e.preventDefault();
        const sectionId = e.target.getAttribute('href').substring(1);
        this.navigateToSection(sectionId);
    }

    navigateToSection(sectionId) {
        document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
        document.querySelector(`.nav-link[href="#${sectionId}"]`)?.classList.add('active');

        document.querySelectorAll('.section').forEach(section => section.style.display = 'none');
        document.getElementById(sectionId).style.display = 'block';

        if (sectionId === 'roadmap') this.generateRoadmap();
        else if (sectionId === 'insights') this.displayInsights();
        else if (sectionId === 'chat') this.initializeChat();
    }

    switchCareerType(type) {
        this.selectedCareerType = type;
        this.selectedDomain = null;
        this.skillAssessment = {};

        document.querySelectorAll('.career-type-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-type="${type}"]`).classList.add('active');

        this.updateDomainOptions();
        if (this.currentMode === 'detailed') {
            this.loadSkillCategories();
        }
    }

    switchMode(mode) {
        this.currentMode = mode;
        document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-mode="${mode}"]`).classList.add('active');

        // Hide all input panels first
        ['quickInput', 'detailedAssessment', 'resumeAnalysis'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.style.display = 'none';
        });

        // FIX: Create a mapping from the button's 'mode' to the panel's actual ID.
        const panelIdMap = {
            quick: 'quickInput',
            detailed: 'detailedAssessment',
            resume: 'resumeAnalysis'
        };

        // Use the map to find the correct ID to show.
        const idToShow = panelIdMap[mode];
        const elementToShow = document.getElementById(idToShow);
        
        if (elementToShow) {
            elementToShow.style.display = 'block';
        }

        if (mode === 'detailed') {
            this.loadSkillCategories();
        }
    }
    // --- DATA & CONTENT MANAGEMENT ---
    getSkillCategoriesForDomain() {
        const skillsData = {
            tech: [
                { name: 'Programming Languages', icon: 'fas fa-code', skills: ['JavaScript', 'Python', 'Java', 'C++', 'TypeScript', 'Go'] },
                { name: 'Frameworks & Libraries', icon: 'fas fa-cogs', skills: ['React', 'Node.js', 'Spring Boot', 'Django', 'Vue.js', 'Angular'] },
                { name: 'Databases & Cloud', icon: 'fas fa-database', skills: ['SQL', 'MongoDB', 'AWS', 'Docker', 'Kubernetes', 'PostgreSQL'] }
            ],
            nontech: [
                { name: 'Business & Strategy', icon: 'fas fa-briefcase', skills: ['Project Management', 'Strategic Planning', 'Business Analysis', 'Financial Modeling'] },
                { name: 'Marketing & Sales', icon: 'fas fa-bullhorn', skills: ['Digital Marketing', 'SEO', 'Content Marketing', 'CRM'] },
                { name: 'Communication', icon: 'fas fa-comments', skills: ['Public Speaking', 'Presentation Skills', 'Negotiation', 'Writing'] }
            ],
            government: [
                { name: 'Core Academic Subjects', icon: 'fas fa-book', skills: ['Mathematics', 'English Language', 'General Science', 'Computer Awareness', 'Environmental Studies', 'General Knowledge'] },
                { name: 'Aptitude & Reasoning', icon: 'fas fa-brain', skills: ['Quantitative Aptitude', 'Logical Reasoning', 'Verbal Reasoning', 'Data Interpretation', 'Analytical Ability', 'Problem Solving'] },
                { name: 'Social Sciences', icon: 'fas fa-landmark', skills: ['Indian Polity', 'Indian Constitution', 'Modern History', 'Ancient History', 'Geography', 'Economics', 'Sociology', 'Public Administration'] },
                { name: 'Current Affairs & GK', icon: 'fas fa-newspaper', skills: ['Current Affairs', 'Static GK', 'Sports & Awards', 'Books & Authors', 'Important Dates', 'Science & Technology News'] },
                { name: 'Specialized Knowledge', icon: 'fas fa-graduation-cap', skills: ['Banking Awareness', 'Financial Markets', 'Insurance', 'Railway Technical', 'Defense Studies', 'Legal Knowledge', 'Teaching Methodology'] },
                { name: 'Language & Communication', icon: 'fas fa-comments', skills: ['Hindi Language', 'Regional Languages', 'Essay Writing', 'Comprehension', 'Grammar', 'Communication Skills'] }
            ]
        };
        return skillsData[this.selectedCareerType];
    }
    
    getDomainsForCareerType() {
        const domains = {
            tech: [
                { id: 'web', name: 'Web Development', icon: 'fas fa-code' },
                { id: 'data', name: 'Data Science', icon: 'fas fa-chart-bar' },
                { id: 'ml', name: 'AI/ML', icon: 'fas fa-brain' },
                { id: 'cloud', name: 'Cloud/DevOps', icon: 'fas fa-cloud' },
                { id: 'mobile', name: 'Mobile Dev', icon: 'fas fa-mobile-alt' },
                { id: 'security', name: 'Cybersecurity', icon: 'fas fa-shield-alt' },
                { id: 'uiux', name: 'UI/UX Design', icon: 'fas fa-palette' },
                { id: 'qa', name: 'QA/Testing', icon: 'fas fa-bug' }
            ],
            nontech: [
                { id: 'marketing', name: 'Marketing & Sales', icon: 'fas fa-bullhorn' },
                { id: 'finance', name: 'Finance', icon: 'fas fa-dollar-sign' },
                { id: 'hr', name: 'Human Resources', icon: 'fas fa-users' },
                { id: 'consulting', name: 'Consulting', icon: 'fas fa-handshake' },
                { id: 'operations', name: 'Operations', icon: 'fas fa-cogs' },
                { id: 'legal', name: 'Legal', icon: 'fas fa-gavel' },
                { id: 'creative', name: 'Creative & Design', icon: 'fas fa-paint-brush' },
                { id: 'retail', name: 'Retail', icon: 'fas fa-store' }
            ],
            government: [
                { id: 'ias', name: 'Civil Services (UPSC)', icon: 'fas fa-user-tie' },
                { id: 'banking', name: 'Banking (IBPS/SBI)', icon: 'fas fa-university' },
                { id: 'ssc', name: 'SSC (CGL/CHSL)', icon: 'fas fa-clipboard-list' },
                { id: 'defense', name: 'Defense Services', icon: 'fas fa-shield-alt' },
                { id: 'railway', name: 'Railways', icon: 'fas fa-train' },
                { id: 'psu', name: 'PSU Jobs', icon: 'fas fa-industry' },
                { id: 'teaching', name: 'Teaching', icon: 'fas fa-chalkboard-teacher' },
                { id: 'judiciary', name: 'Judiciary', icon: 'fas fa-balance-scale' }
            ]
        };
        return domains[this.selectedCareerType];
    }

    loadSkillCategories() {
        const container = document.getElementById('skillCategories');
        const skillCategories = this.getSkillCategoriesForDomain();
        container.innerHTML = skillCategories.map(category => `
            <div class="skill-category">
                <h4><i class="${category.icon}"></i> ${category.name}</h4>
                <div class="skills-grid">
                    ${category.skills.map(skill => `
                        <div class="skill-item">
                            <span class="skill-name">${skill}</span>
                            <div class="proficiency-levels">
                                ${[1, 2, 3, 4, 5].map(level => `
                                    <button class="proficiency-level" data-level="${level}" data-skill="${skill}">${level}</button>
                                `).join('')}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `).join('');
    }
    
    updateDomainOptions() {
        const container = document.getElementById('domainOptionsContainer');
        const domains = this.getDomainsForCareerType();
        container.innerHTML = `<div class="domain-options-grid">
            ${domains.map(domain => `
                <div class="domain-option" data-domain="${domain.id}">
                    <i class="${domain.icon}"></i>
                    <span>${domain.name}</span>
                </div>
            `).join('')}
        </div>`;
    }

    selectDomain(domainId) {
        const currentlySelected = document.querySelector('.domain-option.selected');
        if (currentlySelected) {
            currentlySelected.classList.remove('selected');
        }

        if (this.selectedDomain === domainId) {
            this.selectedDomain = null; // Toggle off
        } else {
            this.selectedDomain = domainId;
            document.querySelector(`[data-domain="${domainId}"]`).classList.add('selected');
        }
    }
    
    updateProficiency(button) {
        const skill = button.dataset.skill;
        const level = parseInt(button.dataset.level, 10);

        // Update state
        this.skillAssessment[skill] = level;

        // Update UI
        const parent = button.parentElement;
        parent.querySelectorAll('.proficiency-level').forEach(btn => btn.classList.remove('active'));
        for (let i = 1; i <= level; i++) {
            parent.querySelector(`[data-level="${i}"]`).classList.add('active');
        }
    }

    // --- ANALYSIS ---
    async performAnalysis() {
        const resultsWrapper = document.getElementById('resultsWrapper');
        const loading = document.getElementById('loading');
        
        resultsWrapper.style.display = 'block';
        loading.style.display = 'flex';
        document.getElementById('results').style.display = 'none';
        
        try {
            let analysisData = {
                mode: this.currentMode,
                careerType: this.selectedCareerType,
                domain: this.selectedDomain,
                skills: []
            };

            if (this.currentMode === 'quick') {
                const skillsText = document.getElementById('skillsInput').value;
                if (!skillsText.trim()) throw new Error('Please enter your skills.');
                analysisData.skills = skillsText;
            } else if (this.currentMode === 'detailed') {
                const skillsList = Object.entries(this.skillAssessment).map(([skill, proficiency]) => ({ skill, proficiency }));
                if (skillsList.length === 0) throw new Error('Please rate at least one skill.');
                analysisData.skills = skillsList;
            } else if (this.currentMode === 'resume') {
                if (this.extractedSkills.length === 0) throw new Error('Please upload a resume to extract skills.');
                analysisData.skills = this.extractedSkills.join(', ');
            }

            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(analysisData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Analysis failed. Please try again.');
            }

            this.analysisResults = await response.json();
            this.displayResults(this.analysisResults);

        } catch (error) {
            this.showNotification(error.message, 'error');
            resultsWrapper.style.display = 'none';
        } finally {
            loading.style.display = 'none';
        }
    }

    async handleResumeFile(file) {
        if (!file) return;
        this.showNotification(`Analyzing ${file.name}...`, 'info');
        
        // This is a mock analysis. In a real app, you would send the file to the backend.
        // For this demo, we use a mock response based on the backend logic.
        try {
            const mockText = "Experience with Python, JavaScript, and React. Managed projects using Agile. Also skilled in SQL and AWS.";
            const response = await fetch('/api/resume/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: mockText, careerType: this.selectedCareerType })
            });
            if (!response.ok) throw new Error('Resume analysis failed.');

            const data = await response.json();
            this.extractedSkills = data.skills || [];

            document.getElementById('extractedSkills').innerHTML = this.extractedSkills.map(s => `<span class="skill-tag">${s}</span>`).join('');
            document.getElementById('resumeAnalysisResults').style.display = 'block';
            this.showNotification('Skills extracted successfully!', 'success');
        } catch (error) {
            this.showNotification(error.message, 'error');
        }
    }
    
    // --- DISPLAY RESULTS ---
    displayResults(results) {
        document.getElementById('results').style.display = 'block';
        document.getElementById('resultsWrapper').scrollIntoView({ behavior: 'smooth' });

        this.displayCareerMatches(results.bestRoles || []);
        this.displaySkillAnalysis(results.userSkills || [], results.skillGaps || []);
        this.displayLearningResources(results.learningPlan || []);
        this.displayAIAdvice(results.aiAdvice || '');
    }
    
    displayCareerMatches(roles) {
        const container = document.getElementById('careerList');
        if (!roles.length) {
            container.innerHTML = '<p>No career matches found. Try adding more skills.</p>';
            return;
        }
        container.innerHTML = roles.map(role => `
            <div class="career-match">
                <div class="match-header">
                    <h4>${role.title}</h4>
                    <span class="match-score">${role.score}% Match</span>
                </div>
                <p>${role.description}</p>
                <div class="skill-tags">
                    ${role.skills.map(s => `<span class="skill-tag">${s}</span>`).join('')}
                </div>
            </div>
        `).join('');
    }

    displaySkillAnalysis(userSkills, skillGaps) {
        document.getElementById('userSkills').innerHTML = userSkills.map(s => `<span class="skill-tag">${s}</span>`).join('') || '<p>No skills found.</p>';
        document.getElementById('skillGaps').innerHTML = skillGaps.map(s => `<span class="skill-tag">${s}</span>`).join('') || '<p>No skill gaps identified. Great job!</p>';
    }

    displayLearningResources(learningPlan) {
        const container = document.getElementById('learningResources');
        if (!learningPlan.length) {
            container.innerHTML = '<p>No specific resources to recommend.</p>';
            return;
        }
        container.innerHTML = learningPlan.map(cat => `
            <div class="resource-category">
                <h4>${cat.category}</h4>
                <div class="resource-list">
                    ${cat.resources.map(res => `<a href="${res.url}" target="_blank" class="resource-link"><i class="fas fa-external-link-alt"></i> ${res.title}</a>`).join('')}
                </div>
            </div>
        `).join('');
    }

    displayAIAdvice(advice) {
        const adviceContainer = document.getElementById('aiAdvice');
        adviceContainer.innerHTML = ''; // Clear previous content

        // FIX: Securely render AI advice to prevent XSS
        const paragraphs = advice.split('\n').filter(p => p.trim() !== '');
        paragraphs.forEach(text => {
            const p = document.createElement('p');
            p.textContent = text;
            adviceContainer.appendChild(p);
        });
    }
    
    generateRoadmap() {
        const container = document.querySelector('.roadmap-timeline');
        if (!container) return;

        if (!this.analysisResults || !this.analysisResults.bestRoles.length) {
            container.innerHTML = `
                <div class="roadmap-placeholder" style="text-align: center; padding: 3rem;">
                    <i class="fas fa-map-signs" style="font-size: 3rem; color: var(--primary); margin-bottom: 1rem;"></i>
                    <h3>Complete Your Skill Assessment First</h3>
                    <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">A personalized roadmap will be generated here after you analyze your skills.</p>
                    <button class="btn-primary" onclick="window.careerPathAI.navigateToSection('assessment')">
                        Go to Assessment
                    </button>
                </div>
            `;
            return;
        }

        const topRole = this.analysisResults.bestRoles[0];
        const roadmap = this.createCareerRoadmap(topRole);
        container.innerHTML = roadmap.map((milestone, index) => `
            <div class="roadmap-milestone">
                <div class="milestone-marker"><span>${index + 1}</span></div>
                <div class="milestone-content">
                    <h3>${milestone.title}</h3>
                    <p>${milestone.description}</p>
                    <ul class="milestone-tasks">
                        ${milestone.tasks.map(task => `<li>${task}</li>`).join('')}
                    </ul>
                    <div class="milestone-timeline">${milestone.timeline}</div>
                </div>
            </div>
        `).join('');
    }

    createCareerRoadmap(role) {
        const careerType = this.selectedCareerType;
        const roleTitle = role.title;
        const skillGaps = role.missing || [];
        
        if (careerType === 'government') {
            return this.createGovernmentRoadmap(roleTitle, skillGaps);
        } else if (careerType === 'nontech') {
            return this.createNonTechRoadmap(roleTitle, skillGaps);
        } else {
            return this.createTechRoadmap(roleTitle, skillGaps);
        }
    }

    createTechRoadmap(roleTitle, skillGaps) {
        const roadmap = [
            {
                title: "Foundation Phase",
                description: "Build core technical skills and understanding",
                timeline: "Months 1-3",
                tasks: [
                    "Master fundamental programming concepts",
                    "Set up development environment and tools",
                    "Learn version control (Git) basics",
                    "Complete online coding tutorials and exercises"
                ]
            },
            {
                title: "Skill Development",
                description: "Focus on role-specific technologies and frameworks",
                timeline: "Months 4-8",
                tasks: [
                    `Learn key technologies: ${skillGaps.slice(0, 3).join(', ')}`,
                    "Build 2-3 personal projects showcasing your skills",
                    "Contribute to open-source projects",
                    "Join tech communities and forums"
                ]
            },
            {
                title: "Portfolio Building",
                description: "Create impressive projects and establish online presence",
                timeline: "Months 9-12",
                tasks: [
                    "Develop a comprehensive portfolio website",
                    "Create advanced projects demonstrating expertise",
                    "Write technical blog posts or documentation",
                    "Network with professionals in your field"
                ]
            },
            {
                title: "Job Preparation",
                description: "Prepare for interviews and job applications",
                timeline: "Months 13-15",
                tasks: [
                    "Practice coding interviews and technical questions",
                    "Optimize your resume and LinkedIn profile",
                    "Apply to relevant positions and internships",
                    "Prepare for system design and behavioral interviews"
                ]
            },
            {
                title: "Career Launch",
                description: "Land your first role and continue growing",
                timeline: "Month 16+",
                tasks: [
                    `Secure a position as ${roleTitle}`,
                    "Excel in your first 90 days on the job",
                    "Seek mentorship and feedback",
                    "Plan for career advancement and specialization"
                ]
            }
        ];
        return roadmap;
    }

    createNonTechRoadmap(roleTitle, skillGaps) {
        const roadmap = [
            {
                title: "Industry Research",
                description: "Understand the field and identify opportunities",
                timeline: "Months 1-2",
                tasks: [
                    "Research industry trends and key players",
                    "Identify required skills and qualifications",
                    "Network with professionals in the field",
                    "Attend industry events and webinars"
                ]
            },
            {
                title: "Skill Building",
                description: "Develop essential competencies for your target role",
                timeline: "Months 3-6",
                tasks: [
                    `Focus on key skills: ${skillGaps.slice(0, 3).join(', ')}`,
                    "Pursue relevant certifications or courses",
                    "Gain practical experience through projects or volunteering",
                    "Develop strong communication and presentation skills"
                ]
            },
            {
                title: "Experience Gaining",
                description: "Build relevant experience and credibility",
                timeline: "Months 7-12",
                tasks: [
                    "Seek internships or entry-level positions",
                    "Take on freelance projects or consulting work",
                    "Build a professional portfolio or case studies",
                    "Establish thought leadership through content creation"
                ]
            },
            {
                title: "Professional Development",
                description: "Enhance your profile and expand your network",
                timeline: "Months 13-18",
                tasks: [
                    "Join professional associations and organizations",
                    "Attend conferences and networking events",
                    "Seek mentorship from industry veterans",
                    "Consider advanced education or specialized training"
                ]
            },
            {
                title: "Career Advancement",
                description: "Secure your target role and plan for growth",
                timeline: "Month 19+",
                tasks: [
                    `Land a position as ${roleTitle}`,
                    "Excel in your role and seek additional responsibilities",
                    "Build internal and external professional relationships",
                    "Plan for long-term career progression"
                ]
            }
        ];
        return roadmap;
    }

    createGovernmentRoadmap(roleTitle, skillGaps) {
        const roadmap = [
            {
                title: "Exam Preparation Foundation",
                description: "Build strong fundamentals for government exams",
                timeline: "Months 1-4",
                tasks: [
                    "Complete NCERT books (6th-12th) for all subjects",
                    "Start daily current affairs reading (The Hindu)",
                    "Build strong foundation in quantitative aptitude",
                    "Develop basic reasoning and logical thinking skills"
                ]
            },
            {
                title: "Focused Study Phase",
                description: "Intensive preparation for target examinations",
                timeline: "Months 5-10",
                tasks: [
                    `Master key subjects: ${skillGaps.slice(0, 3).join(', ')}`,
                    "Practice previous year question papers extensively",
                    "Join test series and mock examinations",
                    "Develop answer writing skills for descriptive papers"
                ]
            },
            {
                title: "Advanced Preparation",
                description: "Fine-tune skills and exam strategy",
                timeline: "Months 11-15",
                tasks: [
                    "Focus on weak areas identified through mock tests",
                    "Practice time management and exam strategies",
                    "Stay updated with latest current affairs and policies",
                    "Prepare for interview and personality test rounds"
                ]
            },
            {
                title: "Exam Execution",
                description: "Appear for examinations and optimize performance",
                timeline: "Months 16-18",
                tasks: [
                    "Appear for preliminary examinations",
                    "Clear mains examination with strong performance",
                    "Prepare thoroughly for interview rounds",
                    "Maintain physical and mental fitness"
                ]
            },
            {
                title: "Service Commencement",
                description: "Begin your government service career",
                timeline: "Month 19+",
                tasks: [
                    `Secure selection as ${roleTitle}`,
                    "Complete training programs and orientation",
                    "Excel in probationary period",
                    "Plan for career progression within government service"
                ]
            }
        ];
        return roadmap;
    }
    
    displayInsights() {
        const trendsContainer = document.querySelector('.trends-list');
        const recommendationsContainer = document.querySelector('.recommendations-list');

        if (!this.analysisResults || !this.analysisResults.bestRoles.length) {
            const placeholder = `
                <div class="insights-placeholder" style="text-align: center; padding: 2rem;">
                    <i class="fas fa-lightbulb" style="font-size: 2rem; color: var(--primary); margin-bottom: 1rem;"></i>
                    <p style="color: var(--text-secondary);">Complete the skill assessment to view personalized market insights and recommendations.</p>
                    <button class="btn-primary" onclick="window.careerPathAI.navigateToSection('assessment')" style="margin-top: 1rem;">
                        Start Assessment
                    </button>
                </div>
            `;
            if (trendsContainer) trendsContainer.innerHTML = placeholder;
            if (recommendationsContainer) recommendationsContainer.innerHTML = '';
            return;
        }

        const topRole = this.analysisResults.bestRoles[0];
        const skillGaps = this.analysisResults.skillGaps || [];
        const careerType = this.selectedCareerType;
        
        // Generate market trends based on career type and role
        const trends = this.generateMarketTrends(topRole, careerType);
        trendsContainer.innerHTML = trends.map(trend => `
            <div class="trend-item">
                <div class="trend-icon"><i class="${trend.icon}"></i></div>
                <div class="trend-content">
                    <h4>${trend.title}</h4>
                    <p>${trend.description}</p>
                    <div class="trend-stats">
                        <span class="stat-item">
                            <i class="fas fa-chart-line"></i>
                            ${trend.growth}
                        </span>
                        <span class="stat-item">
                            <i class="fas fa-dollar-sign"></i>
                            ${trend.salary}
                        </span>
                    </div>
                </div>
            </div>
        `).join('');

        // Generate personalized recommendations
        const recommendations = this.generateRecommendations(topRole, skillGaps, careerType);
        if (recommendationsContainer) {
            recommendationsContainer.innerHTML = recommendations.map(rec => `
                <div class="recommendation-item">
                    <div class="rec-icon"><i class="${rec.icon}"></i></div>
                    <div class="rec-content">
                        <h4>${rec.title}</h4>
                        <p>${rec.description}</p>
                        <div class="rec-actions">
                            ${rec.actions.map(action => `
                                <a href="${action.url}" target="_blank" class="rec-action-btn">
                                    <i class="${action.icon}"></i> ${action.text}
                                </a>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `).join('');
        }
    }

    generateMarketTrends(role, careerType) {
        const roleTitle = role.title;
        
        if (careerType === 'government') {
            return [
                {
                    icon: 'fas fa-landmark',
                    title: `${roleTitle} - Stable Career Path`,
                    description: 'Government positions offer excellent job security, regular promotions, and comprehensive benefits.',
                    growth: '+15% openings annually',
                    salary: '₹4-12 LPA'
                },
                {
                    icon: 'fas fa-users',
                    title: 'Digital Government Initiative',
                    description: 'Government is increasingly adopting digital technologies, creating new opportunities for tech-savvy candidates.',
                    growth: '+25% digital roles',
                    salary: '₹6-15 LPA'
                },
                {
                    icon: 'fas fa-graduation-cap',
                    title: 'Skill-Based Recruitment',
                    description: 'Modern government recruitment emphasizes practical skills alongside traditional exam performance.',
                    growth: '+20% skill emphasis',
                    salary: 'Merit-based pay'
                }
            ];
        } else if (careerType === 'nontech') {
            return [
                {
                    icon: 'fas fa-briefcase',
                    title: `${roleTitle} Market Demand`,
                    description: 'Strong demand for experienced professionals in traditional business roles with digital literacy.',
                    growth: '+18% job growth',
                    salary: '₹5-20 LPA'
                },
                {
                    icon: 'fas fa-chart-line',
                    title: 'Remote Work Opportunities',
                    description: 'Many non-tech roles now offer flexible work arrangements, expanding job opportunities.',
                    growth: '+40% remote positions',
                    salary: '₹6-25 LPA'
                },
                {
                    icon: 'fas fa-handshake',
                    title: 'Consulting & Freelancing',
                    description: 'Growing trend of businesses hiring specialized consultants for project-based work.',
                    growth: '+30% freelance market',
                    salary: '₹500-2000/hour'
                }
            ];
        } else {
            return [
                {
                    icon: 'fas fa-rocket',
                    title: `${roleTitle} High Demand`,
                    description: 'Tech roles continue to show strong growth with competitive salaries and excellent career prospects.',
                    growth: '+22% job growth',
                    salary: '₹8-35 LPA'
                },
                {
                    icon: 'fas fa-robot',
                    title: 'AI & Automation Boom',
                    description: 'Artificial Intelligence and automation are creating new opportunities across all tech domains.',
                    growth: '+45% AI roles',
                    salary: '₹12-50 LPA'
                },
                {
                    icon: 'fas fa-globe',
                    title: 'Global Remote Opportunities',
                    description: 'Tech professionals can now work for international companies remotely, accessing global salary scales.',
                    growth: '+60% remote jobs',
                    salary: '$30-120k USD'
                }
            ];
        }
    }

    generateRecommendations(role, skillGaps, careerType) {
        const recommendations = [];
        
        if (skillGaps.length > 0) {
            if (careerType === 'government') {
                recommendations.push({
                    icon: 'fas fa-book-open',
                    title: 'Focus on Core Subjects',
                    description: `Strengthen your preparation in: ${skillGaps.slice(0, 3).join(', ')}. These are critical for government exam success.`,
                    actions: [
                        { icon: 'fas fa-external-link-alt', text: 'NCERT Books', url: 'https://ncert.nic.in/textbook.php' },
                        { icon: 'fas fa-newspaper', text: 'Current Affairs', url: 'https://www.thehindu.com/' }
                    ]
                });
                
                recommendations.push({
                    icon: 'fas fa-clock',
                    title: 'Structured Study Plan',
                    description: 'Create a daily 8-10 hour study schedule with regular breaks and mock tests.',
                    actions: [
                        { icon: 'fas fa-calendar', text: 'Study Planner', url: 'https://www.studyplanner.in/' },
                        { icon: 'fas fa-question-circle', text: 'Mock Tests', url: 'https://testbook.com/' }
                    ]
                });
            } else if (careerType === 'nontech') {
                recommendations.push({
                    icon: 'fas fa-certificate',
                    title: 'Pursue Relevant Certifications',
                    description: `Build credibility with certifications in: ${skillGaps.slice(0, 3).join(', ')}. Industry certifications boost your profile significantly.`,
                    actions: [
                        { icon: 'fas fa-graduation-cap', text: 'Coursera', url: 'https://www.coursera.org/' },
                        { icon: 'fas fa-linkedin', text: 'LinkedIn Learning', url: 'https://www.linkedin.com/learning/' }
                    ]
                });
                
                recommendations.push({
                    icon: 'fas fa-network-wired',
                    title: 'Build Professional Network',
                    description: 'Connect with industry professionals and join relevant associations to expand opportunities.',
                    actions: [
                        { icon: 'fas fa-users', text: 'Industry Events', url: 'https://www.eventbrite.com/' },
                        { icon: 'fas fa-handshake', text: 'Professional Groups', url: 'https://www.linkedin.com/groups/' }
                    ]
                });
            } else {
                recommendations.push({
                    icon: 'fas fa-code',
                    title: 'Master Key Technologies',
                    description: `Focus on learning: ${skillGaps.slice(0, 3).join(', ')}. These skills are in high demand and will boost your career prospects.`,
                    actions: [
                        { icon: 'fas fa-laptop-code', text: 'freeCodeCamp', url: 'https://www.freecodecamp.org/' },
                        { icon: 'fas fa-play', text: 'YouTube Tutorials', url: 'https://www.youtube.com/' }
                    ]
                });
                
                recommendations.push({
                    icon: 'fas fa-project-diagram',
                    title: 'Build Portfolio Projects',
                    description: 'Create 2-3 impressive projects showcasing your skills. A strong portfolio is crucial for landing interviews.',
                    actions: [
                        { icon: 'fas fa-github', text: 'GitHub', url: 'https://github.com/' },
                        { icon: 'fas fa-globe', text: 'Deploy Projects', url: 'https://netlify.com/' }
                    ]
                });
            }
        }
        
        // Add career-specific recommendation
        if (careerType === 'government') {
            recommendations.push({
                icon: 'fas fa-medal',
                title: 'Stay Motivated & Consistent',
                description: 'Government exam preparation is a marathon. Maintain consistency, take care of your health, and stay positive.',
                actions: [
                    { icon: 'fas fa-heart', text: 'Wellness Tips', url: 'https://www.mindful.org/' },
                    { icon: 'fas fa-users', text: 'Study Groups', url: 'https://www.telegram.org/' }
                ]
            });
        } else {
            recommendations.push({
                icon: 'fas fa-comments',
                title: 'Practice Interview Skills',
                description: 'Prepare for technical and behavioral interviews. Practice coding problems and system design questions regularly.',
                actions: [
                    { icon: 'fas fa-code', text: 'LeetCode', url: 'https://leetcode.com/' },
                    { icon: 'fas fa-microphone', text: 'Mock Interviews', url: 'https://pramp.com/' }
                ]
            });
        }
        
        return recommendations;
    }

    // --- CHAT ---
    initializeChat() {
        const container = document.getElementById('chatMessages');
        container.innerHTML = `<div class="message ai-message">
            <div class="message-avatar"><i class="fas fa-robot"></i></div>
            <div class="message-content"><p>Hello! I'm your AI career assistant. Ask me anything!</p></div>
        </div>`;
        
        const suggestions = ["What skills are in demand?", "Compare two career paths", "How do I prepare for an interview?"];
        document.querySelector('.chat-suggestions').innerHTML = suggestions.map(s => `<button class="suggestion-btn">${s}</button>`).join('');
    }
    
    async sendChatMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        if (!message) return;

        this.addMessageToChat(message, 'user');
        input.value = '';
        this.showTypingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    context: {
                        careerType: this.selectedCareerType,
                        domain: this.selectedDomain,
                        skills: this.analysisResults?.userSkills || []
                    }
                })
            });
            if (!response.ok) throw new Error('Chat service is unavailable.');
            const data = await response.json();
            this.addMessageToChat(data.response, 'ai');
        } catch (error) {
            this.addMessageToChat('Sorry, I encountered an error. Please try again.', 'ai');
        } finally {
            this.hideTypingIndicator();
        }
    }
    
    sendSuggestedMessage(message) {
        document.getElementById('chatInput').value = message;
        this.sendChatMessage();
    }

    addMessageToChat(message, sender) {
        const container = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        const avatar = sender === 'ai' ? 'fa-robot' : 'fa-user';

        // FIX: Securely render chat messages
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';

        const paragraphs = message.split('\n').filter(p => p.trim() !== '');
        paragraphs.forEach(text => {
            const p = document.createElement('p');
            p.textContent = text;
            messageContent.appendChild(p);
        });

        messageDiv.innerHTML = `<div class="message-avatar"><i class="fas ${avatar}"></i></div>`;
        messageDiv.appendChild(messageContent);
        
        container.appendChild(messageDiv);
        container.scrollTop = container.scrollHeight;
    }

    showTypingIndicator() {
        this.hideTypingIndicator(); // Ensure no duplicates
        const container = document.getElementById('chatMessages');
        const indicator = document.createElement('div');
        indicator.id = 'typingIndicator';
        indicator.className = 'message ai-message typing-indicator';
        indicator.innerHTML = `
            <div class="message-avatar"><i class="fas fa-robot"></i></div>
            <div class="message-content"><p>AI is typing...</p></div>`;
        container.appendChild(indicator);
        container.scrollTop = container.scrollHeight;
    }
    
    hideTypingIndicator() {
        document.getElementById('typingIndicator')?.remove();
    }

    // --- UTILITIES ---
    resetAssessment() {
        this.currentMode = 'quick';
        this.selectedCareerType = 'tech';
        this.selectedDomain = null;
        this.skillAssessment = {};
        this.analysisResults = null;
        this.extractedSkills = [];

        // Reset UI elements to default state
        document.getElementById('skillsInput').value = '';
        document.getElementById('resumeFile').value = '';
        document.getElementById('resumeAnalysisResults').style.display = 'none';
        
        this.switchCareerType('tech');
        this.switchMode('quick');

        document.getElementById('resultsWrapper').style.display = 'none';
        this.navigateToSection('assessment');
        window.scrollTo({ top: 0, behavior: 'smooth' });
        this.showNotification('Assessment has been reset.', 'info');
    }

    showNotification(message, type = 'info') {
        const colors = { success: '#10b981', error: '#ef4444', info: '#3b82f6' };
        const notification = document.createElement('div');
        notification.textContent = message;
        Object.assign(notification.style, {
            position: 'fixed', top: '20px', right: '20px', padding: '1rem 1.5rem',
            borderRadius: '8px', color: 'white', fontWeight: '500', zIndex: '10001',
            backgroundColor: colors[type] || colors.info,
            transform: 'translateX(120%)', transition: 'transform 0.3s ease-in-out'
        });
        document.body.appendChild(notification);
        setTimeout(() => notification.style.transform = 'translateX(0)', 10);
        setTimeout(() => {
            notification.style.transform = 'translateX(120%)';
            notification.addEventListener('transitionend', () => notification.remove());
        }, 3000);
    }
}

// Initialize the application on DOM content load
document.addEventListener('DOMContentLoaded', () => {
    window.careerPathAI = new CareerPathAI();
});