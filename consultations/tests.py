from datetime import date, time, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from patients.models import ChildProfile
from appointments.models import Appointment
from consultations.models import Consultation, TreatmentPlan
from consultations.services.pdf_generator import render_consultation_pdf

User = get_user_model()

class ConsultationWorkflowTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.parent = User.objects.create_user(
            username='parent_user', email='p@example.com', password='password123', role=User.Role.PARENT
        )
        self.unrelated_parent = User.objects.create_user(
            username='unrelated_parent', email='unrelated@example.com', password='password123', role=User.Role.PARENT
        )
        self.doctor = User.objects.create_user(
            username='doctor_user', email='doc@example.com', password='password123', role=User.Role.DOCTOR
        )

        self.child = ChildProfile.objects.create(
            parent=self.parent,
            first_name='Lucas',
            last_name='Scott',
            date_of_birth=date(2022, 1, 10),
            gender=ChildProfile.Gender.MALE
        )

        self.appointment = Appointment.objects.create(
            child=self.child,
            parent=self.parent,
            doctor=self.doctor,
            scheduled_date=timezone.now().date() + timedelta(days=2),
            scheduled_time=time(11, 0),
            status=Appointment.Status.CONFIRMED,
            chief_complaint='Eczema rash'
        )

        self.consultation = Consultation.objects.create(
            appointment=self.appointment,
            doctor=self.doctor,
            clinical_assessment='Infantile Atopic Dermatitis flare-up',
            severity=Consultation.Severity.MILD
        )

        self.treatment_plan = TreatmentPlan.objects.create(
            consultation=self.consultation,
            prescribed_medications='Hydrocortisone 1% cream apply twice daily for 5 days',
            care_instructions='Lukewarm baths, gentle emollient after bathing',
            warning_signs='Seek ER if high fever or golden crusting develops'
        )

    def test_finalizing_consultation_updates_appointment_to_completed(self):
        self.assertFalse(self.consultation.is_finalized)
        self.assertEqual(self.appointment.status, Appointment.Status.CONFIRMED)

        self.consultation.finalize()

        self.assertTrue(self.consultation.is_finalized)
        self.assertIsNotNone(self.consultation.finalized_at)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, Appointment.Status.COMPLETED)

    def test_unfinalized_report_inaccessible_to_parent(self):
        self.client.force_login(self.parent)
        res = self.client.get(reverse('consultations:parent_report', kwargs={'pk': self.consultation.pk}))
        # Not finalized yet -> 404
        self.assertEqual(res.status_code, 404)

    def test_finalized_report_accessible_to_parent(self):
        self.consultation.finalize()
        self.client.force_login(self.parent)
        res = self.client.get(reverse('consultations:parent_report', kwargs={'pk': self.consultation.pk}))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'consultations/parent_report_detail.html')
        self.assertContains(res, 'Infantile Atopic Dermatitis')

    def test_cross_parent_report_access_blocked(self):
        self.consultation.finalize()
        self.client.force_login(self.unrelated_parent)
        res = self.client.get(reverse('consultations:parent_report', kwargs={'pk': self.consultation.pk}))
        self.assertEqual(res.status_code, 403)

    def test_pdf_generation_service(self):
        pdf_bytes = render_consultation_pdf(self.consultation)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'), "PDF output does not have %PDF magic header")

    def test_download_pdf_view(self):
        self.consultation.finalize()
        self.client.force_login(self.parent)
        res = self.client.get(reverse('consultations:download_pdf', kwargs={'pk': self.consultation.pk}))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'application/pdf')
        self.assertTrue(res.content.startswith(b'%PDF'))
