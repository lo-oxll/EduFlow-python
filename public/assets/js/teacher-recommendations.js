/**
 * Teacher Recommendations Module
 * Displays grade recommendations, student weaknesses, and class insights for teachers
 */

// Global recommendation manager
window.TeacherRecommendationsManager = null;

// Initialize when teacher is logged in
document.addEventListener('DOMContentLoaded', function() {
    // Wait for teacher data to be available
    if (window.currentTeacher) {
        initializeTeacherRecommendations();
    } else {
        // Check periodically for teacher data
        const checkTeacherInterval = setInterval(() => {
            if (window.currentTeacher) {
                clearInterval(checkTeacherInterval);
                initializeTeacherRecommendations();
            }
        }, 500);
        
        // Stop checking after 10 seconds
        setTimeout(() => clearInterval(checkTeacherInterval), 10000);
    }
});

/**
 * Initialize the Teacher Recommendations Manager
 */
function initializeTeacherRecommendations() {
    if (!window.currentTeacher || !window.currentTeacher.id) {
        console.warn('Cannot initialize recommendations: no teacher data');
        return;
    }
    
    window.TeacherRecommendationsManager = new TeacherRecommendationsManager(
        window.currentTeacher.id,
        document.getElementById('gradeRecommendationsContainer')
    );
    
    // Load recommendations
    window.TeacherRecommendationsManager.loadRecommendations();
}

/**
 * Teacher Recommendations Manager Class
 */
class TeacherRecommendationsManager {
    constructor(teacherId, container) {
        this.teacherId = teacherId;
        this.container = container;
        this.recommendations = null;
    }
    
    /**
     * Load recommendations from API
     */
    async loadRecommendations() {
        if (!this.container) return;
        
        try {
            const response = await fetch(`/api/recommendations/teacher?teacher_id=${this.teacherId}`);
            const result = await response.json();
            
            if (result.success) {
                this.recommendations = result;
                this.render();
            } else {
                this.showError(result.error || 'فشل في تحميل التوصيات');
            }
        } catch (error) {
            console.error('Error loading recommendations:', error);
            this.showError('حدث خطأ في الاتصال بالخادم');
        }
    }
    
    /**
     * Render the recommendations UI
     */
    render() {
        if (!this.recommendations) return;
        
        let html = '';
        
        // Class Insights Section
        const classInsights = this.recommendations.class_insights;
        if (classInsights && classInsights.total_students > 0) {
            html += this.renderClassInsights(classInsights);
        }
        
        // Subject Analysis Section
        const subjectsAnalysis = this.recommendations.subjects_analysis;
        if (subjectsAnalysis && Object.keys(subjectsAnalysis).length > 0) {
            html += this.renderSubjectAnalysis(subjectsAnalysis);
        }
        
        // At-Risk Students Section
        const atRiskStudents = this.recommendations.at_risk_students;
        if (atRiskStudents && atRiskStudents.length > 0) {
            html += this.renderAtRiskStudents(atRiskStudents);
        }
        
        // Educational Strategies Section
        const strategies = this.recommendations.strategies;
        if (strategies && strategies.length > 0) {
            html += this.renderStrategies(strategies);
        }
        
        // Empty state
        if (html === '') {
            html = '<div class="recommendations-empty">\n                <i class="fas fa-info-circle"></i>\n                <p>لا توجد بيانات كافية لعرض التوصيات</p>\n            </div>';
        }
        
        this.container.innerHTML = html;
    }
    
    /**
     * Render class insights
     */
    renderClassInsights(insights) {
        const passRateClass = insights.pass_rate >= 70 ? 'success' : (insights.pass_rate >= 50 ? 'warning' : 'danger');
        const overallClass = insights.overall_average >= 70 ? 'success' : (insights.overall_average >= 50 ? 'warning' : 'danger');
        
        let html = `
            <div class="class-insights-section">
                <h4 class="insights-title"><i class="fas fa-chart-pie"></i> نظرة عامة على الفصل</h4>
                <div class="insights-grid">
                    <div class="insight-card-mini">
                        <div class="insight-icon">👥</div>
                        <div class="insight-data">
                            <div class="insight-value">${insights.total_students}</div>
                            <div class="insight-label">إجمالي الطلاب</div>
                        </div>
                    </div>
                    <div class="insight-card-mini">
                        <div class="insight-icon">📊</div>
                        <div class="insight-data">
                            <div class="insight-value ${overallClass}">${insights.overall_average}%</div>
                            <div class="insight-label">المعدل العام</div>
                        </div>
                    </div>
                    <div class="insight-card-mini">
                        <div class="insight-icon">✅</div>
                        <div class="insight-data">
                            <div class="insight-value ${passRateClass}">${insights.pass_rate}%</div>
                            <div class="insight-label">معدل النجاح</div>
                        </div>
                    </div>
                </div>
        `;
        
        // Show subjects needing focus
        if (insights.subjects_need_focus && insights.subjects_need_focus.length > 0) {
            html += `
                <div class="subjects-focus-alert">
                    <i class="fas fa-exclamation-triangle"></i>
                    <strong>المواد التي تحتاج تركيز:</strong>
                    <span>${insights.subjects_need_focus.join('، ')}</span>
                </div>
            `;
        }
        
        html += '</div>';
        return html;
    }
    
