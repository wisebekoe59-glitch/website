from flask import Flask, request, redirect, url_for, session, render_template_string, flash
import sqlite3
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

# ============================================================
# MC_UNIFINDER
# Complete Flask + SQLite application in ONE Python file
# ============================================================

app = Flask(__name__)

# Change this to a stronger secret before deploying publicly
app.secret_key = "mc-unifinder-secret-key-change-this"

DATABASE = "unifinder.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_db():

    conn = get_db()

    # --------------------------------------------------------
    # UNIVERSITIES TABLE
    # --------------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS universities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            type TEXT NOT NULL,
            website TEXT,
            description TEXT
        )
    """)

    # --------------------------------------------------------
    # PROGRAMMES TABLE
    # --------------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS programmes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            university_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            department TEXT,
            duration TEXT,
            requirements TEXT,
            careers TEXT,
            description TEXT,
            FOREIGN KEY (university_id) REFERENCES universities(id)
        )
    """)

    # --------------------------------------------------------
    # ADMINS TABLE
    # --------------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # ========================================================
    # ADMIN ACCOUNT
    # ========================================================

    admin_username = "Bekoewise99"
    admin_password = "Bekoewise99@"

    # Check if new admin already exists
    admin = conn.execute(
        "SELECT * FROM admins WHERE username = ?",
        (admin_username,)
    ).fetchone()

    if not admin:

        # Find existing admin account
        old_admin = conn.execute(
            "SELECT * FROM admins ORDER BY id LIMIT 1"
        ).fetchone()

        if old_admin:

            # Convert old admin to new credentials
            conn.execute(
                """
                UPDATE admins
                SET username = ?, password = ?
                WHERE id = ?
                """,
                (
                    admin_username,
                    generate_password_hash(admin_password),
                    old_admin["id"]
                )
            )

        else:

            # Create completely new admin
            conn.execute(
                """
                INSERT INTO admins (username, password)
                VALUES (?, ?)
                """,
                (
                    admin_username,
                    generate_password_hash(admin_password)
                )
            )

    # ========================================================
    # SAMPLE UNIVERSITIES
    # ========================================================

    count = conn.execute(
        "SELECT COUNT(*) AS total FROM universities"
    ).fetchone()["total"]

    if count == 0:

        universities = [

            (
                "University of Ghana",
                "Legon, Accra",
                "Public",
                "https://www.ug.edu.gh",
                "Ghana's premier public university offering a wide range of academic programmes."
            ),

            (
                "Kwame Nkrumah University of Science and Technology",
                "Kumasi",
                "Public",
                "https://www.knust.edu.gh",
                "A leading university in science, technology, engineering, business and related disciplines."
            ),

            (
                "University of Cape Coast",
                "Cape Coast",
                "Public",
                "https://www.ucc.edu.gh",
                "A major Ghanaian university known for teacher education, business, humanities and sciences."
            ),

            (
                "University of Mines and Technology",
                "Tarkwa",
                "Public",
                "https://www.umat.edu.gh",
                "A university specialising in mining, engineering, technology, business and related fields."
            ),

            (
                "University of Professional Studies, Accra",
                "Accra",
                "Public",
                "https://upsa.edu.gh",
                "A public university with strong programmes in accounting, finance, business and related areas."
            ),

            (
                "University of Education, Winneba",
                "Winneba",
                "Public",
                "https://www.uew.edu.gh",
                "A university specialising in education, arts, business, sciences and related disciplines."
            ),

            (
                "University for Development Studies",
                "Tamale",
                "Public",
                "https://uds.edu.gh",
                "A multi-campus public university serving northern Ghana and beyond."
            ),

            (
                "University of Energy and Natural Resources",
                "Sunyani",
                "Public",
                "https://uenr.edu.gh",
                "A university focused on energy, natural resources, engineering, business and related fields."
            ),

            (
                "Ghana Communication Technology University",
                "Accra",
                "Public",
                "https://site.gctu.edu.gh",
                "A technology-focused university offering programmes in computing, business and communication."
            )
        ]

        conn.executemany(
            """
            INSERT INTO universities
            (name, location, type, website, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            universities
        )

        # Get university IDs
        uni = {
            row["name"]: row["id"]
            for row in conn.execute(
                "SELECT id, name FROM universities"
            )
        }

        # ====================================================
        # SAMPLE PROGRAMMES + FUTURE CAREERS
        # ====================================================

        programmes = [

            (
                uni["University of Ghana"],
                "BSc Computer Science",
                "Department of Computer Science",
                "4 years",
                "WASSCE applicants should meet the university's approved admission requirements.",
                "Software Engineer, Data Scientist, Data Analyst, AI Engineer, Cybersecurity Analyst, Systems Analyst, Cloud Engineer",
                "A programme covering computing, programming, algorithms, databases and software development."
            ),

            (
                uni["University of Ghana"],
                "BSc Business Administration",
                "Business School",
                "4 years",
                "Applicants must meet the approved admission requirements.",
                "Business Analyst, Operations Manager, Entrepreneur, Management Consultant, Project Coordinator, Marketing Officer",
                "A business programme covering management, accounting, finance and organisational studies."
            ),

            (
                uni["Kwame Nkrumah University of Science and Technology"],
                "BSc Computer Science",
                "Department of Computer Science",
                "4 years",
                "Applicants must meet KNUST admission requirements.",
                "Software Engineer, Data Scientist, AI Engineer, Cybersecurity Analyst, Systems Analyst, Database Administrator",
                "A computing programme focused on software, algorithms, systems and information technology."
            ),

            (
                uni["Kwame Nkrumah University of Science and Technology"],
                "BSc Actuarial Science",
                "Department of Statistics and Actuarial Science",
                "4 years",
                "Applicants must meet the university's mathematics and admission requirements.",
                "Actuary, Risk Analyst, Financial Analyst, Insurance Analyst, Pension Analyst, Investment Analyst",
                "A quantitative programme combining mathematics, statistics, finance and risk management."
            ),

            (
                uni["University of Cape Coast"],
                "BSc Information Technology",
                "Department of Information Technology",
                "4 years",
                "Applicants must meet UCC admission requirements.",
                "IT Officer, Web Developer, Systems Analyst, Database Administrator, Network Administrator, Technology Consultant",
                "A programme focusing on information technology, systems and digital solutions."
            ),

            (
                uni["University of Cape Coast"],
                "BCom Accounting",
                "School of Business",
                "4 years",
                "Applicants must meet approved admission requirements.",
                "Accountant, Auditor, Tax Officer, Financial Analyst, Internal Auditor, Finance Officer",
                "A programme covering accounting principles, financial reporting, auditing and taxation."
            ),

            (
                uni["University of Mines and Technology"],
                "BSc Finance and Data Science",
                "Department of Finance and Data Science",
                "4 years",
                "Applicants must satisfy UMaT admission requirements.",
                "Financial Data Scientist, Data Scientist, Financial Analyst, Business Intelligence Analyst, Risk Analyst, Data Analyst, Machine Learning Analyst",
                "An interdisciplinary programme combining finance, statistics, programming and data science."
            ),

            (
                uni["University of Mines and Technology"],
                "BSc Computer Science",
                "Department of Computer Science and Engineering",
                "4 years",
                "Applicants must satisfy UMaT admission requirements.",
                "Software Engineer, Data Scientist, Data Analyst, Systems Analyst, IT Specialist, Cybersecurity Analyst",
                "A programme designed to develop strong computing and software development skills."
            ),

            (
                uni["University of Professional Studies, Accra"],
                "BSc Banking and Finance",
                "Department of Banking and Finance",
                "4 years",
                "Applicants must meet UPSA admission requirements.",
                "Banker, Financial Analyst, Credit Analyst, Investment Analyst, Risk Analyst, Treasury Analyst",
                "A programme focused on banking, investment, financial markets and financial management."
            ),

            (
                uni["University of Professional Studies, Accra"],
                "BSc Data Science",
                "Department of Information Technology",
                "4 years",
                "Applicants must meet approved admission requirements.",
                "Data Scientist, Data Analyst, Machine Learning Engineer, Business Intelligence Analyst, Data Engineer, Statistician",
                "A programme combining statistics, computing, programming and data-driven decision making."
            ),

            (
                uni["University of Education, Winneba"],
                "BSc Information Technology",
                "Department of ICT",
                "4 years",
                "Applicants must meet UEW admission requirements.",
                "IT Officer, Systems Analyst, Web Developer, Database Administrator, Network Administrator, Technology Consultant",
                "A technology programme covering computing and information systems."
            ),

            (
                uni["University for Development Studies"],
                "BSc Business Administration",
                "School of Business",
                "4 years",
                "Applicants must meet UDS admission requirements.",
                "Business Analyst, Entrepreneur, Manager, Administrative Officer, Operations Officer, Project Coordinator",
                "A programme covering business management and organisational decision making."
            ),

            (
                uni["University of Energy and Natural Resources"],
                "BSc Computer Science",
                "Department of Computer Science",
                "4 years",
                "Applicants must meet UENR admission requirements.",
                "Software Engineer, Data Analyst, Data Scientist, IT Specialist, Systems Analyst, Cybersecurity Analyst",
                "A computing programme combining theoretical and practical computing skills."
            ),

            (
                uni["Ghana Communication Technology University"],
                "BSc Information Technology",
                "School of Computing and Information Technology",
                "4 years",
                "Applicants must meet GCTU admission requirements.",
                "Software Engineer, IT Officer, Systems Analyst, Network Administrator, Database Administrator, Technology Consultant",
                "A programme designed around computing, information systems and digital technologies."
            )
        ]

        conn.executemany(
            """
            INSERT INTO programmes
            (
                university_id,
                name,
                department,
                duration,
                requirements,
                careers,
                description
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            programmes
        )

    conn.commit()
    conn.close()


# ============================================================
# ADMIN DECORATOR
# ============================================================

def admin_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))

        return function(*args, **kwargs)

    return wrapper


