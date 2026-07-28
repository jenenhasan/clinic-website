"""
Marsh Family Practice — Complete Clinic Management System
----------------------------------------------------------
A professional system with public website for patients and
private backend for doctors with full EHR capabilities.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, g, jsonify
from datetime import datetime, timedelta, timezone
import sqlite3
import os
import hashlib
import json
from functools import wraps
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# ===========================================================================
# CONFIGURATION - Load from environment variables (NO DEFAULTS!)
# ===========================================================================

# Secret key - MUST be set in .env
app.secret_key = os.environ.get("SECRET_KEY")
if app.secret_key is None:
    raise ValueError(
        "❌ SECRET_KEY environment variable is not set!\n"
        "Please create a .env file with SECRET_KEY=your-secret-key\n"
        "Generate one with: python -c 'import secrets; print(secrets.token_hex(32))'"
    )

# Flask configuration
app.config['DEBUG'] = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
app.config['ENV'] = os.environ.get("FLASK_ENV", "production")

# Admin password - MUST be set in .env
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
if ADMIN_PASSWORD is None:
    raise ValueError(
        "❌ ADMIN_PASSWORD environment variable is not set!\n"
        "Please create a .env file with ADMIN_PASSWORD=your-password"
    )

DB_PATH = os.path.join(os.path.dirname(__file__), "clinic.db")

# ===========================================================================
# CONFIGURATION - PROFESSIONAL CONTENT
# ===========================================================================
CONFIG = {
    "business_name": {
        "en": "Marsh Family Practice",
        "ar": "عيادة مارش العائلية"
    },
    "doctor_name": {
        "en": "Dr. Elena Marsh",
        "ar": "الدكتورة إلينا مارش"
    },
    "credentials": {
        "en": "MD, FAAFP | Family Medicine Specialist",
        "ar": "دكتوراه في الطب، زمالة الأكاديمية الأمريكية لأطباء الأسرة | أخصائية طب العائلة"
    },
    "tagline": {
        "en": "Exceptional Family Care, Right in Your Community",
        "ar": "رعاية عائلية استثنائية، في مجتمعك"
    },
    "about": {
        "en": "At Marsh Family Practice, we believe healthcare should be personal, accessible, and comprehensive. Our independent practice offers same-week appointments, thorough consultations, and genuine continuity of care—because you deserve a doctor who knows you, not just your chart.",
        "ar": "في عيادة مارش العائلية، نؤمن بأن الرعاية الصحية يجب أن تكون شخصية ومتاحة وشاملة. تقدم عيادتنا المستقلة مواعيد في نفس الأسبوع، واستشارات شاملة، واستمرارية حقيقية في الرعاية—لأنك تستحق طبيباً يعرفك، وليس فقط ملفك الطبي."
    },
    "bio": {
        "en": "Dr. Elena Marsh is a board-certified family medicine physician with over 12 years of clinical experience. She completed her medical training at the University of Cambridge and her residency in Family Medicine at St. Thomas' Hospital, London. Dr. Marsh is passionate about preventive medicine and building lasting relationships with her patients. She believes in empowering individuals and families to take an active role in their health through education, open communication, and evidence-based care.",
        "ar": "الدكتورة إلينا مارش هي طبيبة معتمدة في طب الأسرة مع أكثر من 12 عاماً من الخبرة السريرية. أكملت تدريبها الطبي في جامعة كامبريدج وإقامتها في طب الأسرة في مستشفى سانت توماس، لندن. الدكتورة مارش شغوفة بالطب الوقائي وبناء علاقات دائمة مع مرضاها. تؤمن بتمكين الأفراد والعائلات من القيام بدور نشط في صحتهم من خلال التثقيف والتواصل المفتوح والرعاية القائمة على الأدلة."
    },
    "philosophy_points": [
        {
            "title": {"en": "Patient-Centered Care", "ar": "رعاية تركز على المريض"},
            "text": {"en": "Every appointment is scheduled with adequate time to listen, understand, and address your concerns without rushing.", "ar": "يتم جدولة كل موعد بوقت كافٍ للاستماع والفهم ومعالجة مخاوفك دون استعجال."}
        },
        {
            "title": {"en": "Continuity of Care", "ar": "استمرارية الرعاية"},
            "text": {"en": "You see the same physician at every visit, ensuring your care is consistent, comprehensive, and personalized.", "ar": "ترى نفس الطبيب في كل زيارة، مما يضمن أن رعايتك متسقة وشاملة وشخصية."}
        },
        {
            "title": {"en": "Evidence-Based Medicine", "ar": "الطب القائم على الأدلة"},
            "text": {"en": "We provide clear, straightforward explanations of your health and treatment options based on the latest medical research.", "ar": "نقدم شرحاً واضحاً ومباشراً لصحتك وخيارات العلاج الخاصة بك استناداً إلى أحدث الأبحاث الطبية."}
        }
    ],
    "credentials_list": {
        "en": [
            "MD — University of Cambridge School of Medicine",
            "Board Certified — Family Medicine",
            "Fellow — American Academy of Family Physicians (FAAFP)",
            "12+ years of clinical experience",
            "Postgraduate training in Preventive & Primary Care"
        ],
        "ar": [
            "دكتوراه في الطب — كلية الطب بجامعة كامبريدج",
            "معتمدة في طب الأسرة",
            "زميلة — الأكاديمية الأمريكية لأطباء الأسرة (FAAFP)",
            "أكثر من 12 عاماً من الخبرة السريرية",
            "تدريب دراسات عليا في الرعاية الوقائية والأولية"
        ]
    },
    "address": {
        "en": "14 Marina Street, Kyrenia, Cyprus",
        "ar": "شارع مارينا 14، كيرينيا، قبرص"
    },
    "phone": "+90 548 861 6466",
    "email": "info@marshfamilypractice.com",
    "hours": {
        "en": "Monday–Friday, 9:00 AM – 5:00 PM",
        "ar": "الإثنين–الجمعة، 9:00 صباحاً – 5:00 مساءً"
    },
    "open_days": [0, 1, 2, 3, 4],
    "open_time": "09:00",
    "close_time": "17:00",
    "admin_password": ADMIN_PASSWORD,  # Now from environment only! No default!
    "services": [
        {
            "id": "general",
            "name": {
                "en": "General Consultation",
                "ar": "استشارة عامة"
            },
            "duration": {
                "en": "30 minutes",
                "ar": "٣٠ دقيقة"
            },
            "price": "€25",
            "description": {
                "en": "Comprehensive evaluation for new symptoms, ongoing health concerns, or any condition that requires a specialist referral. Includes thorough history taking, physical examination, and personalized treatment plan.",
                "ar": "تقييم شامل للأعراض الجديدة، المخاوف الصحية المستمرة، أو أي حالة تتطلب إحالة إلى أخصائي. يشمل أخذ تاريخ طبي شامل، فحص سريري، وخطة علاج شخصية."
            }
        },
        {
            "id": "followup",
            "name": {
                "en": "Follow-up Visit",
                "ar": "زيارة متابعة"
            },
            "duration": {
                "en": "20 minutes",
                "ar": "٢٠ دقيقة"
            },
            "price": "€15",
            "description": {
                "en": "Continued care and monitoring of chronic conditions, post-treatment follow-ups, or discussion of laboratory and diagnostic test results to ensure optimal health outcomes.",
                "ar": "رعاية مستمرة ومتابعة للحالات المزمنة، متابعات ما بعد العلاج، أو مناقشة نتائج الفحوصات المخبرية والتشخيصية لضمان أفضل النتائج الصحية."
            }
        },
        {
            "id": "wellness",
            "name": {
                "en": "Annual Wellness Checkup",
                "ar": "فحص الصحة السنوي"
            },
            "duration": {
                "en": "45 minutes",
                "ar": "٤٥ دقيقة"
            },
            "price": "€50",
            "description": {
                "en": "Comprehensive annual health assessment including vital signs monitoring, blood work referrals, preventive screenings, and a complete review of your overall health status and wellness goals.",
                "ar": "تقييم صحي سنوي شامل يشمل مراقبة العلامات الحيوية، إحالات لتحليل الدم، فحوصات وقائية، ومراجعة كاملة لحالتك الصحية العامة وأهدافك الصحية."
            }
        }
    ],
    "insurance_note": {
        "en": "We accept most major insurance plans. Please contact our office to verify your coverage. Self-pay options are available at the rates listed above.",
        "ar": "نقبل معظم خطط التأمين الرئيسية. يرجى الاتصال بمكتبنا للتحقق من تغطيتك. تتوفر خيارات الدفع الذاتي بالأسعار المذكورة أعلاه."
    },
    "testimonials": [
        {
            "quote": {
                "en": "Dr. Marsh took the time to truly listen to my concerns and explained everything in a way I could understand. I finally feel like I have a doctor who cares about my well-being.",
                "ar": "أخذت الدكتورة مارش الوقت للاستماع حقاً إلى مخاوفي وشرحت كل شيء بطريقة تمكنت من فهمها. أخيراً أشعر أن لدي طبيبة تهتم برفاهيتي."
            },
            "name": "Sarah J."
        },
        {
            "quote": {
                "en": "After years of rushed appointments and switching doctors, I found Dr. Marsh. She knows my history, follows up after every visit, and genuinely cares about my family's health.",
                "ar": "بعد سنوات من المواعيد السريعة وتغيير الأطباء، وجدت الدكتورة مارش. تعرف تاريخي الطبي، وتتابع بعد كل زيارة، وتهتم حقاً بصحة عائلتي."
            },
            "name": "Michael R."
        },
        {
            "quote": {
                "en": "The online booking system makes it so easy to schedule appointments. Dr. Marsh is thorough, kind, and always makes me feel heard. Highly recommend her practice.",
                "ar": "نظام الحجز عبر الإنترنت يجعل من السهل جداً جدولة المواعيد. الدكتورة مارش دقيقة ولطيفة وتجعلني دائماً أشعر بأنني مسموع. أوصي بشدة بعيادتها."
            },
            "name": "Anna K."
        }
    ],
    "faqs": [
        {
            "q": {
                "en": "Do I need a referral to book an appointment?",
                "ar": "هل أحتاج إلى تحويل لحجز موعد؟"
            },
            "a": {
                "en": "No referral is required. You can book directly with Dr. Marsh for any of our services. We welcome new patients and same-day appointments when available.",
                "ar": "لا حاجة إلى تحويل. يمكنك الحجز مباشرة مع الدكتورة مارش لأي من خدماتنا. نرحب بالمرضى الجدد والمواعيد في نفس اليوم عند توفرها."
            }
        },
        {
            "q": {
                "en": "What should I bring to my first appointment?",
                "ar": "ماذا يجب أن أحضر لموعدي الأول؟"
            },
            "a": {
                "en": "Please bring your identification, current list of medications, any recent test results, and your insurance card. Arrive 10 minutes early to complete registration paperwork.",
                "ar": "يرجى إحضار بطاقة الهوية الخاصة بك، قائمة الأدوية الحالية، أي نتائج فحوصات حديثة، وبطاقة التأمين الخاصة بك. احضر قبل 10 دقائق من موعدك لإكمال أوراق التسجيل."
            }
        },
        {
            "q": {
                "en": "What is your cancellation policy?",
                "ar": "ما هي سياسة الإلغاء الخاصة بكم؟"
            },
            "a": {
                "en": "We kindly request at least 24 hours notice for cancellations or rescheduling. This allows us to offer the appointment time to other patients in need of care.",
                "ar": "نطلب بلطف إشعاراً قبل 24 ساعة على الأقل للإلغاء أو إعادة الجدولة. هذا يسمح لنا بتقديم وقت الموعد لمرضى آخرين بحاجة إلى رعاية."
            }
        },
        {
            "q": {
                "en": "Do you accept walk-in patients?",
                "ar": "هل تقبلون المرضى بدون موعد؟"
            },
            "a": {
                "en": "We do our best to accommodate walk-in patients when schedule permits. However, we strongly recommend booking ahead to guarantee availability and minimize wait times.",
                "ar": "نبذل قصارى جهدنا لاستقبال المرضى بدون موعد عندما يتسع الجدول. ومع ذلك، نوصي بشدة بالحجز المسبق لضمان التوفر وتقليل أوقات الانتظار."
            }
        },
        {
            "q": {
                "en": "Do you offer telemedicine consultations?",
                "ar": "هل تقدمون استشارات عن بعد؟"
            },
            "a": {
                "en": "Yes, we offer secure video consultations for eligible patients. Please contact our office to determine if a telemedicine visit is appropriate for your condition.",
                "ar": "نعم، نقدم استشارات فيديو آمنة للمرضى المؤهلين. يرجى الاتصال بمكتبنا لتحديد ما إذا كانت زيارة التطبيب عن بعد مناسبة لحالتك."
            }
        }
    ]
}

TIME_SLOTS = ["09:00", "09:45", "10:30", "11:15", "13:00", "13:45", "14:30", "15:15", "16:00"]

# ===========================================================================
# DATABASE FUNCTIONS
# ===========================================================================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    
    # Users table (for doctors/staff)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'doctor',
            name TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    # Patients table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mr_number TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            name_ar TEXT,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,
            gender TEXT,
            address TEXT,
            emergency_contact_name TEXT,
            emergency_contact_phone TEXT,
            blood_type TEXT,
            allergies TEXT,
            chronic_conditions TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            status TEXT DEFAULT 'active'
        )
    """)
    
    # Appointments (bookings)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            service_type TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT DEFAULT 'scheduled',
            reason TEXT,
            notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    """)
    
    # Medical History
    conn.execute("""
        CREATE TABLE IF NOT EXISTS medical_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            visit_date TEXT NOT NULL,
            doctor_id INTEGER,
            chief_complaint TEXT,
            diagnosis TEXT,
            treatment_plan TEXT,
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    """)
    
    # Prescriptions
    conn.execute("""
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            medical_history_id INTEGER,
            medication_name TEXT NOT NULL,
            dosage TEXT NOT NULL,
            frequency TEXT NOT NULL,
            duration TEXT NOT NULL,
            instructions TEXT,
            prescribed_date TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (medical_history_id) REFERENCES medical_history(id)
        )
    """)
    
    # Lab Tests
    conn.execute("""
        CREATE TABLE IF NOT EXISTS lab_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            medical_history_id INTEGER,
            test_name TEXT NOT NULL,
            test_date TEXT NOT NULL,
            result TEXT,
            reference_range TEXT,
            interpretation TEXT,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (medical_history_id) REFERENCES medical_history(id)
        )
    """)
    
    # Contact messages
    conn.execute("""
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()
    
    # Create default admin account if not exists
    create_default_admin()

