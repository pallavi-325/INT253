"""
seed_data.py — Realistic demo data for Pediatric Teledermatology (CareNest)
Run: python manage.py seed_data
"""

import random
from datetime import date, timedelta, time
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


# ─── Realistic Doctor Data ─────────────────────────────────────────────────────
DOCTORS = [
    {
        "first_name": "Priya", "last_name": "Sharma",
        "email": "dr.priya.sharma@carenest.health",
        "username": "dr_priya_sharma",
        "license_number": "MCI-DEL-2009-04821",
        "specialization": "Atopic Dermatitis & Infantile Eczema",
        "experience_years": 15,
        "consultation_fee": "800.00",
        "bio": "Dr. Priya Sharma is a senior pediatric dermatologist with 15 years of experience at AIIMS New Delhi. "
               "She specializes in atopic dermatitis, infantile eczema, and urticaria in children under 5. "
               "She has published over 30 peer-reviewed papers on childhood allergic skin conditions and leads "
               "weekly teledermatology clinics for underserved rural communities.",
        "is_verified": True,
        "phone_number": "+91-98110-45231",
    },
    {
        "first_name": "Arjun", "last_name": "Mehta",
        "email": "dr.arjun.mehta@carenest.health",
        "username": "dr_arjun_mehta",
        "license_number": "MMC-MUM-2012-07634",
        "specialization": "Paediatric Psoriasis & Autoimmune Skin Disorders",
        "experience_years": 12,
        "consultation_fee": "950.00",
        "bio": "Dr. Arjun Mehta completed his MD Dermatology from KEM Hospital, Mumbai and a fellowship in "
               "Paediatric Immunodermatology from Great Ormond Street Hospital, London. He is a leading expert "
               "in childhood psoriasis, alopecia areata, and rare autoimmune blistering disorders.",
        "is_verified": True,
        "phone_number": "+91-98204-77832",
    },
    {
        "first_name": "Sunita", "last_name": "Nair",
        "email": "dr.sunita.nair@carenest.health",
        "username": "dr_sunita_nair",
        "license_number": "KMC-BLR-2014-02198",
        "specialization": "Neonatal & Infantile Skin Conditions",
        "experience_years": 10,
        "consultation_fee": "700.00",
        "bio": "Dr. Sunita Nair specializes in neonatal dermatology — including neonatal lupus, toxic erythema "
               "neonatorum, seborrhoeic dermatitis, and miliaria. She completed her training at Bangalore "
               "Medical College and has a special interest in safe topical therapy for newborns and premature infants.",
        "is_verified": True,
        "phone_number": "+91-80-4023-7891",
    },
    {
        "first_name": "Rahul", "last_name": "Verma",
        "email": "dr.rahul.verma@carenest.health",
        "username": "dr_rahul_verma",
        "license_number": "DMC-DEL-2016-09301",
        "specialization": "Fungal & Viral Paediatric Skin Infections",
        "experience_years": 8,
        "consultation_fee": "650.00",
        "bio": "Dr. Rahul Verma focuses on infectious dermatology in children: tinea capitis, molluscum "
               "contagiosum, impetigo, and herpes simplex infections. He runs a weekly outreach clinic "
               "at a government school and strongly advocates for early teledermatology triage.",
        "is_verified": False,
        "phone_number": "+91-11-4598-2201",
    },
    {
        "first_name": "Kavitha", "last_name": "Reddy",
        "email": "dr.kavitha.reddy@carenest.health",
        "username": "dr_kavitha_reddy",
        "license_number": "TSMC-HYD-2011-03567",
        "specialization": "Acne, Pigmentation & Adolescent Dermatology",
        "experience_years": 13,
        "consultation_fee": "850.00",
        "bio": "Dr. Kavitha Reddy is an expert in adolescent dermatology, particularly managing severe acne, "
               "post-inflammatory hyperpigmentation, and melasma in teens. She trained at Osmania Medical "
               "College and maintains a high-volume teledermatology practice serving over 500 patients monthly.",
        "is_verified": True,
        "phone_number": "+91-40-6789-4320",
    },
]