# ============================================================
# CSS
# ============================================================

CSS = """
<style>

:root {
    --primary: #0d6efd;
    --dark: #0b1f33;
    --light: #f5f7fb;
    --white: #ffffff;
    --success: #198754;
}

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, Helvetica, sans-serif;
    background: var(--light);
    color: #1f2937;
}

/* =========================================================
   NAVBAR
   ========================================================= */

.navbar {
    background: var(--dark);
    color: white;
    padding: 16px 6%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
}

.logo {
    font-size: 24px;
    font-weight: bold;
    color: white;
    text-decoration: none;
}

.logo span {
    color: #55a8ff;
}

.nav-links {
    display: flex;
    gap: 20px;
    align-items: center;
    flex-wrap: wrap;
}

.nav-links a {
    color: white;
    text-decoration: none;
}

.nav-links a:hover {
    color: #55a8ff;
}

/* =========================================================
   CONTAINER
   ========================================================= */

.container {
    width: 88%;
    max-width: 1200px;
    margin: auto;
}

/* =========================================================
   HERO
   Students holding books background
   ========================================================= */

.hero {

    background:
        linear-gradient(
            rgba(11, 31, 51, 0.78),
            rgba(13, 110, 253, 0.75)
        ),
        url("https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=1800&q=85");

    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;

    color: white;

    padding: 110px 8%;

    text-align: center;

    min-height: 500px;

    display: flex;
    flex-direction: column;
    justify-content: center;
}

.hero h1 {
    font-size: 50px;
    margin-bottom: 15px;
}

.hero p {
    font-size: 19px;
    max-width: 750px;
    margin: 0 auto 30px;
}

/* =========================================================
   SEARCH
   ========================================================= */

.search-box {
    max-width: 750px;
    margin: auto;
    display: flex;
    gap: 10px;
}

.search-box input {
    flex: 1;
    padding: 16px;
    border: none;
    border-radius: 8px;
    font-size: 16px;
}

/* =========================================================
   BUTTONS
   ========================================================= */

.btn {
    display: inline-block;
    padding: 11px 18px;
    border-radius: 7px;
    text-decoration: none;
    border: none;
    cursor: pointer;
    font-size: 15px;
}

.btn-primary {
    background: var(--primary);
    color: white;
}

.btn-dark {
    background: var(--dark);
    color: white;
}

.btn-success {
    background: var(--success);
    color: white;
}

.btn-danger {
    background: #dc3545;
    color: white;
}

.btn-secondary {
    background: #6c757d;
    color: white;
}

/* =========================================================
   SECTIONS
   ========================================================= */

.section {
    padding: 50px 0;
}

.section-title {
    text-align: center;
    margin-bottom: 35px;
}

/* =========================================================
   GRID
   ========================================================= */

.grid {
    display: grid;
    grid-template-columns: repeat(
        auto-fit,
        minmax(270px, 1fr)
    );
    gap: 22px;
}

/* =========================================================
   CARDS
   ========================================================= */

.card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 4px 15px rgba(0,0,0,.07);
}

.card h3 {
    margin-top: 0;
}

.card a {
    color: var(--primary);
    text-decoration: none;
}

/* =========================================================
   BADGE
   ========================================================= */

.badge {
    display: inline-block;
    padding: 5px 10px;
    background: #e7f1ff;
    color: var(--primary);
    border-radius: 20px;
    font-size: 13px;
}

/* =========================================================
   CAREER BOX
   ========================================================= */

.career-box {

    background: #eef7ff;

    border-left: 5px solid var(--primary);

    padding: 18px;

    border-radius: 8px;

    margin-top: 15px;

    line-height: 1.7;
}

.career-title {

    color: var(--primary);

    font-size: 20px;

    margin-bottom: 8px;
}

/* =========================================================
   FORMS
   ========================================================= */

.form-card {
    max-width: 650px;
    margin: 50px auto;
    background: white;
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,.08);
}

.form-group {
    margin-bottom: 17px;
}

.form-group label {
    display: block;
    margin-bottom: 7px;
    font-weight: bold;
}

.form-group input,
.form-group textarea,
.form-group select {
    width: 100%;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 7px;
    font-size: 15px;
}

.form-group textarea {
    min-height: 120px;
}

/* =========================================================
   TABLES
   ========================================================= */

.table-wrapper {
    overflow-x: auto;
    background: white;
    border-radius: 10px;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    padding: 13px;
    border-bottom: 1px solid #eee;
    text-align: left;
}

th {
    background: #f1f5f9;
}

/* =========================================================
   ADMIN DASHBOARD
   ========================================================= */

.dashboard {
    padding: 45px 0;
}

.stats {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(210px, 1fr));

    gap: 20px;

    margin-bottom: 35px;
}

.stat {
    background: white;
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 3px 15px rgba(0,0,0,.06);
}

.stat h2 {
    margin: 0;
    font-size: 35px;
    color: var(--primary);
}

.admin-nav {
    background: #162b40;
    padding: 13px;
    margin-bottom: 25px;
    border-radius: 8px;
}

.admin-nav a {
    color: white;
    text-decoration: none;
    margin-right: 20px;
}

/* =========================================================
   ALERT
   ========================================================= */

.alert {
    padding: 12px 18px;
    border-radius: 7px;
    margin: 15px auto;
    max-width: 1200px;
    background: #dff0ff;
}

/* =========================================================
   FOOTER
   ========================================================= */

.footer {
    background: var(--dark);
    color: white;
    text-align: center;
    padding: 30px;
    margin-top: 50px;
}

/* =========================================================
   MOBILE
   ========================================================= */

@media(max-width: 700px) {

    .hero h1 {
        font-size: 34px;
    }

    .search-box {
        flex-direction: column;
    }

    .navbar {
        gap: 15px;
    }

}

</style>
"""


