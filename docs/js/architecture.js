// ========================================
// Architecture Visualization with Interactive SVG
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    renderArchitectureDiagram();
});

function renderArchitectureDiagram() {
    const diagramContainer = document.getElementById('architecture-diagram');
    
    if (!diagramContainer) return;

    const svg = `
        <svg width="100%" height="500" viewBox="0 0 1200 500" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <!-- Gradients -->
                <linearGradient id="primaryGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#FF694B;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#29B5E8;stop-opacity:1" />
                </linearGradient>
                
                <linearGradient id="bronzeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#cd7f32;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#b8860b;stop-opacity:1" />
                </linearGradient>
                
                <linearGradient id="silverGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#c0c0c0;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#808080;stop-opacity:1" />
                </linearGradient>
                
                <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#ffd700;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#ffaa00;stop-opacity:1" />
                </linearGradient>
                
                <!-- Arrow markers -->
                <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                    <polygon points="0 0, 10 3, 0 6" fill="#FF694B" />
                </marker>
                
                <!-- Drop shadow filter -->
                <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
                    <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
                    <feOffset dx="2" dy="2" result="offsetblur"/>
                    <feComponentTransfer>
                        <feFuncA type="linear" slope="0.3"/>
                    </feComponentTransfer>
                    <feMerge>
                        <feMergeNode/>
                        <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                </filter>
            </defs>
            
            <!-- Data Flow Arrows -->
            <g class="flow-arrows">
                <!-- S3 to Snowflake RAW -->
                <path d="M 140 80 L 280 80" stroke="url(#primaryGrad)" stroke-width="3" 
                      marker-end="url(#arrowhead)" class="animated-arrow arrow-1"/>
                
                <!-- RAW to Bronze -->
                <path d="M 380 80 L 480 80" stroke="url(#primaryGrad)" stroke-width="3" 
                      marker-end="url(#arrowhead)" class="animated-arrow arrow-2"/>
                
                <!-- Bronze to Silver -->
                <path d="M 580 80 L 680 80" stroke="url(#primaryGrad)" stroke-width="3" 
                      marker-end="url(#arrowhead)" class="animated-arrow arrow-3"/>
                
                <!-- Silver to Gold -->
                <path d="M 780 80 L 880 80" stroke="url(#primaryGrad)" stroke-width="3" 
                      marker-end="url(#arrowhead)" class="animated-arrow arrow-4"/>
                
                <!-- Gold to ML Pipeline -->
                <path d="M 980 80 L 1020 80 L 1020 250" stroke="url(#primaryGrad)" stroke-width="3" 
                      marker-end="url(#arrowhead)" class="animated-arrow arrow-5"/>
                
                <!-- Gold to Dashboard -->
                <path d="M 980 80 L 1120 80 L 1120 380" stroke="url(#primaryGrad)" stroke-width="3" 
                      marker-end="url(#arrowhead)" class="animated-arrow arrow-6"/>
            </g>
            
            <!-- Data Source: AWS S3 -->
            <g class="arch-node node-s3" transform="translate(30, 30)" data-info="s3">
                <rect width="110" height="100" rx="10" fill="#232F3E" filter="url(#shadow)" 
                      class="node-rect interactive"/>
                <text x="55" y="30" text-anchor="middle" fill="white" font-size="14" font-weight="bold">
                    AWS S3
                </text>
                <text x="55" y="55" text-anchor="middle" fill="#FF9900" font-size="24">☁</text>
                <text x="55" y="80" text-anchor="middle" fill="#cccccc" font-size="11">
                    Raw CSV
                </text>
                <text x="55" y="95" text-anchor="middle" fill="#cccccc" font-size="11">
                    Files
                </text>
            </g>
            
            <!-- Snowflake RAW -->
            <g class="arch-node node-raw" transform="translate(280, 30)" data-info="raw">
                <rect width="100" height="100" rx="10" fill="#29B5E8" filter="url(#shadow)" 
                      class="node-rect interactive"/>
                <text x="50" y="30" text-anchor="middle" fill="white" font-size="14" font-weight="bold">
                    Snowflake
                </text>
                <text x="50" y="55" text-anchor="middle" fill="white" font-size="24">❄</text>
                <text x="50" y="80" text-anchor="middle" fill="#e6f7ff" font-size="11">
                    RAW
                </text>
                <text x="50" y="95" text-anchor="middle" fill="#e6f7ff" font-size="11">
                    Schema
                </text>
            </g>
            
            <!-- Bronze Layer -->
            <g class="arch-node node-bronze" transform="translate(480, 30)" data-info="bronze">
                <rect width="100" height="100" rx="10" fill="url(#bronzeGrad)" filter="url(#shadow)" 
                      class="node-rect interactive"/>
                <text x="50" y="30" text-anchor="middle" fill="white" font-size="14" font-weight="bold">
                    Bronze
                </text>
                <text x="50" y="55" text-anchor="middle" fill="white" font-size="24">🥉</text>
                <text x="50" y="80" text-anchor="middle" fill="#fff5e6" font-size="11">
                    Staging
                </text>
                <text x="50" y="95" text-anchor="middle" fill="#fff5e6" font-size="11">
                    Layer
                </text>
            </g>
            
            <!-- Silver Layer -->
            <g class="arch-node node-silver" transform="translate(680, 30)" data-info="silver">
                <rect width="100" height="100" rx="10" fill="url(#silverGrad)" filter="url(#shadow)" 
                      class="node-rect interactive"/>
                <text x="50" y="30" text-anchor="middle" fill="white" font-size="14" font-weight="bold">
                    Silver
                </text>
                <text x="50" y="55" text-anchor="middle" fill="white" font-size="24">🥈</text>
                <text x="50" y="80" text-anchor="middle" fill="#f5f5f5" font-size="11">
                    Cleaned
                </text>
                <text x="50" y="95" text-anchor="middle" fill="#f5f5f5" font-size="11">
                    Data
                </text>
            </g>
            
            <!-- Gold Layer -->
            <g class="arch-node node-gold" transform="translate(880, 30)" data-info="gold">
                <rect width="100" height="100" rx="10" fill="url(#goldGrad)" filter="url(#shadow)" 
                      class="node-rect interactive"/>
                <text x="50" y="30" text-anchor="middle" fill="#333" font-size="14" font-weight="bold">
                    Gold
                </text>
                <text x="50" y="55" text-anchor="middle" fill="#333" font-size="24">🥇</text>
                <text x="50" y="80" text-anchor="middle" fill="#664d00" font-size="11">
                    Business
                </text>
                <text x="50" y="95" text-anchor="middle" fill="#664d00" font-size="11">
                    Layer
                </text>
            </g>
            
            <!-- ML Pipeline -->
            <g class="arch-node node-ml" transform="translate(950, 250)" data-info="ml">
                <rect width="140" height="90" rx="10" fill="#9b59b6" filter="url(#shadow)" 
                      class="node-rect interactive"/>
                <text x="70" y="25" text-anchor="middle" fill="white" font-size="14" font-weight="bold">
                    ML Pipeline
                </text>
                <text x="70" y="50" text-anchor="middle" fill="white" font-size="24">🧠</text>
                <text x="70" y="72" text-anchor="middle" fill="#f3e5f5" font-size="11">
                    CatBoost Model
                </text>
            </g>
            
            <!-- Analytics Dashboard -->
            <g class="arch-node node-dashboard" transform="translate(1020, 380)" data-info="dashboard">
                <rect width="150" height="90" rx="10" fill="#3498db" filter="url(#shadow)" 
                      class="node-rect interactive"/>
                <text x="75" y="25" text-anchor="middle" fill="white" font-size="14" font-weight="bold">
                    Dashboard
                </text>
                <text x="75" y="50" text-anchor="middle" fill="white" font-size="24">📊</text>
                <text x="75" y="72" text-anchor="middle" fill="#e3f2fd" font-size="11">
                    Streamlit Analytics
                </text>
            </g>
            
            <!-- DBT Transformation Badge -->
            <g class="dbt-badge" transform="translate(550, 180)">
                <rect width="180" height="60" rx="30" fill="#FF694B" filter="url(#shadow)"/>
                <text x="90" y="25" text-anchor="middle" fill="white" font-size="13" font-weight="bold">
                    dbt Transformations
                </text>
                <text x="90" y="45" text-anchor="middle" fill="#ffe6e0" font-size="10">
                    Data Build Tool
                </text>
            </g>
            
            <!-- Data Quality Badge -->
            <g class="quality-badge" transform="translate(550, 260)">
                <rect width="180" height="50" rx="25" fill="#27ae60" filter="url(#shadow)"/>
                <text x="90" y="22" text-anchor="middle" fill="white" font-size="12" font-weight="bold">
                    ✓ Data Quality Tests
                </text>
                <text x="90" y="38" text-anchor="middle" fill="#e8f8f5" font-size="9">
                    20+ Tests Applied
                </text>
            </g>
            
            <!-- Legend -->
            <g class="legend" transform="translate(30, 380)">
                <text x="0" y="0" fill="#666" font-size="13" font-weight="bold">Legend:</text>
                <circle cx="10" cy="25" r="6" fill="#FF694B"/>
                <text x="25" y="30" fill="#666" font-size="11">Data Flow</text>
                
                <circle cx="10" cy="50" r="6" fill="#9b59b6"/>
                <text x="25" y="55" fill="#666" font-size="11">ML Pipeline</text>
                
                <circle cx="10" cy="75" r="6" fill="#3498db"/>
                <text x="25" y="80" fill="#666" font-size="11">Analytics</text>
            </g>
            
            <!-- Animated data particles -->
            <g class="data-particles">
                <circle class="particle particle-1" r="4" fill="#FF694B">
                    <animateMotion dur="3s" repeatCount="indefinite" 
                                   path="M 140 80 L 280 80 L 380 80 L 480 80 L 580 80 L 680 80 L 780 80 L 880 80 L 980 80"/>
                </circle>
                <circle class="particle particle-2" r="4" fill="#29B5E8">
                    <animateMotion dur="3s" begin="1s" repeatCount="indefinite" 
                                   path="M 140 80 L 280 80 L 380 80 L 480 80 L 580 80 L 680 80 L 780 80 L 880 80 L 980 80"/>
                </circle>
                <circle class="particle particle-3" r="4" fill="#ffd700">
                    <animateMotion dur="3s" begin="2s" repeatCount="indefinite" 
                                   path="M 140 80 L 280 80 L 380 80 L 480 80 L 580 80 L 680 80 L 780 80 L 880 80 L 980 80"/>
                </circle>
            </g>
        </svg>
    `;

    diagramContainer.innerHTML = svg;

    // Add interactivity to nodes
    addNodeInteractivity();
    
    // Add CSS for animations
    addArchitectureStyles();
}

