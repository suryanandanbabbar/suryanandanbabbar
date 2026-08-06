import json
import os
import base64

def load_file(path, default=""):
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception:
        return default

def escape_xml(text):
    if not isinstance(text, str):
        return str(text)
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def get_base64_image(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    except Exception as e:
        print(f"Error loading image: {e}")
        return ""

def generate_svg(config, theme, portrait_b64, github_data):
    # CSS Styles
    css = f"""
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&amp;display=swap');
    
    :root {{
        --bg: {theme.get('background', '#0D1117')};
        --border: {theme.get('borders', '#30363D')};
        --label: {theme.get('labels', '#FFB454')};
        --value: {theme.get('values', '#79C0FF')};
        --success: {theme.get('success', '#3FB950')};
        --warning: {theme.get('warnings', '#F85149')};
        --accent: {theme.get('accent', '#58A6FF')};
        --cursor: {theme.get('cursor', '#58A6FF')};
        --text-pri: {theme.get('text_primary', '#C9D1D9')};
        --text-sec: {theme.get('text_secondary', '#8B949E')};
    }}
    
    svg {{
        font-family: 'Fira Code', monospace;
        background-color: var(--bg);
        border-radius: 10px;
    }}
    
    .text-main {{ fill: var(--text-pri); font-size: 14px; }}
    .text-sec {{ fill: var(--text-sec); font-size: 14px; }}
    .label {{ fill: var(--label); font-weight: bold; font-size: 14px; }}
    .value {{ fill: var(--value); font-size: 14px; }}
    .accent {{ fill: var(--accent); font-weight: bold; font-size: 14px; }}
    .success {{ fill: var(--success); font-weight: bold; font-size: 14px; }}
    .title {{ font-size: 16px; font-weight: bold; fill: var(--accent); }}
    
    a {{ cursor: pointer; }}
    a:hover text {{ text-decoration: underline; }}
    
    /* Animations */
    @keyframes blink {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}
    .cursor {{ animation: blink 1s step-end infinite; fill: var(--cursor); }}
    
    @keyframes typing {{ from {{ width: 0; }} to {{ width: 100%; }} }}
    .typing-text {{ overflow: hidden; white-space: nowrap; animation: typing 2s steps(40, end); }}
    
    @keyframes mainFadeIn {{ 0% {{ opacity: 0; }} 100% {{ opacity: 1; }} }}
    .main-layer {{ opacity: 0; animation: mainFadeIn 1.5s forwards; }}
    
    @keyframes barFill {{ from {{ width: 0; }} to {{ width: var(--target-width); }} }}
    .anim-bar {{
        animation: barFill 1.5s ease-out forwards;
        fill: var(--value);
    }}
    """
    
    profile = config.get('profile', {})
    patent = config.get('patent', {})
    specializations = config.get('specialization', [])
    contact = config.get('contact', {})
    open_source = config.get('open_source', {})
    
    langs = ", ".join(github_data.get('top_languages', []))
    if not langs: langs = "N/A"

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 800" width="100%" height="auto">
    <defs>
        <style>{css}</style>
        <filter id="softGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="10" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
        <clipPath id="leftColClip">
            <rect x="0" y="60" width="300" height="740" rx="0" ry="0" />
        </clipPath>
        <clipPath id="headerClip">
            <rect x="0" y="0" width="1000" height="60" rx="10" ry="10" />
        </clipPath>
    </defs>
    
    <!-- Background -->
    <rect width="100%" height="100%" fill="var(--bg)" rx="10"/>
    <rect width="100%" height="100%" fill="none" stroke="var(--border)" stroke-width="2" rx="10"/>
    
    <!-- Main Layer (fades in) -->
    <g class="main-layer">
        
        <!-- Header -->
        <g clip-path="url(#headerClip)">
            <rect x="0" y="0" width="100%" height="60" fill="var(--bg)"/>
            <text x="20" y="40" class="text-main typing-text">{github_data.get('username', 'user')}@github:~# <tspan class="cursor">_</tspan></text>
            <line x1="0" y1="60" x2="1000" y2="60" stroke="var(--border)" stroke-width="1" />
        </g>
        
        <!-- Left Column: Portrait -->
        <!-- Portrait spanning full height under header, no circular mask -->
        <g transform="translate(0, 0)" clip-path="url(#leftColClip)">
            <!-- Soft ambient glow -->
            <rect x="-50" y="60" width="400" height="740" fill="var(--accent)" opacity="0.05" filter="url(#softGlow)" />
            <!-- The portrait -->
            <image href="data:image/png;base64,{portrait_b64}" x="-20" y="60" width="340" height="740" preserveAspectRatio="xMidYMax slice" />
        </g>
        <line x1="300" y1="60" x2="300" y2="800" stroke="var(--border)" stroke-width="1" />
        
        <!-- Right Column (Dashboard) -->
        <!-- Grid System: Labels at x=340, text-sec (colon) at x=480, Values at x=500 -->
        <g transform="translate(340, 90)">
            
            <!-- SYS_INFO -->
            <text x="0" y="0" class="title">SYS_INFO</text>
            <text x="0" y="25" class="label">.name</text>      <text x="140" y="25" class="text-sec">:</text> <text x="160" y="25" class="value">{escape_xml(github_data.get('name', ''))}</text>
            <text x="0" y="45" class="label">.role</text>      <text x="140" y="45" class="text-sec">:</text> <text x="160" y="45" class="value">{escape_xml(profile.get('role', ''))}</text>
            <text x="0" y="65" class="label">.education</text> <text x="140" y="65" class="text-sec">:</text> <text x="160" y="65" class="value">{escape_xml(profile.get('education', ''))}</text>
            <text x="0" y="85" class="label">.focus</text>     <text x="140" y="85" class="text-sec">:</text> <text x="160" y="85" class="value">{escape_xml(profile.get('focus', ''))}</text>
            <text x="0" y="105" class="label">.stack</text>    <text x="140" y="105" class="text-sec">:</text> <text x="160" y="105" class="value">{escape_xml(profile.get('stack', ''))}</text>
            
            <!-- CURRENT_BUILD -->
            <g transform="translate(0, 150)">
                <text x="0" y="0" class="title">CURRENT_BUILD</text>
                <text x="0" y="25" class="label">.repository</text> <text x="140" y="25" class="text-sec">:</text> <text x="160" y="25" class="accent">{escape_xml(github_data.get('latest_repo', 'N/A'))}</text>
                <text x="0" y="45" class="label">.stack</text>   <text x="140" y="45" class="text-sec">:</text> <text x="160" y="45" class="value">{escape_xml(github_data.get('latest_repo_lang', 'N/A'))}</text>
                <text x="0" y="65" class="label">.updated</text>    <text x="140" y="65" class="text-sec">:</text> <text x="160" y="65" class="value">{escape_xml(github_data.get('latest_repo_updated', 'N/A'))}</text>
            </g>

            <!-- GITHUB_TELEMETRY -->
            <g transform="translate(0, 240)">
                <text x="0" y="0" class="title">GITHUB_TELEMETRY</text>
                <text x="0" y="25" class="label">.public_repos</text> <text x="140" y="25" class="text-sec">:</text> <text x="160" y="25" class="value">{github_data.get('public_repos', 0)}</text>
                <text x="0" y="45" class="label">.followers</text>    <text x="140" y="45" class="text-sec">:</text> <text x="160" y="45" class="value">{github_data.get('followers', 0)}</text>
                <text x="0" y="65" class="label">.stars</text>        <text x="140" y="65" class="text-sec">:</text> <text x="160" y="65" class="value">{github_data.get('stars', 0)}</text>

                <!-- Subcolumn for telemetry -->
                <text x="280" y="25" class="label">.top_langs</text>  <text x="390" y="25" class="text-sec">:</text> <text x="410" y="25" class="value">{escape_xml(langs)}</text>
                <text x="280" y="45" class="label">.latest_rel</text> <text x="390" y="45" class="text-sec">:</text> <text x="410" y="45" class="value">{escape_xml(github_data.get('latest_release', 'N/A'))}</text>
            </g>

            <!-- PATENT -->
            <g transform="translate(0, 330)">
                <text x="0" y="0" class="title">PATENT</text>
                <text x="0" y="25" class="label">.status</text>      <text x="140" y="25" class="text-sec">:</text> <text x="160" y="25" class="success">{escape_xml(patent.get('status', ''))}</text>
                <text x="0" y="45" class="label">.application_no</text> <text x="140" y="45" class="text-sec">:</text> <text x="160" y="45" class="success">{escape_xml(patent.get('application_no', ''))}</text>
            </g>
            
            <!-- SPECIALIZATION -->
            <g transform="translate(0, 405)">
                <text x="0" y="0" class="title">SPECIALIZATION</text>
                """
    
    y_pos = 25
    x_offset = 0
    count = 0
    for spec in specializations:
        if count == 3:
            y_pos = 25
            x_offset = 280
        svg_content += f'<text x="{x_offset}" y="{y_pos}" class="label">*</text> <text x="{x_offset + 20}" y="{y_pos}" class="value">{escape_xml(spec)}</text>\n'
        y_pos += 20
        count += 1
                
    svg_content += f"""
            </g>
            
            <!-- ENGINEERING_RADAR -->
            <g transform="translate(0, 495)">
                <text x="0" y="0" class="title">ENGINEERING_RADAR</text>
                """
    
    # Render animated bars instead of percentages. 
    # To keep it decorative, we assign fixed widths for the 3 sample domains requested.
    radar = [(".ai", 80), (".backend", 70), (".dsa", 70)]
    y_pos = 25
    for skill, val in radar:
        svg_content += f'<text x="0" y="{y_pos}" class="label">{escape_xml(skill)}</text>\n'
        # Background empty bar blocks (using a rect for a cleaner look or texture)
        svg_content += f'<rect x="0" y="{y_pos + 8}" width="150" height="12" fill="var(--border)" rx="2" />\n'
        # Animated fill bar
        target_width = (150 * val) // 100
        svg_content += f'<rect x="0" y="{y_pos + 8}" width="0" height="12" rx="2" class="anim-bar" style="--target-width: {target_width}px;" />\n'
        y_pos += 45
        
    svg_content += f"""
            </g>

            <!-- OPEN_SOURCE -->
            <g transform="translate(280, 495)">
                <text x="0" y="0" class="title">OPEN_SOURCE</text>
                """
    y_pos = 25
    # NPM packages
    for pkg in open_source.get('npm', []):
        name = pkg.get('name', '')
        url = pkg.get('url', '')
        badge = f"https://img.shields.io/npm/v/{name.replace('@', '%40')}?style=flat-square&amp;color=3FB950&amp;label={name.replace('@', '%40')}"
        svg_content += f'<a href="{escape_xml(url)}" target="_blank"><image href="{badge}" x="0" y="{y_pos - 12}" height="20" /></a>\n'
        y_pos += 30

    # PyPI packages
    for pkg in open_source.get('pypi', []):
        name = pkg.get('name', '')
        url = pkg.get('url', '')
        badge = f"https://img.shields.io/pypi/v/{name}?style=flat-square&amp;color=58A6FF&amp;label={name}"
        svg_content += f'<a href="{escape_xml(url)}" target="_blank"><image href="{badge}" x="0" y="{y_pos - 12}" height="20" /></a>\n'
        y_pos += 30

    svg_content += f"""
            </g>

            <!-- CONTACT -->
            <g transform="translate(0, 665)">
                <text x="0" y="0" class="title">CONTACT</text>
                <a href="{escape_xml(contact.get('github', ''))}" target="_blank"><text x="0" y="25" class="value">gitHub</text></a>
                <a href="{escape_xml(contact.get('linkedin', ''))}" target="_blank"><text x="90" y="25" class="value">linkedIn</text></a>
                <a href="{escape_xml(contact.get('portfolio', ''))}" target="_blank"><text x="200" y="25" class="value">portfolio</text></a>
                <a href="{escape_xml(contact.get('email', ''))}" target="_blank"><text x="310" y="25" class="value">email</text></a>
            </g>
        </g>
    </g>
</svg>"""

    return svg_content

def main():
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("config.json not found")
        return
        
    try:
        with open("github_data.json", "r") as f:
            github_data = json.load(f)
    except FileNotFoundError:
        print("github_data.json not found. Run fetch_github_data.py first.")
        github_data = {}
        
    try:
        with open("assets/theme.json", "r") as f:
            theme = json.load(f)
    except FileNotFoundError:
        theme = {}
        
    portrait_b64 = get_base64_image("assets/portrait.png")
    
    svg = generate_svg(config, theme, portrait_b64, github_data)
    
    os.makedirs("assets", exist_ok=True)
    with open("assets/dashboard.svg", "w", encoding="utf-8") as f:
        f.write(svg)
        
    print("Dashboard SVG generated at assets/dashboard.svg")

if __name__ == "__main__":
    main()
