import json
import time

from django.contrib.auth import get_user_model
from django.core.signing import Signer
from django.test import TestCase
from django.urls import reverse

from .models import BusinessArea, Mission, TestDetail


class OrderMissionTestsViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123',
        )
        self.client.login(username='testuser', password='password123')

        self.business_area = BusinessArea.objects.create(name='Operations')
        self.mission = Mission.objects.create(
            mission_name='Test Mission',
            mission_number='001',
            business_area=self.business_area,
        )

        self.test_a = TestDetail.objects.create(
            mission=self.mission,
            test_number=1,
            test_objective='Test objective A',
            attack_phase='RECON',
        )
        self.test_b = TestDetail.objects.create(
            mission=self.mission,
            test_number=2,
            test_objective='Test objective B',
            attack_phase='RECON',
        )

    def test_reorder_updates_mission_sort_order(self):
        signed_timestamp = Signer().sign(time.time())
        payload = {
            'server_timestamp': signed_timestamp,
            'order': [str(self.test_b.id), str(self.test_a.id)],
        }

        response = self.client.post(
            reverse('mission-tests-reorder', kwargs={'mission': self.mission.id}),
            data=json.dumps(payload),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)

        self.mission.refresh_from_db()
        self.assertEqual(self.mission.testdetail_sort_order, f'[{self.test_b.id}, {self.test_a.id}]')

    def test_reorder_rejects_invalid_order_items(self):
        signed_timestamp = Signer().sign(time.time())
        payload = {
            'server_timestamp': signed_timestamp,
            'order': [str(self.test_b.id), 'invalid-id'],
        }

        response = self.client.post(
            reverse('mission-tests-reorder', kwargs={'mission': self.mission.id}),
            data=json.dumps(payload),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('Order items must be integers', response.json().get('error', ''))