# ─── Realistic Parent & Children Data ─────────────────────────────────────────
FAMILIES = [
    {
        "parent": {
            "first_name": "Meena", "last_name": "Kapoor",
            "email": "meena.kapoor@gmail.com",
            "username": "meena_kapoor",
            "phone_number": "+91-98765-43210",
            "emergency_contact": "+91-98765-11000",
            "preferred_language": "Hindi",
        },
        "children": [
            {
                "first_name": "Aryan", "last_name": "Kapoor",
                "dob": date(2019, 3, 14),
                "gender": "MALE", "blood_group": "B+",
                "known_allergies": "Penicillin, Peanuts",
                "previous_skin_conditions": "Infantile eczema (resolved at 18 months), Viral rash (roseola at 11 months)",
                "current_medications": "Cetaphil moisturizing cream (daily), Vitamin D3 drops",
                "medical_history_notes": "Premature birth at 36 weeks. No asthma. Mild food allergies noted at 6 months.",
            },
            {
                "first_name": "Riya", "last_name": "Kapoor",
                "dob": date(2021, 8, 22),
                "gender": "FEMALE", "blood_group": "B+",
                "known_allergies": "Latex",
                "previous_skin_conditions": "Seborrhoeic dermatitis (cradle cap) at 2 months – resolved",
                "current_medications": "None",
                "medical_history_notes": "Healthy birth, full term. No significant medical history.",
            },
        ]
    },
    {
        "parent": {
            "first_name": "Rohit", "last_name": "Singh",
            "email": "rohit.singh.family@outlook.com",
            "username": "rohit_singh",
            "phone_number": "+91-97654-32109",
            "emergency_contact": "+91-97654-00001",
            "preferred_language": "English",
        },
        "children": [
            {
                "first_name": "Kabir", "last_name": "Singh",
                "dob": date(2017, 11, 5),
                "gender": "MALE", "blood_group": "O+",
                "known_allergies": "Sulfonamides, Nickel",
                "previous_skin_conditions": "Molluscum contagiosum (resolved with treatment 2022), Tinea capitis (2021)",
                "current_medications": "No current medications",
                "medical_history_notes": "Previously treated for recurrent fungal scalp infections. Immunocompetent. No asthma or atopy.",
            }
        ]
    },
    {
        "parent": {
            "first_name": "Anjali", "last_name": "Patel",
            "email": "anjali.patel87@yahoo.co.in",
            "username": "anjali_patel",
            "phone_number": "+91-96543-21098",
            "emergency_contact": "+91-96543-00500",
            "preferred_language": "Gujarati",
        },
        "children": [
            {
                "first_name": "Dhruv", "last_name": "Patel",
                "dob": date(2020, 6, 1),
                "gender": "MALE", "blood_group": "A+",
                "known_allergies": "Aspirin, Dust mites",
                "previous_skin_conditions": "Atopic dermatitis (ongoing, mild-moderate), Urticaria episode (2022)",
                "current_medications": "Tacrolimus 0.03% ointment (face), CeraVe Baby lotion twice daily",
                "medical_history_notes": "Known atopic triad: eczema, mild allergic rhinitis, mild asthma. Allergy-tested 2023.",
            },
            {
                "first_name": "Pooja", "last_name": "Patel",
                "dob": date(2023, 1, 15),
                "gender": "FEMALE", "blood_group": "A+",
                "known_allergies": "",
                "previous_skin_conditions": "Milia at birth (resolved)",
                "current_medications": "None",
                "medical_history_notes": "Infant, 10 months old. Exclusively breastfed until 6 months. All vaccinations current.",
            },
        ]
    },
    {
        "parent": {
            "first_name": "Suresh", "last_name": "Iyer",
            "email": "suresh.iyer@hotmail.com",
            "username": "suresh_iyer",
            "phone_number": "+91-94321-09876",
            "emergency_contact": "+91-94321-55555",
            "preferred_language": "Tamil",
        },
        "children": [
            {
                "first_name": "Preethi", "last_name": "Iyer",
                "dob": date(2015, 4, 20),
                "gender": "FEMALE", "blood_group": "AB+",
                "known_allergies": "Topical steroids (contact dermatitis to Betamethasone)",
                "previous_skin_conditions": "Psoriasis (plaque type, diagnosed 2022), Pityriasis rosea (2021)",
                "current_medications": "Coal tar shampoo (twice weekly), Calcipotriol ointment 0.005% (scalp)",
                "medical_history_notes": "Strong family history of psoriasis (maternal grandfather, paternal aunt). "
                                          "Currently managed with topical therapy. Under review for PUVA if no improvement.",
            },
        ]
    },
    {
        "parent": {
            "first_name": "Fatima", "last_name": "Khan",
            "email": "fatima.khan.mom@gmail.com",
            "username": "fatima_khan",
            "phone_number": "+91-91234-56789",
            "emergency_contact": "+91-91234-00099",
            "preferred_language": "Urdu",
        },
        "children": [
            {
                "first_name": "Zara", "last_name": "Khan",
                "dob": date(2018, 9, 12),
                "gender": "FEMALE", "blood_group": "O-",
                "known_allergies": "Fragrances (perfumed soaps), Wool",
                "previous_skin_conditions": "Atopic dermatitis (chronic, moderate), Hand eczema (2023)",
                "current_medications": "Hydrocortisone 1% cream (flares), Vaseline Intensive Care (daily)",
                "medical_history_notes": "Chronic atopic dermatitis since 6 months. Multiple food challenges done. "
                                          "Avoids scented products. Last flare was August 2024.",
            },
            {
                "first_name": "Ayaan", "last_name": "Khan",
                "dob": date(2022, 5, 30),
                "gender": "MALE", "blood_group": "A-",
                "known_allergies": "No known allergies",
                "previous_skin_conditions": "Neonatal acne (self-resolving, first month)",
                "current_medications": "None",
                "medical_history_notes": "Healthy toddler. No significant skin history. Up to date on vaccinations.",
            },
        ]
    },
]