# ============================================================
# BASE HTML
# ============================================================

BASE = """
<!DOCTYPE html>

<html>

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>
        {{ title }} | MC_UNIFINDER
    </title>

    {{ css|safe }}

</head>


<body>


<nav class="navbar">

    <a
        class="logo"
        href="{{ url_for('home') }}"
    >
        MC_<span>UNIFINDER</span>
    </a>


    <div class="nav-links">

        <a href="{{ url_for('home') }}">
            Home
        </a>

        <a href="{{ url_for('universities') }}">
            Universities
        </a>

        <a href="{{ url_for('programmes') }}">
            Programmes
        </a>

        <a href="{{ url_for('compare') }}">
            Compare
        </a>

        <a href="{{ url_for('saved') }}">
            Saved
        </a>


        {% if session.get("admin_logged_in") %}

            <a href="{{ url_for('admin_dashboard') }}">
                Admin
            </a>

        {% else %}

            <a href="{{ url_for('admin_login') }}">
                Admin Login
            </a>

        {% endif %}

    </div>

</nav>


{% with messages = get_flashed_messages() %}

    {% for message in messages %}

        <div class="alert">
            {{ message }}
        </div>

    {% endfor %}

{% endwith %}


{{ content|safe }}


<footer class="footer">

    <strong>
        MC_UNIFINDER
    </strong>

    <p>
        Choose your university. Discover your future.
    </p>

    <p>
        © 2026 MC_UNIFINDER
    </p>

</footer>


</body>

</html>
"""


# ============================================================
# PAGE FUNCTION
# ============================================================

def page(title, content):

    return render_template_string(
        BASE,
        title=title,
        css=CSS,
        content=content
    )


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    conn = get_db()

    universities = conn.execute(
        """
        SELECT *
        FROM universities
        ORDER BY name
        """
    ).fetchall()

    programmes = conn.execute(
        """
        SELECT programmes.*,
               universities.name AS university_name

        FROM programmes

        JOIN universities
        ON programmes.university_id = universities.id

        ORDER BY programmes.name
        """
    ).fetchall()

    conn.close()

    html = """

<section class="hero">

    <h1>
        Choose Your University.
    </h1>


    <p>

        Discover universities and programmes in Ghana,
        explore admission information,
        future career opportunities,
        and find your future.

    </p>


    <form
        class="search-box"
        action="/search"
        method="get"
    >

        <input
            type="text"
            name="q"
            placeholder="Search university or programme..."
        >

        <button class="btn btn-primary">
            Search
        </button>

    </form>

</section>


<section class="section container">

    <div class="section-title">

        <h2>
            Explore Universities
        </h2>

        <p>
            Discover Ghanaian universities
            and what they offer.
        </p>

    </div>


    <div class="grid">

        {% for university in universities %}

        <div class="card">

            <span class="badge">
                {{ university['type'] }}
            </span>


            <h3>
                {{ university['name'] }}
            </h3>


            <p>
                📍 {{ university['location'] }}
            </p>


            <p>
                {{ university['description'] }}
            </p>


            <a
                class="btn btn-primary"
                href="/university/{{ university['id'] }}"
            >
                View University
            </a>

        </div>

        {% endfor %}

    </div>

</section>


<section class="section container">

    <div class="section-title">

        <h2>
            Popular Programmes
        </h2>

        <p>
            Explore programmes and the careers
            they can lead to.
        </p>

    </div>


    <div class="grid">

        {% for programme in programmes[:8] %}

        <div class="card">

            <h3>
                {{ programme['name'] }}
            </h3>


            <p>
                <strong>
                    {{ programme['university_name'] }}
                </strong>
            </p>


            <p>
                {{ programme['department'] }}
            </p>


            <span class="badge">
                {{ programme['duration'] }}
            </span>


            <div class="career-box">

                <div class="career-title">
                    Future Careers
                </div>

                <div>
                    {{ programme['careers'] }}
                </div>

            </div>


            <br>


            <a
                class="btn btn-primary"
                href="/programme/{{ programme['id'] }}"
            >
                View Programme
            </a>

        </div>

        {% endfor %}

    </div>

</section>

"""

    return render_template_string(
        BASE,
        title="Home",
        css=CSS,
        content=render_template_string(
            html,
            universities=universities,
            programmes=programmes
        )
    )


