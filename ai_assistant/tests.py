import io
import json
from PIL import Image
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from patients.models import ChildProfile, SkinImage
from appointments.models import Appointment
from consultations.models import Consultation, TreatmentPlan
from ai_assistant.models import AIAnalysis
from ai_assistant.services import (
    OpenAISymptomAssistant,
    OpenAIVisionAssistant,
    OpenAIConsultationSummarizer,
)

User = get_user_model()

class AIAssistantSuiteTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.parent = User.objects.create_user(
            username='parent_ai', email='pai@example.com', password='password123', role=User.Role.PARENT
        )
        self.doctor = User.objects.create_user(
            username='doctor_ai', email='dai@example.com', password='password123', role=User.Role.DOCTOR
        )
        self.other_doctor = User.objects.create_user(
            username='other_doctor', email='otherdoc@example.com', password='password123', role=User.Role.DOCTOR
        )

        self.child = ChildProfile.objects.create(
            parent=self.parent,
            first_name='Maya',
            last_name='Lin',
            date_of_birth=date(2023, 6, 1),
            gender=ChildProfile.Gender.FEMALE
        )

        self.appointment = Appointment.objects.create(
            child=self.child,
            parent=self.parent,
            doctor=self.doctor,
            scheduled_date=date(2026, 12, 1),
            scheduled_time=Appointment._meta.get_field('scheduled_time').get_default() or '10:00:00',
            chief_complaint='Eczema'
        )

        # Create valid skin image
        buffer = io.BytesIO()
        img = Image.new('RGB', (450, 450), color=(150, 100, 100))
        img.save(buffer, format='JPEG')
        buffer.seek(0)
        upload = SimpleUploadedFile('test.jpg', buffer.read(), content_type='image/jpeg')

        self.skin_image = SkinImage.objects.create(
            child=self.child,
            appointment=self.appointment,
            image=upload,
            body_part=SkinImage.BodyPart.FACE
        )

        self.consultation = Consultation.objects.create(
            appointment=self.appointment,
            doctor=self.doctor,
            clinical_assessment='Infantile atopic dermatitis flare',
            is_finalized=True
        )
        self.treatment_plan = TreatmentPlan.objects.create(
            consultation=self.consultation,
            prescribed_medications='Hydrocortisone 1%',
            care_instructions='Baths under 10 min'
        )

    def test_fallback_triage_without_api_key(self):
        assistant = OpenAISymptomAssistant()
        assistant.api_key = ''
        
        history = [{'role': 'user', 'content': 'My baby has a red itchy rash on her cheeks for 2 days.'}]
        child_context = {'name': 'Maya', 'age': '8 months old', 'allergies': 'None'}
        
        result = assistant.generate_chat_response(history, child_context)
        self.assertIn('reply', result)
        self.assertIn('structured_summary', result)
        summary = result['structured_summary']
        self.assertTrue(summary['itching_reported'])
        self.assertFalse(summary['fever_reported'])

    def test_vision_assistant_fallback_schema(self):
        vision = OpenAIVisionAssistant()
        vision.api_key = ''

        result = vision.analyze_skin_image(self.skin_image)
        self.assertIn('image_quality', result)
        self.assertIn('visible_characteristics', result)
        self.assertIn('clinical_disclaimer', result)
        self.assertIn('morphology_category', result)
        self.assertTrue(len(result['visible_characteristics']) > 0)

    def test_analyze_skin_image_api_endpoint(self):
        self.client.force_login(self.doctor)
        res = self.client.post(reverse('ai_assistant:api_analyze_image', kwargs={'image_id': self.skin_image.id}))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertIn('analysis_id', data)
        self.assertIn('result', data)

    def test_generate_and_approve_consultation_summary(self):
        # Generate draft summary
        self.client.force_login(self.doctor)
        res = self.client.post(reverse('ai_assistant:api_generate_summary', kwargs={'consultation_id': self.consultation.id}))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertFalse(data['doctor_reviewed'])
        analysis_id = data['analysis_id']

        analysis = AIAnalysis.objects.get(id=analysis_id)
        self.assertFalse(analysis.doctor_reviewed)

        # Other doctor attempting approval -> 403 Forbidden
        self.client.force_login(self.other_doctor)
        unauth_res = self.client.post(reverse('ai_assistant:api_approve_summary', kwargs={'analysis_id': analysis_id}))
        self.assertEqual(unauth_res.status_code, 403)

        # Assigned doctor approves -> 200 OK
        self.client.force_login(self.doctor)
        approve_res = self.client.post(reverse('ai_assistant:api_approve_summary', kwargs={'analysis_id': analysis_id}))
        self.assertEqual(approve_res.status_code, 200)
        
        analysis.refresh_from_db()
        self.assertTrue(analysis.doctor_reviewed)
        self.assertIsNotNone(analysis.reviewed_at)