def create_default_admin():
    """Create default admin account if no users exist"""
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if count == 0:
        hashed = hashlib.sha256("admin123".encode()).hexdigest()
        conn.execute(
            "INSERT INTO users (username, password_hash, role, name, created_at) VALUES (?, ?, ?, ?, ?)",
            ("admin", hashed, "admin", "Administrator", datetime.now(timezone.utc).isoformat())
        )
        conn.commit()
        print("=" * 50)
        print("✅ Default admin created!")
        print("   Username: admin")
        print("   Password: admin123")
        print("=" * 50)
    conn.close()

# ===========================================================================
# AUTHENTICATION DECORATORS
# ===========================================================================
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.endpoint == 'admin_login':
            return f(*args, **kwargs)
        if not session.get('is_admin'):
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def patient_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.endpoint in ['patient_login', 'patient_register']:
            return f(*args, **kwargs)
        if not session.get('patient_id'):
            flash('Please log in to access your appointments.', 'error')
            return redirect(url_for('patient_login'))
        return f(*args, **kwargs)
    return decorated_function

# ===========================================================================
# LANGUAGE SUPPORT
# ===========================================================================
@app.before_request
def before_request():
    g.lang = session.get('lang', 'en')
    g.is_rtl = g.lang == 'ar'

@app.context_processor
def inject_lang():
    return {
        'lang': g.lang,
        'is_rtl': g.is_rtl,
        'get_text': get_text,
        'get_config': get_config,
        'CONFIG': CONFIG,
        'TIME_SLOTS': TIME_SLOTS,
        'datetime': datetime,
        'timedelta': timedelta,
        'session': session
    }