# ============================================================
# UNIVERSITIES
# ============================================================

@app.route("/universities")
def universities():

    search = request.args.get(
        "q",
        ""
    ).strip()

    conn = get_db()

    if search:

        universities = conn.execute(
            """
            SELECT *
            FROM universities

            WHERE name LIKE ?
            OR location LIKE ?

            ORDER BY name
            """,
            (
                f"%{search}%",
                f"%{search}%"
            )
        ).fetchall()

    else:

        universities = conn.execute(
            """
            SELECT *
            FROM universities
            ORDER BY name
            """
        ).fetchall()

    conn.close()

    html = """

<div class="section container">

    <div class="section-title">

        <h1>
            Universities in Ghana
        </h1>


        <form
            action="/universities"
            method="get"
        >

            <input
                type="text"
                name="q"
                value="{{ search }}"
                placeholder="Search universities..."
                style="padding:12px;width:70%;max-width:500px"
            >


            <button class="btn btn-primary">
                Search
            </button>

        </form>

    </div>


    <div class="grid">

        {% for university in universities %}

        <div class="card">

            <span class="badge">
                {{ university['type'] }}
            </span>


            <h3>
                {{ university['name'] }}
            </h3>


            <p>
                📍 {{ university['location'] }}
            </p>


            <p>
                {{ university['description'] }}
            </p>


            <a
                href="/university/{{ university['id'] }}"
                class="btn btn-primary"
            >
                Explore
            </a>

        </div>


        {% else %}

        <p>
            No university found.
        </p>

        {% endfor %}

    </div>

</div>

"""

    return render_template_string(
        BASE,
        title="Universities",
        css=CSS,
        content=render_template_string(
            html,
            universities=universities,
            search=search
        )
    )


# ============================================================
# UNIVERSITY DETAILS
# ============================================================

@app.route("/university/<int:university_id>")
def university(university_id):

    conn = get_db()

    university = conn.execute(
        """
        SELECT *
        FROM universities
        WHERE id = ?
        """,
        (university_id,)
    ).fetchone()

    programmes = conn.execute(
        """
        SELECT *
        FROM programmes

        WHERE university_id = ?

        ORDER BY name
        """,
        (university_id,)
    ).fetchall()

    conn.close()

    if not university:

        return "University not found", 404

    html = """

<div class="section container">

    <div class="card">

        <span class="badge">
            {{ university['type'] }}
        </span>


        <h1>
            {{ university['name'] }}
        </h1>


        <p>
            📍 {{ university['location'] }}
        </p>


        <p>
            {{ university['description'] }}
        </p>


        {% if university['website'] %}

        <a
            class="btn btn-dark"
            href="{{ university['website'] }}"
            target="_blank"
        >
            Official Website
        </a>

        {% endif %}

    </div>


    <br>


    <h2>
        Programmes Offered
    </h2>


    <div class="grid">

        {% for programme in programmes %}

        <div class="card">

            <h3>
                {{ programme['name'] }}
            </h3>


            <p>
                {{ programme['department'] }}
            </p>


            <span class="badge">
                {{ programme['duration'] }}
            </span>


            <div class="career-box">

                <div class="career-title">
                    Future Career Opportunities
                </div>

                <div>
                    {{ programme['careers'] }}
                </div>

            </div>


            <br>


            <a
                class="btn btn-primary"
                href="/programme/{{ programme['id'] }}"
            >
                View Details
            </a>

        </div>


        {% else %}

        <p>
            No programmes have been added yet.
        </p>

        {% endfor %}

    </div>

</div>

"""

    return render_template_string(
        BASE,
        title=university["name"],
        css=CSS,
        content=render_template_string(
            html,
            university=university,
            programmes=programmes
        )
    )


# ============================================================
# PROGRAMMES
# ============================================================

@app.route("/programmes")
def programmes():

    search = request.args.get(
        "q",
        ""
    ).strip()

    conn = get_db()

    if search:

        programmes = conn.execute(
            """
            SELECT programmes.*,
                   universities.name AS university_name

            FROM programmes

            JOIN universities
            ON programmes.university_id = universities.id

            WHERE programmes.name LIKE ?
            OR universities.name LIKE ?
            OR programmes.department LIKE ?

            ORDER BY programmes.name
            """,
            (
                f"%{search}%",
                f"%{search}%",
                f"%{search}%"
            )
        ).fetchall()

    else:

        programmes = conn.execute(
            """
            SELECT programmes.*,
                   universities.name AS university_name

            FROM programmes

            JOIN universities
            ON programmes.university_id = universities.id

            ORDER BY programmes.name
            """
        ).fetchall()

    conn.close()

    html = """

<div class="section container">

    <div class="section-title">

        <h1>
            Programmes
        </h1>


        <form
            action="/programmes"
            method="get"
        >

            <input
                type="text"
                name="q"
                value="{{ search }}"
                placeholder="Search programmes..."
                style="padding:12px;width:70%;max-width:500px"
            >


            <button class="btn btn-primary">
                Search
            </button>

        </form>

    </div>


    <div class="grid">

        {% for programme in programmes %}

        <div class="card">

            <h3>
                {{ programme['name'] }}
            </h3>


            <p>
                <strong>
                    {{ programme['university_name'] }}
                </strong>
            </p>


            <p>
                {{ programme['department'] }}
            </p>


            <span class="badge">
                {{ programme['duration'] }}
            </span>


            <div class="career-box">

                <div class="career-title">
                    Future Careers
                </div>

                <div>
                    {{ programme['careers'] }}
                </div>

            </div>


            <br>


            <a
                href="/programme/{{ programme['id'] }}"
                class="btn btn-primary"
            >
                View Details
            </a>


            <a
                href="/save/{{ programme['id'] }}"
                class="btn btn-success"
            >
                Save
            </a>

        </div>


        {% else %}

        <p>
            No programme found.
        </p>

        {% endfor %}

    </div>

</div>

"""

    return render_template_string(
        BASE,
        title="Programmes",
        css=CSS,
        content=render_template_string(
            html,
            programmes=programmes,
            search=search
        )
    )