    /**
     * Render subject analysis
     */
    renderSubjectAnalysis(subjects) {
        let html = `
            <div class="subject-analysis-section">
                <h4 class="insights-title"><i class="fas fa-book"></i> تحليل الأداء حسب المادة</h4>
                <div class="subject-analysis-grid">
        `;
        
        for (const [subjectName, analysis] of Object.entries(subjects)) {
            const passRateClass = analysis.pass_rate >= 70 ? 'success' : (analysis.pass_rate >= 50 ? 'warning' : 'danger');
            
            html += `
                <div class="subject-analysis-card">
                    <div class="subject-header">
                        <span class="subject-name">${subjectName}</span>
                        <span class="subject-badge ${passRateClass}">${analysis.pass_rate}% نجاح</span>
                    </div>
                    <div class="subject-stats">
                        <div class="stat">
                            <span class="stat-value">${analysis.average_score}</span>
                            <span class="stat-label">المعدل</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value success">${analysis.excellent_count}</span>
                            <span class="stat-label">متفوق</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value warning">${analysis.needs_support_count}</span>
                            <span class="stat-label">يحتاج دعم</span>
                        </div>
                    </div>
                </div>
            `;
        }
        
        html += '</div></div>';
        return html;
    }
    
    /**
     * Render at-risk students
     */
    renderAtRiskStudents(students) {
        let html = `
            <div class="at-risk-section">
                <h4 class="insights-title warning"><i class="fas fa-exclamation-circle"></i> الطلاب الذين يحتاجون اهتماماً خاصاً</h4>
                <div class="at-risk-list">
        `;
        
        students.forEach(student => {
            html += `
                <div class="at-risk-student-card">
                    <div class="student-info">
                        <span class="student-name">${student.name}</span>
                        <span class="student-grade">${student.grade || ''}</span>
                    </div>
                    <div class="weak-subjects">
                        ${student.weak_subjects.map(ws => `
                            <span class="weak-subject-badge danger">
                                ${ws.subject} (${ws.average}%)
                            </span>
                        `).join('')}
                    </div>
                </div>
            `;
        });
        
        html += '</div></div>';
        return html;
    }
    
    /**
     * Render educational strategies
     */
    renderStrategies(strategies) {
        let html = `
            <div class="strategies-section">
                <h4 class="insights-title"><i class="fas fa-lightbulb"></i> استراتيجيات تعليمية مقترحة</h4>
                <div class="strategies-list">
        `;
        
        strategies.forEach((strategy, index) => {
            const priorityClass = strategy.priority === 'high' ? 'danger' : 'warning';
            
            html += `
                <div class="strategy-card ${priorityClass}">
                    <div class="strategy-header">
                        <span class="strategy-subject">${strategy.subject}</span>
                        <span class="strategy-priority ${priorityClass}">${strategy.priority === 'high' ? 'أولوية عالية' : 'أولوية متوسطة'}</span>
                    </div>
                    <div class="strategy-issue">${strategy.issue}</div>
                    <div class="strategy-content">
                        <strong>${strategy.strategy}</strong>
                    </div>
                    <ul class="strategy-actions">
                        ${strategy.suggested_actions.map(action => `
                            <li>${action}</li>
                        `).join('')}
                    </ul>
                </div>
            `;
        });
        
        html += '</div></div>';
        return html;
    }
    
    /**
     * Show error message
     */
    showError(message) {
        if (!this.container) return;
        
        this.container.innerHTML = `
            <div class="recommendations-error">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${message}</p>
                <button class="btn-retry" onclick="window.TeacherRecommendationsManager.loadRecommendations()">
                    <i class="fas fa-redo"></i> إعادة المحاولة
                </button>
            </div>
        `;
    }
}
