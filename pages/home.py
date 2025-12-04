import streamlit as st
from backend.auth import UserAuth

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="STOCKREADER AI - Home",
    page_icon="📈",
    layout="wide"
)

# ========== CUSTOM CSS ==========
st.markdown("""
<style>
    /* Main Styles */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 4rem 2rem;
        text-align: center;
        border-radius: 15px;
        margin-bottom: 3rem;
    }
    
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: transform 0.3s;
        height: 100%;
        border: 1px solid #eaeaea;
    }
    
    .feature-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1.5rem;
        color: #667eea;
    }
    
    .stats-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        border-top: 4px solid #667eea;
    }
    
    .cta-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2.5rem;
        border: none;
        border-radius: 50px;
        font-weight: 600;
        font-size: 1.1rem;
        cursor: pointer;
        transition: all 0.3s;
        display: inline-block;
        text-decoration: none;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    .cta-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.5);
    }
    
    .testimonial-card {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        border-left: 5px solid #667eea;
        margin-bottom: 1.5rem;
    }
    
    .pricing-card {
        background: white;
        padding: 2.5rem 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        text-align: center;
        border: 2px solid #eaeaea;
        transition: all 0.3s;
    }
    
    .pricing-card:hover {
        border-color: #667eea;
        transform: translateY(-10px);
    }
    
    .pricing-card.featured {
        border-color: #667eea;
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.2);
        transform: scale(1.05);
    }
    
    .navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    
    .nav-links {
        display: flex;
        gap: 2rem;
    }
    
    .nav-link {
        color: #333;
        text-decoration: none;
        font-weight: 500;
        transition: color 0.3s;
    }
    
    .nav-link:hover {
        color: #667eea;
    }
    
    .hero-section {
        padding: 5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ========== NAVIGATION BAR ==========
col1, col2 = st.columns([3, 2])
with col1:
    st.markdown("<h1 style='color: #667eea; margin: 0;'>STOCKREADER AI</h1>", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="nav-links">
        <a href="/" class="nav-link">Home</a>
        <a href="/2_Login" class="nav-link">Login</a>
        <a href="/3_Register" class="nav-link">Register</a>
        <a href="/" class="nav-link">Dashboard</a>
        <a href="#features" class="nav-link">Features</a>
    </div>
    """, unsafe_allow_html=True)

# ========== HERO SECTION ==========
st.markdown("""
<div class="main-header">
    <h1 style="font-size: 3.5rem; margin-bottom: 1rem;">Intelligent Stock Analysis Platform</h1>
    <p style="font-size: 1.5rem; opacity: 0.9; margin-bottom: 2rem;">
        AI-powered stock analysis for smarter investment decisions
    </p>
    <a href="/3_Register">
        <button class="cta-button">
            Start Free Trial
        </button>
    </a>
    <p style="margin-top: 1.5rem; font-size: 1rem;">
        No credit card required • 14-day free trial
    </p>
</div>
""", unsafe_allow_html=True)

# ========== STATISTICS SECTION ==========
st.markdown("### Trusted by Investors Worldwide")
st.markdown("---")

stats_cols = st.columns(4)
stats = [
    ("10,000+", "Active Users", "Growing community of investors"),
    ("99.8%", "Data Accuracy", "Real-time market data"),
    ("24/7", "Availability", "Always online, always ready"),
    ("50+", "Markets Covered", "Global stock markets")
]

for idx, (value, title, desc) in enumerate(stats):
    with stats_cols[idx]:
        st.markdown(f"""
        <div class="stats-card">
            <h2 style="color: #667eea; margin: 0;">{value}</h2>
            <h4 style="margin: 0.5rem 0;">{title}</h4>
            <p style="color: #666; font-size: 0.9rem; margin: 0;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

# ========== FEATURES SECTION ==========
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("### Key Features")
st.markdown("---")

features = [
    {
        "title": "AI-Powered Analysis",
        "description": "Advanced machine learning algorithms analyze market trends and predict stock movements with high accuracy.",
        "icon": "🤖"
    },
    {
        "title": "Real-Time Data",
        "description": "Access real-time stock data from global markets with milliseconds latency and 99.9% uptime.",
        "icon": "📊"
    },
    {
        "title": "Portfolio Management",
        "description": "Track and manage your investment portfolio with advanced analytics and performance metrics.",
        "icon": "💼"
    },
    {
        "title": "Risk Assessment",
        "description": "Comprehensive risk analysis tools to help you make informed investment decisions.",
        "icon": "📈"
    },
    {
        "title": "Custom Alerts",
        "description": "Set personalized alerts for price movements, news, and market changes.",
        "icon": "🔔"
    },
    {
        "title": "Multi-Platform",
        "description": "Access your account from web, mobile, and desktop applications seamlessly.",
        "icon": "📱"
    }
]

# Display features in grid
cols = st.columns(3)
for idx, feature in enumerate(features):
    with cols[idx % 3]:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">{feature['icon']}</div>
            <h3>{feature['title']}</h3>
            <p style="color: #666; line-height: 1.6;">{feature['description']}</p>
        </div>
        """, unsafe_allow_html=True)

# ========== HOW IT WORKS ==========
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("### How It Works")
st.markdown("---")

steps_cols = st.columns(4)
steps = [
    ("1", "Sign Up", "Create your free account in minutes"),
    ("2", "Connect", "Link your brokerage account or add stocks manually"),
    ("3", "Analyze", "Use AI tools to analyze stocks and markets"),
    ("4", "Invest", "Make informed decisions and track performance")
]