def get_text(text_dict):
    if isinstance(text_dict, dict):
        return text_dict.get(g.lang, text_dict.get('en', str(text_dict)))
    return text_dict

def get_config(key):
    value = CONFIG.get(key)
    if isinstance(value, dict):
        return value.get(g.lang, value.get('en', value))
    return value

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_mr_number():
    """Generate unique medical record number"""
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
    conn.close()
    year = datetime.now().strftime("%Y")
    return f"MR{year}{str(count + 1).zfill(5)}"

def clinic_status():
    """Check if clinic is open"""
    now = datetime.now()
    open_t = datetime.strptime(CONFIG["open_time"], "%H:%M").time()
    close_t = datetime.strptime(CONFIG["close_time"], "%H:%M").time()
    is_open = now.weekday() in CONFIG["open_days"] and open_t <= now.time() <= close_t
    
    today_str = now.strftime("%Y-%m-%d")
    booked_today = booked_times_for_date(today_str)
    remaining_today = [t for t in TIME_SLOTS if t not in booked_today and datetime.strptime(t, "%H:%M").time() > now.time()]
    
    return {
        "is_open": is_open,
        "slots_left_today": len(remaining_today) if now.weekday() in CONFIG["open_days"] else 0,
    }

def booked_times_for_date(date_str):
    conn = get_db()
    rows = conn.execute("SELECT time FROM appointments WHERE date = ? AND status != 'cancelled'", (date_str,)).fetchall()
    conn.close()
    return {row["time"] for row in rows}

