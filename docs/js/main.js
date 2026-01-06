// ========================================
// Main JavaScript - Interactivity & Navigation
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize all interactive components
    initNavigation();
    initTabs();
    initFlowDiagram();
    initLayerCards();
    initScrollAnimations();
});

// ========================================
// Navigation Menu Toggle
// ========================================
function initNavigation() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    const navLinks = document.querySelectorAll('.nav-link');

    if (hamburger) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
    }

    // Close mobile menu when clicking on a link
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            hamburger.classList.remove('active');
            navMenu.classList.remove('active');
        });
    });

    // Smooth scroll for navigation links
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const navHeight = document.querySelector('.navbar').offsetHeight;
                const targetPosition = targetSection.offsetTop - navHeight - 20;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Navbar shadow on scroll
    window.addEventListener('scroll', () => {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 100) {
            navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.3)';
        } else {
            navbar.style.boxShadow = '0 4px 16px rgba(0, 0, 0, 0.15)';
        }
    });
}

// ========================================
// Tab System for Components Section
// ========================================
function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons and contents
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            // Add active class to clicked button
            btn.classList.add('active');

            // Show corresponding content
            const tabId = btn.getAttribute('data-tab');
            const targetContent = document.getElementById(`${tabId}-content`);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });
}

// ========================================
// Data Flow Diagram Interactivity
// ========================================
function initFlowDiagram() {
    const flowSteps = document.querySelectorAll('.flow-step');
    const flowDetails = document.getElementById('flow-details');
    const flowDetailsContent = document.getElementById('flow-details-content');
    const closeBtn = document.getElementById('close-flow-details');

    const stepDetails = {
        '1': {
            title: 'AWS S3 - Data Source',
            icon: 'fa-cloud',
            description: 'Raw CSV files stored in AWS S3 bucket',
            details: [
                '<strong>Storage:</strong> Amazon S3',
                '<strong>Format:</strong> CSV files',
                '<strong>Tables:</strong> 8 source tables',
                '<strong>Volume:</strong> 100K+ order records',
                '<strong>Time Period:</strong> 2016-2018'
            ],
            files: [
                'olist_customers_dataset.csv',
                'olist_orders_dataset.csv',
                'olist_order_items_dataset.csv',
                'olist_order_payments_dataset.csv',
                'olist_products_dataset.csv',
                'olist_sellers_dataset.csv',
                'olist_order_reviews_dataset.csv',
                'olist_geolocation_dataset.csv'
            ]
        },
        '2': {
            title: 'Snowflake RAW Schema',
            icon: 'fa-snowflake',
            description: 'Landing zone for raw data ingestion',
            details: [
                '<strong>Schema:</strong> RAW',
                '<strong>Load Method:</strong> COPY INTO command',
                '<strong>Process:</strong> Bulk data loading from S3',
                '<strong>Transformation:</strong> None (exact copy)',
                '<strong>Purpose:</strong> Preserve original data structure'
            ],
            features: [
                'Automated ingestion pipelines',
                'Error handling and logging',
                'Data lineage tracking',
                'Incremental load capability'
            ]
        },
        '3': {
            title: 'Bronze Layer - Staging',
            icon: 'fa-database',
            description: 'Initial transformation and staging layer',
            details: [
                '<strong>Schema:</strong> BRONZE',
                '<strong>Materialization:</strong> Incremental',
                '<strong>dbt Models:</strong> 8 bronze models',
                '<strong>Purpose:</strong> Minimal transformations',
                '<strong>Operations:</strong> Type casting, timestamp addition'
            ],
            transformations: [
                'Data type conversions',
                'UTC timestamp standardization',
                'Primary key identification',
                'Metadata columns addition',
                'Deduplication (basic)'
            ]
        },
        '4': {
            title: 'Silver Layer - Cleaned Data',
            icon: 'fa-filter',
            description: 'Cleaned and conformed data layer',
            details: [
                '<strong>Schema:</strong> SILVER',
                '<strong>Structure:</strong> Star schema (Dimensions & Facts)',
                '<strong>Materialization:</strong> Mixed (Table/Incremental)',
                '<strong>Quality:</strong> Data quality tests applied',
                '<strong>Keys:</strong> Surrogate keys generated'
            ],
            components: [
                '<strong>Dimensions:</strong> dim_customers, dim_products, dim_sellers, dim_date',
                '<strong>Facts:</strong> fact_orders, fact_order_items, fact_payments, fact_reviews',
                '<strong>Tests:</strong> Not null, unique, relationships, accepted values',
                '<strong>Business Rules:</strong> Applied via dbt macros'
            ]
        },
        '5': {
            title: 'Gold Layer - Business Ready',
            icon: 'fa-gem',
            description: 'Analytics-ready business layer',
            details: [
                '<strong>Schema:</strong> GOLD',
                '<strong>Materialization:</strong> Table',
                '<strong>Purpose:</strong> Business aggregations & analytics',
                '<strong>Structure:</strong> Denormalized for performance',
                '<strong>Use Cases:</strong> Reporting, ML, Analytics'
            ],
            models: [
                '<strong>OBT:</strong> obt_orders (One Big Table for ML)',
                '<strong>Feature Store:</strong> customer_features, product_features',
                '<strong>Aggregations:</strong> sales_summary, customer_metrics',
                '<strong>KPIs:</strong> Dashboard metrics and KPIs'
            ]
        },
        '6': {
            title: 'ML Pipeline',
            icon: 'fa-brain',
            description: 'Machine Learning prediction pipeline',
            details: [
                '<strong>Algorithm:</strong> CatBoost Classifier',
                '<strong>Input:</strong> Gold layer feature store',
                '<strong>Features:</strong> 50+ engineered features',
                '<strong>Output:</strong> Predictions stored in Snowflake'
            ],
            stages: [
                '<strong>1. Feature Engineering:</strong> RFM analysis, customer behavior',
                '<strong>2. Model Training:</strong> CatBoost with hyperparameter tuning',
                '<strong>3. Validation:</strong> Cross-validation and metrics',
                '<strong>4. Prediction:</strong> Batch scoring on new data',
                '<strong>5. Storage:</strong> Results written back to Gold layer'
            ]
        },
        '7': {
            title: 'Analytics Dashboard',
            icon: 'fa-chart-line',
            description: 'Interactive Streamlit dashboard',
            details: [
                '<strong>Framework:</strong> Streamlit',
                '<strong>Pages:</strong> 7 interactive pages',
                '<strong>Visualizations:</strong> Plotly charts',
                '<strong>Users:</strong> Analysts, Data Scientists, Executives'
            ],
            pages: [
                '<strong>Overview:</strong> High-level KPIs and trends',
                '<strong>Sales Analytics:</strong> Revenue, top products, trends',
                '<strong>Customer Analytics:</strong> Segmentation, retention',
                '<strong>Product Analytics:</strong> Category performance',
                '<strong>Payment Analytics:</strong> Payment methods, installments',
                '<strong>Delivery Performance:</strong> Shipping times, delays',
                '<strong>Review Analytics:</strong> Customer satisfaction, ratings'
            ]
        }
    };

    flowSteps.forEach(step => {
        step.addEventListener('click', () => {
            const stepNumber = step.getAttribute('data-step');
            const stepData = stepDetails[stepNumber];

            if (stepData) {
                // Build details HTML
                let detailsHTML = `
                    <div class="flow-detail-header">
                        <i class="fas ${stepData.icon} fa-3x" style="color: var(--primary-color); margin-bottom: 1rem;"></i>
                        <h2>${stepData.title}</h2>
                        <p style="font-size: 1.1rem; color: #666; margin-bottom: 2rem;">${stepData.description}</p>
                    </div>
                    <div class="flow-detail-body">
                        <div class="detail-section">
                            <h3>Details</h3>
                            <ul>
                                ${stepData.details.map(d => `<li>${d}</li>`).join('')}
                            </ul>
                        </div>
                `;

                // Add additional sections based on available data
                if (stepData.files) {
                    detailsHTML += `
                        <div class="detail-section">
                            <h3>Source Files</h3>
                            <ul>
                                ${stepData.files.map(f => `<li><code>${f}</code></li>`).join('')}
                            </ul>
                        </div>
                    `;
                }

                if (stepData.features) {
                    detailsHTML += `
                        <div class="detail-section">
                            <h3>Key Features</h3>
                            <ul>
                                ${stepData.features.map(f => `<li>${f}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }

                if (stepData.transformations) {
                    detailsHTML += `
                        <div class="detail-section">
                            <h3>Transformations Applied</h3>
                            <ul>
                                ${stepData.transformations.map(t => `<li>${t}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }

                if (stepData.components) {
                    detailsHTML += `
                        <div class="detail-section">
                            <h3>Components</h3>
                            <ul>
                                ${stepData.components.map(c => `<li>${c}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }

                if (stepData.models) {
                    detailsHTML += `
                        <div class="detail-section">
                            <h3>Data Models</h3>
                            <ul>
                                ${stepData.models.map(m => `<li>${m}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }

                if (stepData.stages) {
                    detailsHTML += `
                        <div class="detail-section">
                            <h3>Pipeline Stages</h3>
                            <ul>
                                ${stepData.stages.map(s => `<li>${s}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }

                if (stepData.pages) {
                    detailsHTML += `
                        <div class="detail-section">
                            <h3>Dashboard Pages</h3>
                            <ul>
                                ${stepData.pages.map(p => `<li>${p}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }

                detailsHTML += `</div>`;

                flowDetailsContent.innerHTML = detailsHTML;
                flowDetails.classList.add('active');
                flowDetails.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        });
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            flowDetails.classList.remove('active');
        });
    }
}