# ─── Appointment scenarios ─────────────────────────────────────────────────────
APPOINTMENT_SCENARIOS = [
    {
        "chief_complaint": "Spreading red, scaly patches on both elbows and knees for 3 weeks. "
                           "Child scratches at night. No fever. Parents suspect eczema.",
        "severity": "MODERATE",
        "assessment": "Clinical presentation is consistent with moderate plaque psoriasis involving extensor surfaces. "
                      "Lesions are well-demarcated, erythematous plaques with silvery scale — Auspitz sign not tested remotely. "
                      "No signs of guttate spread or nail changes visible in submitted images. "
                      "Differential includes seborrhoeic dermatitis and nummular eczema.",
        "differential": "Nummular eczema, Seborrhoeic dermatitis, Pityriasis lichenoides chronica",
        "medications": "1. Calcipotriol 0.005% ointment — apply thin layer to plaques twice daily for 6 weeks.\n"
                       "2. Betamethasone valerate 0.05% cream — apply once daily for 2 weeks only on thick plaques, then taper.\n"
                       "3. Coconut oil — apply to entire body 30 mins before bathing to reduce scale.",
        "care_instructions": "• Bathe child daily in lukewarm water (not hot) for 10-15 minutes only.\n"
                              "• Pat dry gently — never rub. Apply moisturiser within 3 minutes of bath.\n"
                              "• Use fragrance-free soap (Dove Sensitive or Cetaphil Bar).\n"
                              "• Dress child in 100% cotton. Avoid synthetic and woollen fabrics.\n"
                              "• Keep nails short to minimise scratch damage.",
        "warning_signs": "Seek immediate in-person evaluation if: child develops fever above 101°F with worsening rash, "
                         "pustular lesions appear, rash rapidly spreads to >30% body surface, or any joint swelling.",
        "follow_up": True,
        "follow_up_days": 42,
        "follow_up_instructions": "Return consultation in 6 weeks to assess response to topical calcipotriol. "
                                   "Please upload new photographs of affected areas at that time.",
    },
    {
        "chief_complaint": "Multiple small flesh-coloured bumps on chest and armpits for 2 months. "
                           "No pain, mild itching. School nurse suspects contagion.",
        "severity": "MILD",
        "assessment": "High clinical suspicion for Molluscum Contagiosum based on the characteristic pearly, "
                      "dome-shaped papules with central umbilication visible in submitted images. "
                      "Approximately 15-20 lesions distributed on the anterior trunk and axillae. "
                      "No signs of secondary bacterial superinfection. Child is immunocompetent per history.",
        "differential": "Warts (verruca plana), Milia, Folliculitis, Closed comedones",
        "medications": "1. Imiquimod 5% cream — apply 3 times per week at bedtime to individual lesions. "
                       "Remove after 6-10 hours. Use for up to 12 weeks.\n"
                       "2. Hydrogen peroxide 1% cream (Crystacide) — apply twice daily as an alternative "
                       "if imiquimod causes irritation.\n"
                       "3. Paediatric antihistamine (Cetirizine 2.5mg syrup) — if pruritus is significant.",
        "care_instructions": "• Do not puncture or squeeze the lesions — this spreads the virus.\n"
                              "• Cover lesions with waterproof dressing during swimming or sports.\n"
                              "• Do not share towels, clothing, or bathing sponges.\n"
                              "• Wash hands thoroughly after touching affected area.\n"
                              "• Lesions are self-limiting but may take 6-18 months to fully resolve.",
        "warning_signs": "Return in-person or online if: lesions become red, hot, and painful (superinfection), "
                         "new lesions appear on the face or eyelids, or the number of lesions increases to more than 50.",
        "follow_up": True,
        "follow_up_days": 60,
        "follow_up_instructions": "Review in 8 weeks. Take photographs of all lesion sites before visit. "
                                   "Bring current medication list.",
    },
    {
        "chief_complaint": "Severe itching and redness in elbow and knee creases since 10 days. "
                           "Child wakes up at night to scratch. Family history of asthma.",
        "severity": "MODERATE",
        "assessment": "Presentation strongly consistent with moderate-to-severe Atopic Dermatitis (Eczema) "
                      "in a child with known atopic triad (eczema, asthma, hay fever). "
                      "SCORAD estimated at ~38 (moderate) based on photo documentation. "
                      "Erythema, excoriation, and lichenification visible at both antecubital and popliteal fossae. "
                      "No signs of secondary bacterial infection (no crusting or honey-coloured discharge).",
        "differential": "Contact dermatitis, Seborrhoeic dermatitis, Scabies (rule out if pruritus nocturna is dominant)",
        "medications": "1. Tacrolimus 0.03% ointment — apply thin layer to affected skin twice daily.\n"
                       "   Continue for 4 weeks. Do not apply to skin with active infections.\n"
                       "2. Mometasone furoate 0.1% cream — apply once daily for 7 days on acutely inflamed areas only.\n"
                       "   Taper to alternate days for a further 7 days.\n"
                       "3. Emollient: Cetaphil Restoraderm Lotion — apply 3-4 times daily to entire body.\n"
                       "4. Cetirizine 5mg oral — once at night for 2 weeks (sedating effect aids night-time itch control).",
        "care_instructions": "• Short lukewarm bath (10 minutes max), immediately followed by emollient.\n"
                              "• Wet wrap therapy for severe flares: apply emollient, then damp cotton layer, "
                              "then dry cotton layer. Leave overnight.\n"
                              "• Identify and avoid triggers: sweating, wool, pet dander, chlorinated pools.\n"
                              "• Keep bedroom cool and use anti-allergy pillowcases and duvet covers.\n"
                              "• Trim nails weekly to prevent scratch-induced infection.",
        "warning_signs": "Attend emergency/paediatric casualty if: golden-coloured crusting appears (impetigo), "
                         "fever above 38.5°C, blisters or oozing worsens acutely, or child refuses to eat/drink.",
        "follow_up": True,
        "follow_up_days": 28,
        "follow_up_instructions": "Review in 4 weeks with photographs. If SCORAD not improved by 30%, "
                                   "referral to in-person specialist for consideration of dupilumab.",
    },
    {
        "chief_complaint": "Yellow crusting and honey-coloured discharge around nose and mouth for 5 days. "
                           "Started as a small cut, now spreading. Child attends playschool.",
        "severity": "MODERATE",
        "assessment": "Clinical appearance strongly consistent with Non-bullous Impetigo (Staphylococcal/Streptococcal). "
                      "Characteristic honey-coloured crusted plaques around the perioral and nasal regions visible "
                      "on submitted images. Lesion distribution and appearance are textbook non-bullous impetigo. "
                      "No systemic signs of toxicity or necrotising features present.",
        "differential": "Herpes simplex labialis, Bullous impetigo (less likely — no bullae), Angular cheilitis",
        "medications": "1. Mupirocin 2% ointment (Bactroban) — apply to all lesions three times daily for 5 days. "
                       "Cover lesions with gauze.\n"
                       "2. Cephalexin 125mg/5ml suspension — 25mg/kg/day in 4 divided doses for 7 days "
                       "(if extensive lesions — confirm weight before dispensing).\n"
                       "3. Chlorhexidine 4% wash (Hibiscrub diluted 1:1) — gently cleanse crusted areas once daily.",
        "care_instructions": "• Gently soak crusts with warm water and gauze before applying antibiotic cream.\n"
                              "• Wash hands thoroughly before and after touching affected areas.\n"
                              "• Keep child's fingernails short and clean.\n"
                              "• Do not send child to school until crusts are fully dry and healed (typically 48-72 hrs after antibiotic start).\n"
                              "• Wash all towels, pillowcases, and clothing in hot water daily.\n"
                              "• Do not share eating utensils during treatment period.",
        "warning_signs": "Attend emergency immediately if: fever rises above 39°C, rash spreads to eyes, "
                         "child develops painful swollen lymph nodes, or if skin becomes deeply red and hot (cellulitis).",
        "follow_up": False,
        "follow_up_days": 0,
        "follow_up_instructions": "Return if lesions do not resolve within 7-10 days of antibiotic therapy, "
                                   "or if any new lesions appear after completing the course.",
    },
    {
        "chief_complaint": "Circular bald patch on scalp, about 2cm. No itching. Appeared 3 weeks ago. "
                           "Child otherwise healthy. Teacher noticed it.",
        "severity": "MILD",
        "assessment": "High suspicion for Tinea Capitis (scalp ringworm) based on smooth, circular alopecic "
                      "patch with slight scaling at the border. Black dot sign not clearly visible in photos — "
                      "Wood's lamp examination recommended in-person. Alternatively, Alopecia Areata considered "
                      "as differential (exclamation mark hairs not visible in photos). "
                      "Fungal culture via hair pluck recommended to confirm Trichophyton tonsurans.",
        "differential": "Alopecia Areata, Trichotillomania, Seborrhoeic dermatitis, Psoriasis of scalp",
        "medications": "1. Griseofulvin oral suspension 15-20mg/kg/day — once daily with fatty food for 6-8 weeks.\n"
                       "2. Selenium sulphide 2.5% shampoo — apply to scalp, leave for 5 minutes, rinse. "
                       "Use twice weekly for 4 weeks (reduces spore shedding and prevents household spread).\n"
                       "3. Topical antifungal (Clotrimazole 1% solution) to scalp border — once daily for 4 weeks.",
        "care_instructions": "• All household contacts should use selenium sulphide shampoo twice weekly for 2 weeks.\n"
                              "• Do not share combs, brushes, hats, pillowcases, or hair ties.\n"
                              "• Treat all combs and brushes in antifungal solution.\n"
                              "• Inform the school nurse — asymptomatic carriers among classmates are common.\n"
                              "• Hair regrowth expected in 2-3 months after completing treatment.",
        "warning_signs": "Return immediately if: scalp becomes swollen, tender, and boggy (Kerion formation — "
                         "this requires oral steroids and urgent review), or if fever develops.",
        "follow_up": True,
        "follow_up_days": 56,
        "follow_up_instructions": "Review at 8 weeks with Wood's lamp and clinical photographs. "
                                   "If hair not regrowing, consider repeat fungal culture and alternative antifungal.",
    },
]

