# Gamma PPT Generation Prompt

Copy the prompt below and paste it into [gamma.app](https://gamma.app) → **"Generate with AI"**

---

## Prompt to paste into Gamma

```
Create a professional 12-slide presentation for a college project titled:

"CareNest – Pediatric Teledermatology Platform"
Subtitle: "AI-Assisted Remote Skin Consultation for Children"

Design style: Modern healthcare tech. Use a clean teal and white color palette with dark navy accents. Include relevant medical/tech icons and visuals on each slide. Keep text concise and use bullet points.

---

Slide 1 – Title Slide
Title: CareNest – Pediatric Teledermatology
Subtitle: AI-Assisted Remote Skin Consultation for Children
Tagline: "Expert dermatology care for your child, from the comfort of home."
Include: a visual of a parent holding a phone with a doctor on screen

---

Slide 2 – Problem Statement
Heading: The Gap in Pediatric Skin Care
Bullets:
- 1 in 5 children suffers from skin conditions like eczema, psoriasis, or fungal infections
- Specialist wait times in India average 4–6 weeks
- Rural and semi-urban families lack access to pediatric dermatologists
- Parents often misidentify skin conditions, leading to incorrect home remedies
- Early mismanagement worsens chronic conditions like atopic dermatitis
Visual: a world map or India map with rural area highlight

---

Slide 3 – Our Solution
Heading: What is CareNest?
Bullets:
- A web-based telemedicine platform for pediatric dermatology consultations
- Parents upload photos of their child's skin condition
- AI performs a preliminary image analysis and symptom screening
- A verified pediatric dermatologist reviews the case remotely
- Parents receive a detailed consultation report and downloadable PDF treatment plan
Visual: a simple 4-step flow diagram: Upload → AI Analysis → Doctor Review → Report

---

Slide 4 – Key Features
Heading: Platform Features at a Glance
Two-column layout:
Left column – Parent Side:
- Register multiple children under one account
- AI Symptom Chat before booking
- Upload medical-grade skin images
- Book appointments with verified doctors
- View and download PDF consultation reports

Right column – Doctor Side:
- Clinical dashboard with appointment queue
- AI Vision Analysis of uploaded images
- Write clinical assessments and treatment plans
- Manage appointment status (Pending → Confirmed → Completed)
- AI-generated consultation summaries (doctor-approved)

---

Slide 5 – User Roles
Heading: Three-Role Access System
Visual: 3 cards side by side

Card 1 – Parent / Guardian
- Registers and manages child profiles
- Books consultations and uploads images
- Views reports and follow-up plans

Card 2 – Pediatric Dermatologist
- Reviews skin images and AI observations
- Records clinical assessments
- Issues treatment plans and prescriptions

Card 3 – Administrator
- Manages doctors, parents and appointments
- Monitors platform activity via Django Admin

---

Slide 6 – AI Features
Heading: Intelligent AI Integration (OpenAI GPT-4o)
Three feature blocks:

Feature 1 – AI Symptom Assistant
Before booking, parents answer structured questions. AI produces a clinical symptom summary attached to the appointment.

Feature 2 – AI Skin Vision Analysis
Uploaded images are analyzed by GPT-4o Vision. AI describes visible features, image quality, and flags additional info needed. Never diagnoses — supports the doctor.

Feature 3 – AI Consultation Summarizer
After the doctor finalizes a report, AI simplifies the clinical language into a parent-friendly summary. Doctor must approve before it is shared.

Safety Note: All AI outputs are non-diagnostic. Emergency red-flag phrases trigger urgent warnings. Doctor approval gates all clinical content.

---

Slide 7 – Tech Stack
Heading: Technology Stack
Visual: a clean tech stack diagram or icon grid

Backend: Django 5.2 (Python) – MTV architecture, Class-Based Views, signals, custom managers
Database: SQLite (development) → PostgreSQL (production-ready)
Frontend: Tailwind CSS (CDN) – Dark/Light mode toggle, responsive design
AI: OpenAI GPT-4o and GPT-4o Vision via official Python SDK
PDF Generation: xhtml2pdf + ReportLab
Authentication: Django's built-in auth + custom Role-Based Access Control
Security: CSRF protection, IDOR isolation, session management, XSS headers

---

Slide 8 – System Architecture
Heading: Application Architecture
Visual: a layered architecture diagram

Layer 1 – Django Apps (5 apps):
accounts | patients | appointments | consultations | ai_assistant

Layer 2 – Core Django Concepts Used:
AbstractUser with Role enum | post_save signals | Custom QuerySet managers
UniqueConstraint (double-booking prevention) | Context processors | Template tags

Layer 3 – External Services:
OpenAI API (with offline fallback) | xhtml2pdf for PDF reports

---

Slide 9 – Database Design
Heading: Data Models Overview
Visual: a simple ER-style table or entity list

Models:
- User (custom AbstractUser) → role: PARENT / DOCTOR / ADMIN
- DoctorProfile (OneToOne with User) → specialization, license, bio, fee
- ParentProfile (OneToOne with User) → emergency contact, language, consent
- ChildProfile → DOB, allergies, medications, medical history
- SkinImage → body part, view type, image file, appointment link
- Appointment → doctor, child, parent, date/time, status, severity
- Consultation → clinical assessment, differential diagnosis, finalized flag
- TreatmentPlan → medications, care instructions, follow-up date
- AIAnalysis → type (chat/vision/summary), structured JSON output, doctor reviewed

---

Slide 10 – Security & Testing
Heading: Security Hardening & Quality Assurance

Security Measures:
- IDOR protection: all querysets are parent-scoped (cross-parent access returns HTTP 404)
- CSRF and session cookie hardening (HttpOnly, SameSite=Lax)
- X-Frame-Options: DENY (clickjacking protection)
- Content-Type nosniff and XSS filter headers
- 2-hour session timeout with activity-based reset
- 10MB upload size limit with Pillow byte-level image validation
- AI outputs never reach users without doctor approval

Test Suite:
- 36 automated tests across 5 Django apps
- Tests cover: auth, role-based redirect, IDOR isolation, double-booking constraint, PDF generation, AI fallback, consultation workflow
- 100% pass rate

---

Slide 11 – Demo Flow
Heading: How a Consultation Works – Step by Step
Visual: numbered flow or timeline

1. Parent registers → creates child profile with medical history
2. Parent uses AI Symptom Chat → AI generates structured complaint summary
3. Parent selects a verified doctor → books appointment slot
4. Parent uploads clear photos of the skin condition
5. AI Vision Analysis runs → doctor receives preliminary observations
6. Doctor reviews case, images, and AI notes in clinical workspace
7. Doctor writes assessment, differential diagnosis, and treatment plan
8. Consultation is finalized → report is visible to parent
9. Parent downloads PDF treatment plan with medications and care instructions
10. Follow-up appointment is scheduled if recommended

---

Slide 12 – Summary & Impact
Heading: Why CareNest Matters

Impact Points:
- Bridges the gap between rural families and specialist dermatologists
- Reduces unnecessary in-person visits for non-urgent skin conditions
- AI assistance speeds up triage and improves clinical efficiency
- Transparent, non-diagnostic AI: doctor always makes the final call
- Fully open-source, built on production-grade Django and OpenAI

Project Stats:
- 5 Django apps | 36 passing tests | 11 data models | 3 user roles
- 3 AI features | Real-time dark/light mode UI | PDF report generation
- 10 seeded demo appointments with real clinical data

Closing line: "CareNest — Expert pediatric skin care, wherever you are."
```

---

## Tips for Gamma

- After pasting, choose **"Presentation"** as the output format
- Select a **healthcare or tech** theme (teal/blue tones work best)
- Ask Gamma to **add images** on each slide for visual impact
- You can say: *"Make it look like a startup pitch deck"* for a more polished style
- After generation, manually swap in real screenshots of the app on slides 3, 6, and 11