// ========================================
// Layer Cards Hover Effects
// ========================================
function initLayerCards() {
    const layerCards = document.querySelectorAll('.layer-card');

    layerCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.borderLeftWidth = '8px';
        });

        card.addEventListener('mouseleave', () => {
            card.style.borderLeftWidth = '5px';
        });
    });
}

// ========================================
// Scroll Animations
// ========================================
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Elements to animate
    const animatedElements = document.querySelectorAll(`
        .overview-card,
        .layer-card,
        .component-card,
        .flow-step,
        .deploy-step,
        .tech-category
    `);

    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

// ========================================
// Additional Helper Functions
// ========================================

// Copy code block to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!');
    });
}

// Show notification
function showNotification(message) {
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        padding: 1rem 2rem;
        border-radius: 8px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Add copy buttons to code blocks
document.addEventListener('DOMContentLoaded', () => {
    const codeBlocks = document.querySelectorAll('.code-block');
    codeBlocks.forEach(block => {
        const copyBtn = document.createElement('button');
        copyBtn.innerHTML = '<i class="fas fa-copy"></i> Copy';
        copyBtn.style.cssText = `
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: background 0.3s ease;
        `;
        copyBtn.addEventListener('mouseenter', () => {
            copyBtn.style.background = 'rgba(255, 255, 255, 0.3)';
        });
        copyBtn.addEventListener('mouseleave', () => {
            copyBtn.style.background = 'rgba(255, 255, 255, 0.2)';
        });
        copyBtn.addEventListener('click', () => {
            const code = block.querySelector('code').textContent;
            copyToClipboard(code);
        });

        block.style.position = 'relative';
        block.appendChild(copyBtn);
    });
});

// Stats counter animation
function animateCounter(element, target, duration = 2000) {
    let start = 0;
    const increment = target / (duration / 16);
    
    const timer = setInterval(() => {
        start += increment;
        if (start >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(start);
        }
    }, 16);
}

// Initialize counter animations when hero section is visible
const heroSection = document.querySelector('.hero-section');
if (heroSection) {
    const heroObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const statCards = document.querySelectorAll('.stat-card h3');
                statCards.forEach(card => {
                    const text = card.textContent;
                    const number = parseInt(text.replace(/\D/g, ''));
                    if (number) {
                        card.textContent = '0';
                        setTimeout(() => {
                            animateCounter(card, number);
                        }, 500);
                    }
                });
                heroObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    heroObserver.observe(heroSection);
}