# ─── AI Analysis outputs ───────────────────────────────────────────────────────
AI_SYMPTOM_SUMMARIES = [
    {
        "summary": "Parent reports child has had red, itchy patches in elbow and knee creases for 10 days. "
                   "Scratching worsens at night. No fever. Family history of asthma and hay fever. "
                   "Child attends daycare. No new soaps or detergents used recently.",
        "triage": "moderate",
        "flags": [],
        "follow_up_questions_answered": [
            {"q": "How long have symptoms been present?", "a": "10 days"},
            {"q": "Is there itching?", "a": "Yes, severe — wakes child at night"},
            {"q": "Any fever or other systemic symptoms?", "a": "No fever"},
            {"q": "Family history of allergic conditions?", "a": "Yes — asthma and hay fever in both parents"},
        ]
    },
    {
        "summary": "Parent describes small, flesh-coloured bumps appearing on the child's chest and underarms "
                   "over 2 months. No pain. School nurse raised concern about contagion. No fever or malaise.",
        "triage": "mild",
        "flags": [],
        "follow_up_questions_answered": [
            {"q": "How long have bumps been present?", "a": "About 2 months"},
            {"q": "Are bumps painful or itchy?", "a": "Slightly itchy, not painful"},
            {"q": "Any similar bumps on other family members?", "a": "Younger sibling has 2 bumps on forearm"},
            {"q": "Any fever?", "a": "No"},
        ]
    },
]