# ============================================================
# PROGRAMME DETAILS
# ============================================================

@app.route("/programme/<int:programme_id>")
def programme(programme_id):

    conn = get_db()

    programme = conn.execute(
        """
        SELECT programmes.*,
               universities.name AS university_name,
               universities.location AS university_location

        FROM programmes

        JOIN universities
        ON programmes.university_id = universities.id

        WHERE programmes.id = ?
        """,
        (programme_id,)
    ).fetchone()

    conn.close()

    if not programme:

        return "Programme not found", 404

    html = """

<div class="section container">

    <div class="card">

        <span class="badge">
            {{ programme['duration'] }}
        </span>


        <h1>
            {{ programme['name'] }}
        </h1>


        <h3>
            {{ programme['university_name'] }}
        </h3>


        <p>
            📍 {{ programme['university_location'] }}
        </p>


        <hr>


        <h3>
            Department
        </h3>

        <p>
            {{ programme['department'] }}
        </p>


        <h3>
            Description
        </h3>

        <p>
            {{ programme['description'] }}
        </p>


        <h3>
            Admission Requirements
        </h3>

        <p>
            {{ programme['requirements'] }}
        </p>


        <div class="career-box">

            <div class="career-title">
                Future Career Opportunities
            </div>

            <p>
                {{ programme['careers'] }}
            </p>

        </div>


        <br>


        <a
            class="btn btn-success"
            href="/save/{{ programme['id'] }}"
        >
            Save Programme
        </a>


        <a
            class="btn btn-primary"
            href="/compare?add={{ programme['id'] }}"
        >
            Add to Compare
        </a>

    </div>

</div>

"""

    return render_template_string(
        BASE,
        title=programme["name"],
        css=CSS,
        content=render_template_string(
            html,
            programme=programme
        )
    )


# ============================================================
# SEARCH
# ============================================================

@app.route("/search")
def search():

    q = request.args.get(
        "q",
        ""
    ).strip()

    if not q:

        return redirect(
            url_for("home")
        )

    conn = get_db()

    universities = conn.execute(
        """
        SELECT *
        FROM universities

        WHERE name LIKE ?
        OR location LIKE ?
        """,
        (
            f"%{q}%",
            f"%{q}%"
        )
    ).fetchall()

    programmes = conn.execute(
        """
        SELECT programmes.*,
               universities.name AS university_name

        FROM programmes

        JOIN universities
        ON programmes.university_id = universities.id

        WHERE programmes.name LIKE ?
        OR programmes.department LIKE ?
        OR universities.name LIKE ?
        OR programmes.careers LIKE ?
        """,
        (
            f"%{q}%",
            f"%{q}%",
            f"%{q}%",
            f"%{q}%"
        )
    ).fetchall()

    conn.close()

    html = """

<div class="section container">

    <h1>
        Search Results
    </h1>


    <p>
        Results for:
        <strong>{{ q }}</strong>
    </p>


    <h2>
        Universities
    </h2>


    <div class="grid">

        {% for university in universities %}

        <div class="card">

            <h3>
                {{ university['name'] }}
            </h3>

            <p>
                {{ university['location'] }}
            </p>

            <a
                class="btn btn-primary"
                href="/university/{{ university['id'] }}"
            >
                View
            </a>

        </div>


        {% else %}

        <p>
            No universities found.
        </p>

        {% endfor %}

    </div>


    <br><br>


    <h2>
        Programmes
    </h2>


    <div class="grid">

        {% for programme in programmes %}

        <div class="card">

            <h3>
                {{ programme['name'] }}
            </h3>


            <p>
                {{ programme['university_name'] }}
            </p>


            <div class="career-box">

                <strong>
                    Future Careers
                </strong>

                <p>
                    {{ programme['careers'] }}
                </p>

            </div>


            <a
                class="btn btn-primary"
                href="/programme/{{ programme['id'] }}"
            >
                View
            </a>

        </div>


        {% else %}

        <p>
            No programmes found.
        </p>

        {% endfor %}

    </div>

</div>

"""

    return render_template_string(
        BASE,
        title="Search",
        css=CSS,
        content=render_template_string(
            html,
            q=q,
            universities=universities,
            programmes=programmes
        )
    )


# ============================================================
# SAVE PROGRAMMES
# ============================================================

@app.route("/save/<int:programme_id>")
def save(programme_id):

    saved = session.get(
        "saved",
        []
    )

    if programme_id not in saved:

        saved.append(programme_id)

    session["saved"] = saved

    flash(
        "Programme saved successfully."
    )

    return redirect(
        request.referrer
        or url_for("programmes")
    )


# ============================================================
# REMOVE SAVED PROGRAMME
# ============================================================

@app.route("/remove-save/<int:programme_id>")
def remove_save(programme_id):

    saved = session.get(
        "saved",
        []
    )

    if programme_id in saved:

        saved.remove(programme_id)

    session["saved"] = saved

    flash(
        "Programme removed."
    )

    return redirect(
        url_for("saved")
    )


# ============================================================
# SAVED PROGRAMMES PAGE
# ============================================================

@app.route("/saved")
def saved():

    saved_ids = session.get(
        "saved",
        []
    )

    programmes = []

    if saved_ids:

        conn = get_db()

        placeholders = ",".join(
            "?" for _ in saved_ids
        )

        programmes = conn.execute(
            f"""
            SELECT programmes.*,
                   universities.name AS university_name

            FROM programmes

            JOIN universities
            ON programmes.university_id = universities.id

            WHERE programmes.id IN ({placeholders})
            """,
            saved_ids
        ).fetchall()

        conn.close()

    html = """

<div class="section container">

    <h1>
        Saved Programmes
    </h1>


    {% if programmes %}

    <div class="grid">

        {% for programme in programmes %}

        <div class="card">

            <h3>
                {{ programme['name'] }}
            </h3>


            <p>
                {{ programme['university_name'] }}
            </p>


            <div class="career-box">

                <strong>
                    Future Careers
                </strong>

                <p>
                    {{ programme['careers'] }}
                </p>

            </div>


            <a
                class="btn btn-primary"
                href="/programme/{{ programme['id'] }}"
            >
                View
            </a>


            <a
                class="btn btn-danger"
                href="/remove-save/{{ programme['id'] }}"
            >
                Remove
            </a>

        </div>

        {% endfor %}

    </div>


    {% else %}

    <div class="card">

        <h3>
            No saved programmes yet.
        </h3>


        <p>
            Browse programmes and click Save
            to keep them here.
        </p>


        <a
            class="btn btn-primary"
            href="/programmes"
        >
            Browse Programmes
        </a>

    </div>

    {% endif %}

</div>

"""

    return render_template_string(
        BASE,
        title="Saved Programmes",
        css=CSS,
        content=render_template_string(
            html,
            programmes=programmes
        )
    )