def next_available_dates(n=10):
    dates = []
    d = datetime.today()
    while len(dates) < n:
        d += timedelta(days=1)
        if d.weekday() < 5:
            dates.append((d.strftime("%Y-%m-%d"), d.strftime("%a, %b %d")))
    return dates

# ===========================================================================
# LANGUAGE SWITCH
# ===========================================================================
@app.route('/switch-language/<lang>')
def switch_language(lang):
    if lang in ['en', 'ar']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))

# ===========================================================================
# PUBLIC ROUTES (No Login Required)
# ===========================================================================
@app.route("/")
def index():
    return render_template("index.html", status=clinic_status())

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        message = request.form.get("message", "").strip()
        
        if not name or not email or not message:
            flash("All fields are required.", "error")
            return render_template("contact.html", form=request.form)
        
        conn = get_db()
        conn.execute(
            "INSERT INTO contact_messages (name, email, phone, message, created_at) VALUES (?, ?, ?, ?, ?)",
            (name, email, phone, message, datetime.now(timezone.utc).isoformat())
        )
        conn.commit()
        conn.close()
        flash("Your message has been sent. We will respond within 24 hours.", "success")
        return redirect(url_for("contact"))
    
    return render_template("contact.html", form={})

# ===========================================================================
# BOOKING ROUTES (Public - No Login Required)
# ===========================================================================
@app.route("/book", methods=["GET", "POST"])
def book():
    dates = next_available_dates()
    
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        service_id = request.form.get("service_id", "")
        date = request.form.get("date", "")
        time = request.form.get("time", "")
        notes = request.form.get("notes", "").strip()
        
        errors = []
        if not name:
            errors.append("Please enter your full name.")
        if not phone:
            errors.append("Please enter a valid phone number.")
        if not service_id:
            errors.append("Please select a service.")
        if not date or not time:
            errors.append("Please select a date and time.")
        elif time in booked_times_for_date(date):
            errors.append("This time slot is already booked. Please choose another time.")
        
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("book.html", 
                dates=dates, time_slots=TIME_SLOTS,
                selected_date=date, selected_service=service_id,
                booked_times=booked_times_for_date(date) if date else set(),
                form=request.form, status=clinic_status())
        
        # Check if patient exists, create if not
        conn = get_db()
        patient = conn.execute("SELECT id FROM patients WHERE email = ?", (email,)).fetchone()
        
        if not patient:
            # Create a simple patient record
            mr_number = generate_mr_number()
            conn.execute(
                """INSERT INTO patients 
                   (mr_number, name, email, phone, password_hash, date_of_birth, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (mr_number, name, email, phone, hash_password("temp123"), 
                 datetime.now().strftime("%Y-%m-%d"),
                 datetime.now(timezone.utc).isoformat(), 
                 datetime.now(timezone.utc).isoformat())
            )
            patient_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        else:
            patient_id = patient["id"]
        
        # Create appointment
        conn.execute(
            "INSERT INTO appointments (patient_id, service_type, date, time, notes, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (patient_id, service_id, date, time, notes, 
             datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat())
        )
        conn.commit()
        conn.close()
        
        service_name = next(s["name"] for s in CONFIG["services"] if s["id"] == service_id)
        date_label = next(label for iso, label in dates if iso == date)
        
        return render_template("confirmation.html",
            name=name, service_name=service_name, date_label=date_label, time=time)
    
    # GET
    selected_date = request.args.get("date", dates[0][0] if dates else "")
    return render_template("book.html",
        dates=dates, time_slots=TIME_SLOTS,
        selected_date=selected_date, selected_service=request.args.get("service", ""),
        booked_times=booked_times_for_date(selected_date) if selected_date else set(),
        form={}, status=clinic_status())

@app.route("/booked-times")
def booked_times():
    date = request.args.get("date", "")
    return {"booked": sorted(booked_times_for_date(date))}

@app.route("/clinic-status")
def clinic_status_json():
    return clinic_status()

# ===========================================================================
# PATIENT PORTAL ROUTES
# ===========================================================================
@app.route("/patient/register", methods=["GET", "POST"])
def patient_register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        name_ar = request.form.get("name_ar", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        date_of_birth = request.form.get("date_of_birth", "")
        gender = request.form.get("gender", "")
        
        errors = []
        if not name:
            errors.append("Full name is required.")
        if not email:
            errors.append("Email address is required.")
        if not phone:
            errors.append("Phone number is required.")
        if not password:
            errors.append("Password is required.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("patient_register.html", form=request.form)
        
        hashed_pw = hash_password(password)
        mr_number = generate_mr_number()
        
        conn = get_db()
        try:
            conn.execute(
                """INSERT INTO patients 
                   (mr_number, name, name_ar, email, phone, password_hash, 
                    date_of_birth, gender, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (mr_number, name, name_ar, email, phone, hashed_pw,
                 date_of_birth, gender, datetime.now(timezone.utc).isoformat(),
                 datetime.now(timezone.utc).isoformat())
            )
            conn.commit()
            patient_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            conn.close()
            
            # Auto-login after registration
            session["patient_id"] = patient_id
            session["patient_name"] = name
            session["patient_email"] = email
            
            flash(f"Welcome {name}! Your account has been created successfully.", "success")
            return redirect(url_for("patient_dashboard"))
        except sqlite3.IntegrityError:
            flash("This email is already registered. Please login or use a different email.", "error")
            conn.close()
    
    return render_template("patient_register.html", form={})

@app.route("/patient/login", methods=["GET", "POST"])
def patient_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        
        conn = get_db()
        patient = conn.execute(
            "SELECT * FROM patients WHERE email = ?", (email,)
        ).fetchone()
        conn.close()
        
        if patient and patient["password_hash"] == hash_password(password):
            session["patient_id"] = patient["id"]
            session["patient_name"] = patient["name"]
            session["patient_email"] = patient["email"]
            flash("Welcome back! You are now logged in.", "success")
            return redirect(url_for("patient_dashboard"))
        else:
            flash("Invalid email or password. Please try again.", "error")
    
    return render_template("patient_login.html")

@app.route("/patient/logout")
def patient_logout():
    session.pop("patient_id", None)
    session.pop("patient_name", None)
    session.pop("patient_email", None)
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("index"))