function addNodeInteractivity() {
    const nodes = document.querySelectorAll('.arch-node');
    
    const nodeInfo = {
        's3': {
            title: 'AWS S3 - Data Source',
            description: 'Amazon S3 bucket storing raw CSV files from Brazilian E-Commerce dataset',
            details: [
                '8 CSV source files',
                '100K+ order records',
                'Data period: 2016-2018',
                'Automated ingestion pipeline'
            ]
        },
        'raw': {
            title: 'Snowflake RAW Schema',
            description: 'Landing zone for raw data ingestion via COPY INTO command',
            details: [
                'Exact copy of source data',
                'No transformations applied',
                'Preserves data lineage',
                'Foundation for all transformations'
            ]
        },
        'bronze': {
            title: 'Bronze Layer - Staging',
            description: 'Initial transformation layer with minimal processing',
            details: [
                '8 bronze models',
                'Incremental materialization',
                'Type casting & timestamps',
                'Basic deduplication'
            ]
        },
        'silver': {
            title: 'Silver Layer - Cleaned Data',
            description: 'Star schema with cleaned and conformed data',
            details: [
                'Dimensions & Facts separation',
                'Data quality tests applied',
                'Surrogate keys generated',
                'Business rules enforcement'
            ]
        },
        'gold': {
            title: 'Gold Layer - Business Ready',
            description: 'Analytics-ready aggregated business layer',
            details: [
                'One Big Table (OBT)',
                'Feature store for ML',
                'Denormalized for performance',
                'KPIs and metrics'
            ]
        },
        'ml': {
            title: 'ML Pipeline',
            description: 'Machine learning pipeline with CatBoost model',
            details: [
                'CatBoost classifier',
                '50+ engineered features',
                'Customer behavior prediction',
                'Batch scoring capability'
            ]
        },
        'dashboard': {
            title: 'Analytics Dashboard',
            description: 'Interactive Streamlit dashboard with 7 pages',
            details: [
                'Sales & Revenue Analytics',
                'Customer Segmentation',
                'Product Performance',
                'Delivery & Review Insights'
            ]
        }
    };

    nodes.forEach(node => {
        const infoKey = node.getAttribute('data-info');
        const info = nodeInfo[infoKey];
        
        if (!info) return;

        node.style.cursor = 'pointer';
        
        // Create tooltip
        const tooltip = document.createElement('div');
        tooltip.className = 'arch-tooltip';
        tooltip.innerHTML = `
            <h4>${info.title}</h4>
            <p>${info.description}</p>
            <ul>
                ${info.details.map(d => `<li>${d}</li>`).join('')}
            </ul>
        `;
        document.body.appendChild(tooltip);

        node.addEventListener('mouseenter', (e) => {
            const rect = node.getBoundingClientRect();
            tooltip.style.display = 'block';
            tooltip.style.left = rect.left + 'px';
            tooltip.style.top = (rect.bottom + 10) + 'px';
            
            // Highlight effect
            const nodeRect = node.querySelector('.node-rect');
            if (nodeRect) {
                nodeRect.style.transform = 'scale(1.1)';
                nodeRect.style.transition = 'transform 0.3s ease';
            }
        });

        node.addEventListener('mouseleave', () => {
            tooltip.style.display = 'none';
            
            const nodeRect = node.querySelector('.node-rect');
            if (nodeRect) {
                nodeRect.style.transform = 'scale(1)';
            }
        });

        node.addEventListener('click', () => {
            showNodeModal(info);
        });
    });
}