# ============================================================
# COMPARE
# ============================================================

@app.route("/compare")
def compare():

    if request.args.get("add"):

        try:

            programme_id = int(
                request.args.get("add")
            )

            compare_list = session.get(
                "compare",
                []
            )

            if programme_id not in compare_list:

                compare_list.append(
                    programme_id
                )

            # Maximum 3
            compare_list = compare_list[-3:]

            session["compare"] = compare_list

        except ValueError:

            pass

        return redirect(
            url_for("compare")
        )

    compare_ids = session.get(
        "compare",
        []
    )

    programmes = []

    if compare_ids:

        conn = get_db()

        placeholders = ",".join(
            "?" for _ in compare_ids
        )

        programmes = conn.execute(
            f"""
            SELECT programmes.*,
                   universities.name AS university_name

            FROM programmes

            JOIN universities
            ON programmes.university_id = universities.id

            WHERE programmes.id IN ({placeholders})
            """,
            compare_ids
        ).fetchall()

        conn.close()

    html = """

<div class="section container">

    <h1>
        Compare Programmes
    </h1>


    <p>
        You can compare up to three programmes.
    </p>


    {% if programmes %}

    <div class="table-wrapper">

        <table>

            <tr>

                <th>
                    Information
                </th>


                {% for programme in programmes %}

                <th>
                    {{ programme['name'] }}
                </th>

                {% endfor %}

            </tr>


            <tr>

                <td>
                    University
                </td>


                {% for programme in programmes %}

                <td>
                    {{ programme['university_name'] }}
                </td>

                {% endfor %}

            </tr>


            <tr>

                <td>
                    Department
                </td>


                {% for programme in programmes %}

                <td>
                    {{ programme['department'] }}
                </td>

                {% endfor %}

            </tr>


            <tr>

                <td>
                    Duration
                </td>


                {% for programme in programmes %}

                <td>
                    {{ programme['duration'] }}
                </td>

                {% endfor %}

            </tr>


            <tr>

                <td>
                    Admission Requirements
                </td>


                {% for programme in programmes %}

                <td>
                    {{ programme['requirements'] }}
                </td>

                {% endfor %}

            </tr>


            <tr>

                <td>
                    Future Career Opportunities
                </td>


                {% for programme in programmes %}

                <td>
                    {{ programme['careers'] }}
                </td>

                {% endfor %}

            </tr>


            <tr>

                <td>
                    Description
                </td>


                {% for programme in programmes %}

                <td>
                    {{ programme['description'] }}
                </td>

                {% endfor %}

            </tr>

        </table>

    </div>


    {% else %}

    <div class="card">

        <h3>
            No programmes selected.
        </h3>


        <p>
            Go to Programmes and click
            "Add to Compare".
        </p>


        <a
            class="btn btn-primary"
            href="/programmes"
        >
            Browse Programmes
        </a>

    </div>

    {% endif %}

</div>

"""

    return render_template_string(
        BASE,
        title="Compare",
        css=CSS,
        content=render_template_string(
            html,
            programmes=programmes
        )
    )


# ============================================================
# ADMIN LOGIN
# ============================================================