AI_VISION_OUTPUTS = [
    {
        "image_quality": "Adequate — image is in focus and well-lit. Consider uploading a close-up for better lesion detail.",
        "visible_observations": "Multiple well-demarcated, erythematous plaques with overlying white-silvery scale "
                                 "visible on extensor surfaces. Lesion morphology is consistent with plaque-type involvement. "
                                 "No visible pustules, blistering, or signs of secondary infection in submitted photos.",
        "additional_info_needed": [
            "Duration of current flare",
            "Any new triggers in the past month (stress, infection, medication change)",
            "Nail examination photos if possible (pitting, onycholysis)",
            "Joint pain or swelling in fingers or toes"
        ],
        "safety_note": "These observations are for clinical support only. This AI output is not a diagnosis. "
                       "All clinical decisions must be made by the reviewing dermatologist.",
        "recommendation": "Clinical review required. Lesion morphology warrants dermatologist assessment."
    },
    {
        "image_quality": "Good — multiple angles provided. Umbilication feature visible on close-up. Well lit.",
        "visible_observations": "Pearly, dome-shaped papules with central umbilication visible. "
                                 "Approximately 15-20 lesions distributed on anterior trunk and bilateral axillae. "
                                 "No erythema surrounding individual lesions. No sign of secondary bacterial infection.",
        "additional_info_needed": [
            "Whether lesions have increased in number since onset",
            "History of swimming pool exposure",
            "Any similar lesions on household contacts",
            "Current immunisation status"
        ],
        "safety_note": "These observations are for clinical support only. This AI output is not a diagnosis.",
        "recommendation": "Clinical review required. Morphology supports viral aetiology."
    },
]