@app.route("/patient/dashboard")
@patient_login_required
def patient_dashboard():
    conn = get_db()
    appointments = conn.execute(
        "SELECT * FROM appointments WHERE patient_id = ? ORDER BY date DESC, time DESC",
        (session.get("patient_id"),)
    ).fetchall()
    conn.close()
    return render_template("patient_dashboard.html", appointments=appointments)

@app.route("/patient/book", methods=["GET", "POST"])
@patient_login_required
def patient_book():
    dates = next_available_dates()
    
    if request.method == "POST":
        service_id = request.form.get("service_id", "")
        date = request.form.get("date", "")
        time = request.form.get("time", "")
        notes = request.form.get("notes", "").strip()
        
        errors = []
        if not service_id:
            errors.append("Please select a service.")
        if not date or not time:
            errors.append("Please select a date and time.")
        elif time in booked_times_for_date(date):
            errors.append("This time slot is already booked. Please choose another time.")
        
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("patient_book.html", dates=dates, form=request.form)
        
        conn = get_db()
        conn.execute(
            """INSERT INTO appointments
               (patient_id, service_type, date, time, notes, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (session.get("patient_id"), service_id, date, time, notes,
             datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat())
        )
        conn.commit()
        conn.close()
        
        flash("Your appointment has been booked successfully!", "success")
        return redirect(url_for("patient_dashboard"))
    
    return render_template("patient_book.html", dates=dates)

@app.route("/patient/cancel/<int:appointment_id>", methods=["POST"])
@patient_login_required
def patient_cancel_appointment(appointment_id):
    conn = get_db()
    appointment = conn.execute(
        "SELECT * FROM appointments WHERE id = ? AND patient_id = ?",
        (appointment_id, session.get("patient_id"))
    ).fetchone()
    
    if appointment:
        conn.execute(
            "UPDATE appointments SET status = 'cancelled' WHERE id = ?",
            (appointment_id,)
        )
        conn.commit()
        flash("Your appointment has been cancelled.", "success")
    else:
        flash("Appointment not found.", "error")
    
    conn.close()
    return redirect(url_for("patient_dashboard"))

# ===========================================================================
# ADMIN ROUTES (Login Required)
# ===========================================================================
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if session.get('is_admin'):
        return redirect(url_for("admin_dashboard"))
    
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == CONFIG["admin_password"]:
            session["is_admin"] = True
            session["user_id"] = 1
            session["role"] = "admin"
            session["user_name"] = "Administrator"
            flash("Login successful!", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid password. Please try again.", "error")
            return redirect(url_for("admin_login"))
    
    return render_template("admin_login.html")

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    conn = get_db()
    today = datetime.now().strftime("%Y-%m-%d")
    
    today_appointments = conn.execute(
        """SELECT a.*, p.name as patient_name, p.mr_number, p.phone
           FROM appointments a
           JOIN patients p ON a.patient_id = p.id
           WHERE a.date = ? AND a.status != 'cancelled'
           ORDER BY a.time ASC""",
        (today,)
    ).fetchall()
    
    total_patients = conn.execute("SELECT COUNT(*) FROM patients WHERE status = 'active'").fetchone()[0]
    total_appointments = conn.execute("SELECT COUNT(*) FROM appointments WHERE status != 'cancelled'").fetchone()[0]
    total_prescriptions = conn.execute("SELECT COUNT(*) FROM prescriptions WHERE status = 'active'").fetchone()[0]
    pending_labs = conn.execute("SELECT COUNT(*) FROM lab_tests WHERE status = 'pending'").fetchone()[0]
    pending_messages = conn.execute("SELECT COUNT(*) FROM contact_messages").fetchone()[0]
    
    messages = conn.execute("SELECT * FROM contact_messages ORDER BY created_at DESC LIMIT 10").fetchall()
    
    conn.close()
    
    return render_template("admin_dashboard.html",
        today_appointments=today_appointments,
        total_patients=total_patients,
        total_appointments=total_appointments,
        total_prescriptions=total_prescriptions,
        pending_labs=pending_labs,
        pending_messages=pending_messages,
        messages=messages,
        today=today
    )

@app.route("/admin/patients")
@admin_required
def admin_patients():
    search = request.args.get("search", "")
    conn = get_db()
    
    if search:
        patients = conn.execute(
            "SELECT * FROM patients WHERE name LIKE ? OR email LIKE ? OR phone LIKE ? OR mr_number LIKE ? ORDER BY created_at DESC",
            (f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%")
        ).fetchall()
    else:
        patients = conn.execute("SELECT * FROM patients ORDER BY created_at DESC").fetchall()
    
    conn.close()
    return render_template("admin_patients.html", patients=patients, search=search)

@app.route("/admin/patient/<int:patient_id>")
@admin_required
def admin_patient_detail(patient_id):
    conn = get_db()
    patient = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    
    if not patient:
        flash("Patient not found.", "error")
        return redirect(url_for("admin_patients"))
    
    medical_history = conn.execute(
        "SELECT * FROM medical_history WHERE patient_id = ? ORDER BY visit_date DESC",
        (patient_id,)
    ).fetchall()
    
    prescriptions = conn.execute(
        "SELECT * FROM prescriptions WHERE patient_id = ? AND status = 'active' ORDER BY prescribed_date DESC",
        (patient_id,)
    ).fetchall()
    
    appointments = conn.execute(
        "SELECT * FROM appointments WHERE patient_id = ? ORDER BY date DESC, time DESC",
        (patient_id,)
    ).fetchall()
    
    lab_tests = conn.execute(
        "SELECT * FROM lab_tests WHERE patient_id = ? ORDER BY test_date DESC",
        (patient_id,)
    ).fetchall()
    
    conn.close()
    
    return render_template("admin_patient_detail.html",
        patient=patient,
        medical_history=medical_history,
        prescriptions=prescriptions,
        appointments=appointments,
        lab_tests=lab_tests
    )

@app.route("/admin/patient/<int:patient_id>/add_visit", methods=["POST"])
@admin_required
def admin_add_visit(patient_id):
    visit_date = request.form.get("visit_date", datetime.now().strftime("%Y-%m-%d"))
    chief_complaint = request.form.get("chief_complaint", "").strip()
    diagnosis = request.form.get("diagnosis", "").strip()
    treatment_plan = request.form.get("treatment_plan", "").strip()
    notes = request.form.get("notes", "").strip()
    
    conn = get_db()
    conn.execute(
        """INSERT INTO medical_history
           (patient_id, visit_date, doctor_id, chief_complaint, diagnosis,
            treatment_plan, notes, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (patient_id, visit_date, session.get("user_id"),
         chief_complaint, diagnosis, treatment_plan, notes,
         datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    conn.close()
    
    flash("Medical visit recorded successfully.", "success")
    return redirect(url_for("admin_patient_detail", patient_id=patient_id))

@app.route("/admin/patient/<int:patient_id>/add_prescription", methods=["POST"])
@admin_required
def admin_add_prescription(patient_id):
    medication_name = request.form.get("medication_name", "").strip()
    dosage = request.form.get("dosage", "").strip()
    frequency = request.form.get("frequency", "").strip()
    duration = request.form.get("duration", "").strip()
    medical_history_id = request.form.get("medical_history_id")
    
    if not medication_name or not dosage:
        flash("Medication name and dosage are required.", "error")
        return redirect(request.referrer)
    
    conn = get_db()
    conn.execute(
        """INSERT INTO prescriptions
           (patient_id, medical_history_id, medication_name, dosage, frequency, duration,
            prescribed_date, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (patient_id, medical_history_id or None, medication_name, dosage,
         frequency, duration, datetime.now(timezone.utc).isoformat(), "active")
    )
    conn.commit()
    conn.close()
    
    flash("Prescription added successfully.", "success")
    return redirect(request.referrer)

@app.route("/admin/patient/<int:patient_id>/add_lab_test", methods=["POST"])
@admin_required
def admin_add_lab_test(patient_id):
    test_name = request.form.get("test_name", "").strip()
    test_date = request.form.get("test_date", datetime.now().strftime("%Y-%m-%d"))
    medical_history_id = request.form.get("medical_history_id")
    
    if not test_name:
        flash("Test name is required.", "error")
        return redirect(request.referrer)
    
    conn = get_db()
    conn.execute(
        """INSERT INTO lab_tests
           (patient_id, medical_history_id, test_name, test_date, status)
           VALUES (?, ?, ?, ?, ?)""",
        (patient_id, medical_history_id or None, test_name, test_date, "pending")
    )
    conn.commit()
    conn.close()
    
    flash("Lab test added successfully.", "success")
    return redirect(request.referrer)

@app.route("/admin/prescriptions")
@admin_required
def admin_prescriptions():
    conn = get_db()
    prescriptions = conn.execute(
        """SELECT p.*, pt.name as patient_name, pt.mr_number
           FROM prescriptions p
           JOIN patients pt ON p.patient_id = pt.id
           ORDER BY p.prescribed_date DESC
           LIMIT 100"""
    ).fetchall()
    conn.close()
    return render_template("admin_prescriptions.html", prescriptions=prescriptions)

@app.route("/admin/lab-tests")
@admin_required
def admin_lab_tests():
    conn = get_db()
    lab_tests = conn.execute(
        """SELECT l.*, pt.name as patient_name, pt.mr_number
           FROM lab_tests l
           JOIN patients pt ON l.patient_id = pt.id
           ORDER BY l.test_date DESC
           LIMIT 100"""
    ).fetchall()
    conn.close()
    return render_template("admin_lab_tests.html", lab_tests=lab_tests)

@app.route("/admin/lab-test/<int:test_id>/update", methods=["POST"])
@admin_required
def admin_update_lab_test(test_id):
    result = request.form.get("result", "").strip()
    interpretation = request.form.get("interpretation", "").strip()
    status = request.form.get("status", "completed")
    
    conn = get_db()
    conn.execute(
        "UPDATE lab_tests SET result = ?, interpretation = ?, status = ? WHERE id = ?",
        (result, interpretation, status, test_id)
    )
    conn.commit()
    conn.close()
    flash("Lab test updated.", "success")
    return redirect(request.referrer)

@app.route("/admin/appointments")
@admin_required
def admin_appointments():
    date_str = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    conn = get_db()
    appointments = conn.execute(
        """SELECT a.*, p.name as patient_name, p.mr_number, p.phone
           FROM appointments a
           JOIN patients p ON a.patient_id = p.id
           WHERE a.date = ?
           ORDER BY a.time ASC""",
        (date_str,)
    ).fetchall()
    conn.close()
    
    return render_template("admin_appointments.html", 
        appointments=appointments, 
        date=date_str
    )

@app.route("/admin/upcoming")
@admin_required
def admin_upcoming():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_db()
    appointments = conn.execute(
        """SELECT a.*, p.name as patient_name, p.mr_number, p.phone
           FROM appointments a
           JOIN patients p ON a.patient_id = p.id
           WHERE a.date >= ? AND a.status != 'cancelled'
           ORDER BY a.date ASC, a.time ASC
           LIMIT 50""",
        (today,)
    ).fetchall()
    conn.close()
    return render_template("admin_upcoming.html", appointments=appointments)

@app.route("/admin/appointment/<int:appointment_id>/status", methods=["POST"])
@admin_required
def admin_update_appointment_status(appointment_id):
    status = request.form.get("status", "scheduled")
    conn = get_db()
    conn.execute(
        "UPDATE appointments SET status = ?, updated_at = ? WHERE id = ?",
        (status, datetime.now(timezone.utc).isoformat(), appointment_id)
    )
    conn.commit()
    conn.close()
    flash("Appointment status updated.", "success")
    return redirect(request.referrer)

@app.route("/admin/analytics")
@admin_required
def admin_analytics():
    conn = get_db()
    
    monthly = conn.execute("""
        SELECT strftime('%Y-%m', date) as month, COUNT(*) as count
        FROM appointments
        WHERE date >= date('now', '-6 months') AND status != 'cancelled'
        GROUP BY month
        ORDER BY month DESC
    """).fetchall()
    
    gender_stats = conn.execute("""
        SELECT gender, COUNT(*) as count
        FROM patients
        GROUP BY gender
    """).fetchall()
    
    diagnoses = conn.execute("""
        SELECT diagnosis, COUNT(*) as count
        FROM medical_history
        WHERE diagnosis != ''
        GROUP BY diagnosis
        ORDER BY count DESC
        LIMIT 10
    """).fetchall()
    
    prescription_trends = conn.execute("""
        SELECT medication_name, COUNT(*) as count
        FROM prescriptions
        GROUP BY medication_name
        ORDER BY count DESC
        LIMIT 10
    """).fetchall()
    
    lab_trends = conn.execute("""
        SELECT test_name, COUNT(*) as count
        FROM lab_tests
        GROUP BY test_name
        ORDER BY count DESC
        LIMIT 10
    """).fetchall()
    
    conn.close()
    
    return render_template("admin_analytics.html",
        monthly=monthly,
        gender_stats=gender_stats,
        diagnoses=diagnoses,
        prescription_trends=prescription_trends,
        lab_trends=lab_trends
    )

@app.route("/admin/messages")
@admin_required
def admin_messages():
    conn = get_db()
    messages = conn.execute("SELECT * FROM contact_messages ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template("admin_messages.html", messages=messages)

@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    session.pop("user_id", None)
    session.pop("role", None)
    session.pop("user_name", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))

# ===========================================================================
# ERROR HANDLERS
# ===========================================================================
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

# ===========================================================================
# HEALTH CHECK ENDPOINT
# ===========================================================================
@app.route("/health")
def health_check():
    return {"status": "healthy", "env": app.config['ENV']}

# ===========================================================================
# DEBUG ROUTE (Remove in Production)
# ===========================================================================
@app.route("/debug-session")
def debug_session():
    if app.config['DEBUG']:
        return {
            "session": dict(session),
            "is_admin": session.get('is_admin'),
            "user_id": session.get('user_id'),
            "role": session.get('role'),
            "patient_id": session.get('patient_id')
        }
    return {"error": "Not available in production"}, 404

# ===========================================================================
# MAIN
# ===========================================================================
if __name__ == "__main__":
    init_db()
    app.run(
        debug=app.config['DEBUG'],
        host="0.0.0.0" if app.config['ENV'] == "production" else "127.0.0.1",
        port=int(os.environ.get("PORT", 3000))
    )
else:
    init_db()