function showNodeModal(info) {
    // Create modal
    const modal = document.createElement('div');
    modal.className = 'arch-modal';
    modal.innerHTML = `
        <div class="arch-modal-content">
            <button class="modal-close">&times;</button>
            <h2>${info.title}</h2>
            <p class="modal-description">${info.description}</p>
            <div class="modal-details">
                <h3>Key Features:</h3>
                <ul>
                    ${info.details.map(d => `<li>${d}</li>`).join('')}
                </ul>
            </div>
        </div>
    `;
    document.body.appendChild(modal);

    // Close modal
    const closeBtn = modal.querySelector('.modal-close');
    closeBtn.addEventListener('click', () => {
        modal.remove();
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

function addArchitectureStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .animated-arrow {
            stroke-dasharray: 10;
            animation: dash 1s linear infinite;
        }
        
        @keyframes dash {
            to {
                stroke-dashoffset: -20;
            }
        }
        
        .particle {
            filter: drop-shadow(0 0 3px currentColor);
        }
        
        .arch-tooltip {
            position: fixed;
            display: none;
            background: white;
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
            z-index: 10000;
            max-width: 300px;
            border: 2px solid #FF694B;
        }
        
        .arch-tooltip h4 {
            margin: 0 0 0.5rem 0;
            color: #2c3e50;
            font-size: 1.1rem;
        }
        
        .arch-tooltip p {
            margin: 0 0 0.75rem 0;
            color: #666;
            font-size: 0.9rem;
        }
        
        .arch-tooltip ul {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        
        .arch-tooltip li {
            padding: 0.3rem 0;
            color: #555;
            font-size: 0.85rem;
            position: relative;
            padding-left: 1.2rem;
        }
        
        .arch-tooltip li::before {
            content: '✓';
            position: absolute;
            left: 0;
            color: #27ae60;
        }
        
        .arch-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10001;
            animation: fadeIn 0.3s ease;
        }
        
        .arch-modal-content {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            max-width: 500px;
            width: 90%;
            position: relative;
            animation: slideIn 0.3s ease;
        }
        
        .modal-close {
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: none;
            border: none;
            font-size: 2rem;
            cursor: pointer;
            color: #999;
            transition: color 0.3s ease;
        }
        
        .modal-close:hover {
            color: #FF694B;
        }
        
        .arch-modal-content h2 {
            margin: 0 0 1rem 0;
            color: #2c3e50;
            font-size: 1.5rem;
        }
        
        .modal-description {
            color: #666;
            margin-bottom: 1.5rem;
            font-size: 1rem;
        }
        
        .modal-details h3 {
            color: #2c3e50;
            font-size: 1.2rem;
            margin-bottom: 0.75rem;
        }
        
        .modal-details ul {
            list-style: none;
            padding: 0;
        }
        
        .modal-details li {
            padding: 0.5rem 0;
            color: #555;
            position: relative;
            padding-left: 1.5rem;
        }
        
        .modal-details li::before {
            content: '▸';
            position: absolute;
            left: 0;
            color: #FF694B;
            font-size: 1.2rem;
        }
        
        .node-rect.interactive:hover {
            filter: drop-shadow(0 0 10px rgba(255, 105, 75, 0.5));
        }
    `;
    document.head.appendChild(style);
}