class Command(BaseCommand):
    help = "Seed the database with realistic pediatric teledermatology demo data."

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing seeded data before seeding (keeps superusers).',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        from accounts.models import DoctorProfile, ParentProfile
        from patients.models import ChildProfile
        from appointments.models import Appointment
        from consultations.models import Consultation, TreatmentPlan
        from ai_assistant.models import AIAnalysis

        if options['clear']:
            self.stdout.write(self.style.WARNING("Clearing existing demo data..."))
            AIAnalysis.objects.all().delete()
            TreatmentPlan.objects.all().delete()
            Consultation.objects.all().delete()
            Appointment.objects.all().delete()
            ChildProfile.objects.all().delete()
            User.objects.filter(role__in=['DOCTOR', 'PARENT']).delete()
            self.stdout.write(self.style.SUCCESS("Cleared."))

        self.stdout.write(self.style.MIGRATE_HEADING("\n🩺 CareNest — Seeding Realistic Demo Data\n"))

        # ── 1. Create Doctors ──────────────────────────────────────────────────
        self.stdout.write("  Creating doctors...")
        doctor_users = []
        for d in DOCTORS:
            user, created = User.objects.get_or_create(
                username=d["username"],
                defaults={
                    "first_name": d["first_name"],
                    "last_name": d["last_name"],
                    "email": d["email"],
                    "phone_number": d.get("phone_number", ""),
                    "role": User.Role.DOCTOR,
                }
            )
            if created:
                user.set_password("Doctor@carenest2024")
                user.save()

            profile, _ = DoctorProfile.objects.get_or_create(
                user=user,
                defaults={
                    "license_number": d["license_number"],
                    "specialization": d["specialization"],
                    "experience_years": d["experience_years"],
                    "consultation_fee": d["consultation_fee"],
                    "bio": d["bio"],
                    "is_verified": d["is_verified"],
                }
            )
            # Always update profile data to latest seed values
            DoctorProfile.objects.filter(user=user).update(
                license_number=d["license_number"],
                specialization=d["specialization"],
                experience_years=d["experience_years"],
                consultation_fee=d["consultation_fee"],
                bio=d["bio"],
                is_verified=d["is_verified"],
            )            doctor_users.append(user)
            status = self.style.SUCCESS("created") if created else self.style.WARNING("already exists")
            self.stdout.write(f"    Dr. {d['first_name']} {d['last_name']} — {status}")

        # ── 2. Create Parents & Children ────────────────────────────────────────
        self.stdout.write("\n  Creating parents & children...")
        all_children = []
        parent_users = []

        for family in FAMILIES:
            pd = family["parent"]
            parent, created = User.objects.get_or_create(
                username=pd["username"],
                defaults={
                    "first_name": pd["first_name"],
                    "last_name": pd["last_name"],
                    "email": pd["email"],
                    "phone_number": pd.get("phone_number", ""),
                    "role": User.Role.PARENT,
                }
            )
            if created:
                parent.set_password("Parent@carenest2024")
                parent.save()

            ParentProfile.objects.filter(user=parent).update(
                emergency_contact=pd.get("emergency_contact", ""),
                preferred_language=pd.get("preferred_language", "English"),
                consent_to_telehealth=True,
            )

            status = self.style.SUCCESS("created") if created else self.style.WARNING("already exists")
            self.stdout.write(f"    {pd['first_name']} {pd['last_name']} — {status}")
            parent_users.append(parent)

            for cd in family["children"]:
                child, c_created = ChildProfile.objects.get_or_create(
                    parent=parent,
                    first_name=cd["first_name"],
                    last_name=cd["last_name"],
                    defaults={
                        "date_of_birth": cd["dob"],
                        "gender": cd["gender"],
                        "blood_group": cd["blood_group"],
                        "known_allergies": cd.get("known_allergies", ""),
                        "previous_skin_conditions": cd.get("previous_skin_conditions", ""),
                        "current_medications": cd.get("current_medications", ""),
                        "medical_history_notes": cd.get("medical_history_notes", ""),
                    }
                )
                all_children.append(child)
                c_status = self.style.SUCCESS("created") if c_created else self.style.WARNING("already exists")
                self.stdout.write(f"      └─ Child: {child.full_name} — {c_status}")

        # ── 3. Create Appointments ───────────────────────────────────────────────
        self.stdout.write("\n  Creating appointments...")
        created_appointments = []
        today = timezone.now().date()

        # Build a mix of past (completed), current (confirmed), and future (pending)
        appointment_configs = [
            # (parent_idx, child_idx, doctor_idx, days_offset, status)
            (0, 0, 0, -20, 'COMPLETED'),   # Meena's Aryan — completed with Dr. Priya
            (0, 1, 2, -10, 'COMPLETED'),   # Meena's Riya — completed with Dr. Sunita
            (1, 0, 3,  -5, 'COMPLETED'),   # Rohit's Kabir — completed with Dr. Rahul
            (2, 0, 0,  -2, 'CONFIRMED'),   # Anjali's Dhruv — confirmed today-ish with Dr. Priya
            (2, 1, 2,   7, 'PENDING'),     # Anjali's Pooja — pending next week Dr. Sunita
            (3, 0, 1,  -8, 'COMPLETED'),   # Suresh's Preethi — completed with Dr. Arjun
            (3, 0, 1,  14, 'PENDING'),     # Suresh's Preethi — follow-up pending with Dr. Arjun
            (4, 0, 4,  -3, 'CONFIRMED'),   # Fatima's Zara — confirmed with Dr. Kavitha
            (4, 1, 2,  10, 'PENDING'),     # Fatima's Ayaan — pending Dr. Sunita
            (0, 0, 1,  21, 'PENDING'),     # Meena's Aryan — pending with Dr. Arjun (follow-up)
        ]

        # Flatten parent-child refs
        parent_children_map = []
        for family in FAMILIES:
            pd = family["parent"]
            parent = User.objects.get(username=pd["username"])
            kids = list(ChildProfile.objects.filter(parent=parent).order_by('first_name'))
            parent_children_map.append((parent, kids))

        appointment_hour_slots = [9, 10, 11, 14, 15, 16]

        for i, (p_idx, c_idx, d_idx, day_offset, status) in enumerate(appointment_configs):
            parent, kids = parent_children_map[p_idx]
            if c_idx >= len(kids):
                continue
            child = kids[c_idx]
            doctor = doctor_users[d_idx]
            sched_date = today + timedelta(days=day_offset)
            sched_time = time(random.choice(appointment_hour_slots), 0)

            scenario = APPOINTMENT_SCENARIOS[i % len(APPOINTMENT_SCENARIOS)]

            appt, created = Appointment.objects.get_or_create(
                parent=parent,
                child=child,
                doctor=doctor,
                scheduled_date=sched_date,
                defaults={
                    "scheduled_time": sched_time,
                    "status": status,
                    "chief_complaint": scenario["chief_complaint"][:255],
                    "severity": scenario["severity"],
                }
            )
            if not created:
                appt.status = status
                appt.save()

            created_appointments.append((appt, scenario, status))
            a_status = self.style.SUCCESS("created") if created else self.style.WARNING("updated")
            self.stdout.write(
                f"    Appt #{appt.pk}: {child.full_name} → Dr. {doctor.last_name} "
                f"on {sched_date} [{status}] — {a_status}"
            )

        # ── 4. Create Consultations & Treatment Plans for COMPLETED appointments ──
        self.stdout.write("\n  Creating consultations & treatment plans...")
        for appt, scenario, status in created_appointments:
            if status != 'COMPLETED':
                continue

            consultation, c_created = Consultation.objects.get_or_create(
                appointment=appt,
                defaults={
                    "doctor": appt.doctor,
                    "clinical_assessment": scenario["assessment"],
                    "differential_diagnosis": scenario["differential"],
                    "severity": scenario["severity"],
                    "clinical_notes": f"[Private] Patient reviewed via teledermatology. "
                                      f"Images were of {random.choice(['adequate', 'good', 'sufficient'])} quality. "
                                      f"Parent was cooperative and provided full history.",
                    "is_finalized": True,
                    "finalized_at": timezone.now() - timedelta(days=random.randint(1, 5)),
                }
            )

            if c_created:
                tp_follow_date = None
                if scenario["follow_up"] and scenario["follow_up_days"]:
                    tp_follow_date = today + timedelta(days=scenario["follow_up_days"])

                TreatmentPlan.objects.get_or_create(
                    consultation=consultation,
                    defaults={
                        "prescribed_medications": scenario["medications"],
                        "care_instructions": scenario["care_instructions"],
                        "warning_signs": scenario["warning_signs"],
                        "follow_up_recommended": scenario["follow_up"],
                        "follow_up_date": tp_follow_date,
                        "follow_up_instructions": scenario.get("follow_up_instructions", ""),
                    }
                )
                self.stdout.write(
                    f"    Consultation #{consultation.pk} + Treatment Plan — "
                    + self.style.SUCCESS("created")
                )
            else:
                self.stdout.write(f"    Consultation #{consultation.pk} — {self.style.WARNING('already exists')}")

        # ── 5. Create AI Analysis records ─────────────────────────────────────
        self.stdout.write("\n  Creating AI analysis records...")
        for i, (appt, scenario, status) in enumerate(created_appointments[:4]):
            child = appt.child

            # Symptom chat analysis
            symptom_data = AI_SYMPTOM_SUMMARIES[i % len(AI_SYMPTOM_SUMMARIES)]
            AIAnalysis.objects.get_or_create(
                child=child,
                appointment=appt,
                analysis_type='SYMPTOM_CHAT',
                defaults={
                    "input_context": {
                        "messages": symptom_data["follow_up_questions_answered"],
                        "chief_complaint": appt.chief_complaint,
                    },
                    "structured_output": {
                        "summary": symptom_data["summary"],
                        "triage": symptom_data["triage"],
                        "flags": symptom_data["flags"],
                    },
                    "status": "COMPLETED",
                    "doctor_reviewed": status == 'COMPLETED',
                    "reviewed_at": timezone.now() - timedelta(days=1) if status == 'COMPLETED' else None,
                }
            )

            # Vision analysis
            vision_data = AI_VISION_OUTPUTS[i % len(AI_VISION_OUTPUTS)]
            AIAnalysis.objects.get_or_create(
                child=child,
                appointment=appt,
                analysis_type='IMAGE_OBSERVATION',
                defaults={
                    "input_context": {
                        "body_part": "ARMS",
                        "symptoms_description": appt.chief_complaint,
                    },
                    "structured_output": vision_data,
                    "status": "COMPLETED",
                    "doctor_reviewed": status == 'COMPLETED',
                    "reviewed_at": timezone.now() - timedelta(hours=random.randint(2, 48)) if status == 'COMPLETED' else None,
                }
            )

        ai_count = AIAnalysis.objects.count()
        self.stdout.write(f"    AI analysis records total: {self.style.SUCCESS(str(ai_count))}")

        # ── 6. Create Admin Superuser ──────────────────────────────────────────
        self.stdout.write("\n  Creating admin superuser...")
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@carenest.health',
                password='Admin@carenest2024',
                first_name='Admin',
                last_name='CareNest',
            )
            self.stdout.write("    admin@carenest.health — " + self.style.SUCCESS("created"))
        else:
            self.stdout.write("    admin — " + self.style.WARNING("already exists"))

        # ── Summary ─────────────────────────────────────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING("\n✅ Seeding Complete!\n"))
        self.stdout.write(self.style.SUCCESS(f"  Doctors:          {User.objects.filter(role='DOCTOR').count()}"))
        self.stdout.write(self.style.SUCCESS(f"  Parents:          {User.objects.filter(role='PARENT').count()}"))
        self.stdout.write(self.style.SUCCESS(f"  Children:         {ChildProfile.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"  Appointments:     {Appointment.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"  Consultations:    {Consultation.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"  Treatment Plans:  {TreatmentPlan.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"  AI Analyses:      {AIAnalysis.objects.count()}"))

        self.stdout.write("\n" + self.style.WARNING("Login credentials:"))
        self.stdout.write("  Admin:    admin / Admin@carenest2024")
        self.stdout.write("  Doctors:  dr_priya_sharma (and others) / Doctor@carenest2024")
        self.stdout.write("  Parents:  meena_kapoor (and others) / Parent@carenest2024")
        self.stdout.write("\n  → http://127.0.0.1:8000/\n")