@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        username = request.form.get(
            "username"
        )

        password = request.form.get(
            "password"
        )

        conn = get_db()

        admin = conn.execute(
            """
            SELECT *
            FROM admins
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

        conn.close()

        if admin and check_password_hash(
            admin["password"],
            password
        ):

            session["admin_logged_in"] = True

            return redirect(
                url_for("admin_dashboard")
            )

        flash(
            "Invalid username or password."
        )

    html = """

<div class="form-card">

    <h1>
        MC_UNIFINDER Admin Login
    </h1>


    <p>
        Login to manage universities,
        programmes and future career information.
    </p>


    <form method="post">

        <div class="form-group">

            <label>
                Username
            </label>


            <input
                type="text"
                name="username"
                required
            >

        </div>


        <div class="form-group">

            <label>
                Password
            </label>


            <input
                type="password"
                name="password"
                required
            >

        </div>


        <button class="btn btn-primary">
            Login
        </button>

    </form>


    <br>

    <small>
        Use the administrator credentials provided for MC_UNIFINDER.
    </small>

</div>

"""

    return render_template_string(
        BASE,
        title="Admin Login",
        css=CSS,
        content=render_template_string(html)
    )


# ============================================================
# ADMIN LOGOUT
# ============================================================

@app.route("/admin/logout")
def admin_logout():

    session.pop(
        "admin_logged_in",
        None
    )

    return redirect(
        url_for("home")
    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route("/admin")
@admin_required
def admin_dashboard():

    conn = get_db()

    university_count = conn.execute(
        """
        SELECT COUNT(*) AS total
        FROM universities
        """
    ).fetchone()["total"]

    programme_count = conn.execute(
        """
        SELECT COUNT(*) AS total
        FROM programmes
        """
    ).fetchone()["total"]

    admin_count = conn.execute(
        """
        SELECT COUNT(*) AS total
        FROM admins
        """
    ).fetchone()["total"]

    universities = conn.execute(
        """
        SELECT *
        FROM universities
        ORDER BY id DESC
        """
    ).fetchall()

    programmes = conn.execute(
        """
        SELECT programmes.*,
               universities.name AS university_name

        FROM programmes

        JOIN universities
        ON programmes.university_id = universities.id

        ORDER BY programmes.id DESC
        """
    ).fetchall()

    conn.close()

    html = """

<div class="dashboard container">

    <div class="admin-nav">

        <a href="/admin">
            Dashboard
        </a>


        <a href="/admin/university/add">
            Add University
        </a>


        <a href="/admin/programme/add">
            Add Programme
        </a>


        <a href="/admin/logout">
            Logout
        </a>

    </div>


    <h1>
        MC_UNIFINDER Admin Dashboard
    </h1>


    <p>
        Manage universities, programmes
        and future career opportunities.
    </p>


    <div class="stats">

        <div class="stat">

            <h2>
                {{ university_count }}
            </h2>

            <p>
                Universities
            </p>

        </div>


        <div class="stat">

            <h2>
                {{ programme_count }}
            </h2>

            <p>
                Programmes
            </p>

        </div>


        <div class="stat">

            <h2>
                {{ admin_count }}
            </h2>

            <p>
                Administrators
            </p>

        </div>

    </div>


    <h2>
        Manage Universities
    </h2>


    <div class="table-wrapper">

        <table>

            <tr>

                <th>
                    ID
                </th>

                <th>
                    Name
                </th>

                <th>
                    Location
                </th>

                <th>
                    Type
                </th>

                <th>
                    Actions
                </th>

            </tr>


            {% for university in universities %}

            <tr>

                <td>
                    {{ university['id'] }}
                </td>


                <td>
                    {{ university['name'] }}
                </td>


                <td>
                    {{ university['location'] }}
                </td>


                <td>
                    {{ university['type'] }}
                </td>


                <td>

                    <a
                        class="btn btn-primary"
                        href="/admin/university/edit/{{ university['id'] }}"
                    >
                        Edit
                    </a>


                    <a
                        class="btn btn-danger"
                        href="/admin/university/delete/{{ university['id'] }}"
                        onclick="return confirm('Delete this university and its programmes?')"
                    >
                        Delete
                    </a>

                </td>

            </tr>

            {% endfor %}

        </table>

    </div>


    <br><br>


    <h2>
        Manage Programmes
    </h2>


    <div class="table-wrapper">

        <table>

            <tr>

                <th>
                    ID
                </th>

                <th>
                    Programme
                </th>

                <th>
                    University
                </th>

                <th>
                    Duration
                </th>

                <th>
                    Future Careers
                </th>

                <th>
                    Actions
                </th>

            </tr>


            {% for programme in programmes %}

            <tr>

                <td>
                    {{ programme['id'] }}
                </td>


                <td>
                    {{ programme['name'] }}
                </td>


                <td>
                    {{ programme['university_name'] }}
                </td>


                <td>
                    {{ programme['duration'] }}
                </td>


                <td>
                    {{ programme['careers'] }}
                </td>


                <td>

                    <a
                        class="btn btn-primary"
                        href="/admin/programme/edit/{{ programme['id'] }}"
                    >
                        Edit
                    </a>


                    <a
                        class="btn btn-danger"
                        href="/admin/programme/delete/{{ programme['id'] }}"
                        onclick="return confirm('Delete this programme?')"
                    >
                        Delete
                    </a>

                </td>

            </tr>

            {% endfor %}

        </table>

    </div>

</div>

"""

    return render_template_string(
        BASE,
        title="Admin Dashboard",
        css=CSS,
        content=render_template_string(
            html,
            university_count=university_count,
            programme_count=programme_count,
            admin_count=admin_count,
            universities=universities,
            programmes=programmes
        )
    )


# ============================================================
# ADD UNIVERSITY
# ============================================================

@app.route(
    "/admin/university/add",
    methods=["GET", "POST"]
)
@admin_required
def add_university():

    if request.method == "POST":

        name = request.form["name"]

        location = request.form["location"]

        university_type = request.form["type"]

        website = request.form["website"]

        description = request.form["description"]

        conn = get_db()

        conn.execute(
            """
            INSERT INTO universities
            (
                name,
                location,
                type,
                website,
                description
            )

            VALUES (?, ?, ?, ?, ?)
            """,
            (
                name,
                location,
                university_type,
                website,
                description
            )
        )

        conn.commit()

        conn.close()

        flash(
            "University added successfully."
        )

        return redirect(
            url_for("admin_dashboard")
        )

    return university_form()


# ============================================================
# EDIT UNIVERSITY
# ============================================================

@app.route(
    "/admin/university/edit/<int:university_id>",
    methods=["GET", "POST"]
)
@admin_required
def edit_university(university_id):

    conn = get_db()

    university = conn.execute(
        """
        SELECT *
        FROM universities
        WHERE id = ?
        """,
        (university_id,)
    ).fetchone()

    if not university:

        conn.close()

        return "University not found", 404

    if request.method == "POST":

        conn.execute(
            """
            UPDATE universities

            SET name = ?,
                location = ?,
                type = ?,
                website = ?,
                description = ?

            WHERE id = ?
            """,
            (
                request.form["name"],
                request.form["location"],
                request.form["type"],
                request.form["website"],
                request.form["description"],
                university_id
            )
        )

        conn.commit()

        conn.close()

        flash(
            "University updated successfully."
        )

        return redirect(
            url_for("admin_dashboard")
        )

    conn.close()

    return university_form(
        university
    )


# ============================================================
# DELETE UNIVERSITY
# ============================================================

@app.route(
    "/admin/university/delete/<int:university_id>"
)
@admin_required
def delete_university(university_id):

    conn = get_db()

    conn.execute(
        """
        DELETE FROM programmes
        WHERE university_id = ?
        """,
        (university_id,)
    )

    conn.execute(
        """
        DELETE FROM universities
        WHERE id = ?
        """,
        (university_id,)
    )

    conn.commit()

    conn.close()

    flash(
        "University deleted."
    )

    return redirect(
        url_for("admin_dashboard")
    )


# ============================================================
# UNIVERSITY FORM
# ============================================================

def university_form(university=None):

    editing = university is not None

    html = """

<div class="form-card">

    <h1>

        {% if editing %}

            Edit University

        {% else %}

            Add University

        {% endif %}

    </h1>


    <form method="post">

        <div class="form-group">

            <label>
                University Name
            </label>


            <input
                type="text"
                name="name"
                value="{{ university['name'] if university else '' }}"
                required
            >

        </div>


        <div class="form-group">

            <label>
                Location
            </label>


            <input
                type="text"
                name="location"
                value="{{ university['location'] if university else '' }}"
                required
            >

        </div>


        <div class="form-group">

            <label>
                Type
            </label>


            <select name="type">

                <option
                    {% if university and university['type']=='Public' %}
                    selected
                    {% endif %}
                >
                    Public
                </option>


                <option
                    {% if university and university['type']=='Private' %}
                    selected
                    {% endif %}
                >
                    Private
                </option>

            </select>

        </div>


        <div class="form-group">

            <label>
                Official Website
            </label>


            <input
                type="url"
                name="website"
                value="{{ university['website'] if university else '' }}"
                placeholder="https://example.com"
            >

        </div>


        <div class="form-group">

            <label>
                Description
            </label>


            <textarea name="description">{{ university['description'] if university else '' }}</textarea>

        </div>


        <button class="btn btn-primary">

            {% if editing %}

                Update University

            {% else %}

                Add University

            {% endif %}

        </button>


        <a
            class="btn btn-secondary"
            href="/admin"
        >
            Cancel
        </a>

    </form>

</div>

"""

    return render_template_string(
        BASE,
        title="University Form",
        css=CSS,
        content=render_template_string(
            html,
            university=university,
            editing=editing
        )
    )


# ============================================================
# ADD PROGRAMME
# ============================================================

@app.route(
    "/admin/programme/add",
    methods=["GET", "POST"]
)
@admin_required
def add_programme():

    conn = get_db()

    universities = conn.execute(
        """
        SELECT *
        FROM universities
        ORDER BY name
        """
    ).fetchall()

    if request.method == "POST":

        conn.execute(
            """
            INSERT INTO programmes
            (
                university_id,
                name,
                department,
                duration,
                requirements,
                careers,
                description
            )

            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request.form["university_id"],
                request.form["name"],
                request.form["department"],
                request.form["duration"],
                request.form["requirements"],
                request.form["careers"],
                request.form["description"]
            )
        )

        conn.commit()

        conn.close()

        flash(
            "Programme added successfully."
        )

        return redirect(
            url_for("admin_dashboard")
        )

    conn.close()

    return programme_form(
        universities=universities
    )