for idx, (num, title, desc) in enumerate(steps):
    with steps_cols[idx]:
        st.markdown(f"""
        <div style="text-align: center; padding: 1.5rem;">
            <div style="background: #667eea; color: white; width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; font-size: 1.5rem; font-weight: bold;">
                {num}
            </div>
            <h4>{title}</h4>
            <p style="color: #666; font-size: 0.9rem;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

# ========== PRICING SECTION ==========
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("### Simple, Transparent Pricing")
st.markdown("---")

pricing_cols = st.columns(3)
pricing_plans = [
    {
        "name": "Free",
        "price": "$0",
        "period": "forever",
        "features": ["Basic stock analysis", "Real-time data", "Portfolio tracking", "Email support"],
        "button": "Get Started",
        "featured": False
    },
    {
        "name": "Pro",
        "price": "$29",
        "period": "per month",
        "features": ["AI-powered analysis", "Advanced analytics", "Custom alerts", "Priority support", "API access"],
        "button": "Start Free Trial",
        "featured": True
    },
    {
        "name": "Enterprise",
        "price": "Custom",
        "period": "per year",
        "features": ["Custom AI models", "Dedicated support", "White-label solution", "On-premise deployment", "Training & consulting"],
        "button": "Contact Sales",
        "featured": False
    }
]

for idx, plan in enumerate(pricing_plans):
    with pricing_cols[idx]:
        card_class = "pricing-card featured" if plan['featured'] else "pricing-card"
        st.markdown(f"""
        <div class="{card_class}">
            <h3>{plan['name']}</h3>
            <h1 style="color: #667eea; margin: 1rem 0;">{plan['price']}</h1>
            <p style="color: #666; margin-bottom: 2rem;">{plan['period']}</p>
            <div style="text-align: left; margin-bottom: 2rem;">
        """, unsafe_allow_html=True)
        
        for feature in plan['features']:
            st.markdown(f"✓ {feature}<br>", unsafe_allow_html=True)
        
        st.markdown(f"""
            </div>
            <a href="/3_Register">
                <button class="cta-button" style="width: 100%;">
                    {plan['button']}
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

# ========== TESTIMONIALS ==========
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("### What Our Users Say")
st.markdown("---")

testimonial_cols = st.columns(2)
testimonials = [
    {
        "name": "Michael Chen",
        "role": "Portfolio Manager",
        "company": "Capital Investments",
        "text": "STOCKREADER AI has revolutionized how we analyze stocks. The AI predictions have improved our returns by 35%.",
        "avatar": "👨‍💼"
    },
    {
        "name": "Sarah Johnson",
        "role": "Independent Trader",
        "company": "",
        "text": "As a solo trader, this platform gives me institutional-grade tools at an affordable price. Game changer!",
        "avatar": "👩‍💻"
    }
]

for idx, testimonial in enumerate(testimonials):
    with testimonial_cols[idx]:
        st.markdown(f"""
        <div class="testimonial-card">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div style="font-size: 2.5rem; margin-right: 1rem;">{testimonial['avatar']}</div>
                <div>
                    <h4 style="margin: 0;">{testimonial['name']}</h4>
                    <p style="color: #666; margin: 0.2rem 0 0 0;">
                        {testimonial['role']}{', ' + testimonial['company'] if testimonial['company'] else ''}
                    </p>
                </div>
            </div>
            <p style="font-style: italic; color: #555; line-height: 1.6;">"{testimonial['text']}"</p>
        </div>
        """, unsafe_allow_html=True)

# ========== CALL TO ACTION ==========
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: 4rem 2rem; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 15px;">
    <h2 style="color: #333;">Ready to Transform Your Investment Strategy?</h2>
    <p style="font-size: 1.2rem; color: #666; margin: 1rem 0 2rem 0; max-width: 600px; margin-left: auto; margin-right: auto;">
        Join thousands of investors who are already making smarter decisions with STOCKREADER AI.
    </p>
    <div style="display: flex; gap: 1rem; justify-content: center;">
        <a href="/3_Register">
            <button class="cta-button">
                Start Free Trial
            </button>
        </a>
        <a href="/2_Login">
            <button class="cta-button" style="background: white; color: #667eea; border: 2px solid #667eea;">
                Login to Account
            </button>
        </a>
    </div>
    <p style="margin-top: 1.5rem; color: #666; font-size: 0.9rem;">
        Free 14-day trial • No credit card required • Cancel anytime
    </p>
</div>
""", unsafe_allow_html=True)

# ========== FOOTER ==========
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("""
<div style="display: flex; justify-content: space-between; color: #666; padding: 2rem 0;">
    <div>
        <h4 style="color: #333;">STOCKREADER AI</h4>
        <p>Intelligent stock analysis platform</p>
        <p style="font-size: 0.9rem;">© 2024 StockReader AI. All rights reserved.</p>
    </div>
    <div>
        <h4 style="color: #333;">Quick Links</h4>
        <a href="/" style="color: #666; text-decoration: none; display: block;">Home</a>
        <a href="/2_Login" style="color: #666; text-decoration: none; display: block;">Login</a>
        <a href="/3_Register" style="color: #666; text-decoration: none; display: block;">Register</a>
        <a href="#" style="color: #666; text-decoration: none; display: block;">Documentation</a>
    </div>
    <div>
        <h4 style="color: #333;">Contact</h4>
        <p style="margin: 0.2rem 0;">support@stockreader.ai</p>
        <p style="margin: 0.2rem 0;">+1 (555) 123-4567</p>
        <p style="margin: 0.2rem 0;">Jakarta, Indonesia</p>
    </div>
</div>
""", unsafe_allow_html=True)