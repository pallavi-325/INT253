from datetime import date, time, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from patients.models import ChildProfile
from appointments.models import Appointment

User = get_user_model()

class AppointmentSchedulingTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.parent = User.objects.create_user(
            username='parent_user', email='p@example.com', password='password123', role=User.Role.PARENT
        )
        self.other_parent = User.objects.create_user(
            username='other_parent', email='other@example.com', password='password123', role=User.Role.PARENT
        )
        self.doctor = User.objects.create_user(
            username='doctor_user', email='doc@example.com', password='password123', role=User.Role.DOCTOR
        )

        self.child = ChildProfile.objects.create(
            parent=self.parent,
            first_name='Emma',
            last_name='Watson',
            date_of_birth=date(2022, 3, 10),
            gender=ChildProfile.Gender.FEMALE
        )

    def test_past_date_booking_fails_validation(self):
        past_date = timezone.now().date() - timedelta(days=2)
        appt = Appointment(
            child=self.child,
            parent=self.parent,
            doctor=self.doctor,
            scheduled_date=past_date,
            scheduled_time=time(10, 0),
            chief_complaint='Rash'
        )
        with self.assertRaises(ValidationError):
            appt.full_clean()

    def test_cross_parent_child_booking_blocked(self):
        future_date = timezone.now().date() + timedelta(days=3)
        # other_parent trying to book for self.child (who belongs to self.parent)
        appt = Appointment(
            child=self.child,
            parent=self.other_parent,
            doctor=self.doctor,
            scheduled_date=future_date,
            scheduled_time=time(11, 0),
            chief_complaint='Eczema'
        )
        with self.assertRaises(ValidationError):
            appt.full_clean()

    def test_double_booking_prevention_constraint(self):
        future_date = timezone.now().date() + timedelta(days=5)
        slot_time = time(14, 30)

        # Create first appointment
        Appointment.objects.create(
            child=self.child,
            parent=self.parent,
            doctor=self.doctor,
            scheduled_date=future_date,
            scheduled_time=slot_time,
            chief_complaint='Rash 1'
        )

        # Attempt to double-book same doctor at same date and time
        with self.assertRaises(IntegrityError):
            Appointment.objects.create(
                child=self.child,
                parent=self.parent,
                doctor=self.doctor,
                scheduled_date=future_date,
                scheduled_time=slot_time,
                chief_complaint='Rash 2'
            )

    def test_upcoming_queryset_filter(self):
        future_date = timezone.now().date() + timedelta(days=4)
        Appointment.objects.create(
            child=self.child,
            parent=self.parent,
            doctor=self.doctor,
            scheduled_date=future_date,
            scheduled_time=time(9, 0),
            status=Appointment.Status.CONFIRMED,
            chief_complaint='Followup'
        )
        self.assertEqual(Appointment.objects.upcoming().count(), 1)

    def test_doctor_status_transition(self):
        future_date = timezone.now().date() + timedelta(days=4)
        appt = Appointment.objects.create(
            child=self.child,
            parent=self.parent,
            doctor=self.doctor,
            scheduled_date=future_date,
            scheduled_time=time(15, 0),
            status=Appointment.Status.PENDING,
            chief_complaint='Eczema'
        )
        self.client.force_login(self.doctor)
        res = self.client.post(
            reverse('appointments:appointment_status_update', kwargs={'pk': appt.pk}),
            {'status': Appointment.Status.CONFIRMED}
        )
        self.assertEqual(res.status_code, 302)
        appt.refresh_from_db()
        self.assertEqual(appt.status, Appointment.Status.CONFIRMED)