# ============================================================
# EDIT PROGRAMME
# ============================================================

@app.route(
    "/admin/programme/edit/<int:programme_id>",
    methods=["GET", "POST"]
)
@admin_required
def edit_programme(programme_id):

    conn = get_db()

    programme = conn.execute(
        """
        SELECT *
        FROM programmes
        WHERE id = ?
        """,
        (programme_id,)
    ).fetchone()

    universities = conn.execute(
        """
        SELECT *
        FROM universities
        ORDER BY name
        """
    ).fetchall()

    if not programme:

        conn.close()

        return "Programme not found", 404

    if request.method == "POST":

        conn.execute(
            """
            UPDATE programmes

            SET university_id = ?,
                name = ?,
                department = ?,
                duration = ?,
                requirements = ?,
                careers = ?,
                description = ?

            WHERE id = ?
            """,
            (
                request.form["university_id"],
                request.form["name"],
                request.form["department"],
                request.form["duration"],
                request.form["requirements"],
                request.form["careers"],
                request.form["description"],
                programme_id
            )
        )

        conn.commit()

        conn.close()

        flash(
            "Programme updated successfully."
        )

        return redirect(
            url_for("admin_dashboard")
        )

    conn.close()

    return programme_form(
        programme=programme,
        universities=universities
    )


# ============================================================
# DELETE PROGRAMME
# ============================================================

@app.route(
    "/admin/programme/delete/<int:programme_id>"
)
@admin_required
def delete_programme(programme_id):

    conn = get_db()

    conn.execute(
        """
        DELETE FROM programmes
        WHERE id = ?
        """,
        (programme_id,)
    )

    conn.commit()

    conn.close()

    flash(
        "Programme deleted."
    )

    return redirect(
        url_for("admin_dashboard")
    )


# ============================================================
# PROGRAMME FORM
# ============================================================

def programme_form(
    programme=None,
    universities=None
):

    editing = programme is not None

    html = """

<div class="form-card">

    <h1>

        {% if editing %}

            Edit Programme

        {% else %}

            Add Programme

        {% endif %}

    </h1>


    <form method="post">


        <div class="form-group">

            <label>
                University
            </label>


            <select
                name="university_id"
                required
            >

                {% for university in universities %}

                <option
                    value="{{ university['id'] }}"

                    {% if programme and
                    programme['university_id'] == university['id'] %}

                        selected

                    {% endif %}
                >

                    {{ university['name'] }}

                </option>

                {% endfor %}

            </select>

        </div>


        <div class="form-group">

            <label>
                Programme Name
            </label>


            <input
                type="text"
                name="name"
                value="{{ programme['name'] if programme else '' }}"
                required
            >

        </div>


        <div class="form-group">

            <label>
                Department
            </label>


            <input
                type="text"
                name="department"
                value="{{ programme['department'] if programme else '' }}"
            >

        </div>


        <div class="form-group">

            <label>
                Duration
            </label>


            <input
                type="text"
                name="duration"
                value="{{ programme['duration'] if programme else '4 years' }}"
            >

        </div>


        <div class="form-group">

            <label>
                Admission Requirements
            </label>


            <textarea
                name="requirements"
            >{{ programme['requirements'] if programme else '' }}</textarea>

        </div>


        <div class="form-group">

            <label>
                Future Career Opportunities
            </label>


            <textarea
                name="careers"
                placeholder="Example: Financial Data Scientist, Data Scientist, Financial Analyst, Risk Analyst..."
            >{{ programme['careers'] if programme else '' }}</textarea>

        </div>


        <div class="form-group">

            <label>
                Programme Description
            </label>


            <textarea
                name="description"
            >{{ programme['description'] if programme else '' }}</textarea>

        </div>


        <button class="btn btn-primary">

            {% if editing %}

                Update Programme

            {% else %}

                Add Programme

            {% endif %}

        </button>


        <a
            class="btn btn-secondary"
            href="/admin"
        >
            Cancel
        </a>

    </form>

</div>

"""

    return render_template_string(
        BASE,
        title="Programme Form",
        css=CSS,
        content=render_template_string(
            html,
            programme=programme,
            universities=universities,
            editing=editing
        )
    )


# ============================================================
# 404 ERROR
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    html = """

<div class="section container">

    <div class="card">

        <h1>
            404
        </h1>


        <h2>
            Page Not Found
        </h2>


        <p>
            The page you are looking for does not exist.
        </p>


        <a
            href="/"
            class="btn btn-primary"
        >
            Go Home
        </a>

    </div>

</div>

"""

    return render_template_string(
        BASE,
        title="Page Not Found",
        css=CSS,
        content=render_template_string(html)
    ), 404


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    init_db()

    print("")
    print("==============================================")
    print("              MC_UNIFINDER")
    print("==============================================")
    print("")
    print("Website:")
    print("http://127.0.0.1:5000")
    print("")
    print("Admin Dashboard:")
    print("http://127.0.0.1:5000/admin")
    print("")
    print("Admin username: Bekoewise99")
    print("Admin password: Bekoewise99@")
    print("")
    print("==============================================")

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )