from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import ActivityEvidence, Citizen, CitizenFeedback, Login, Officers, activities


class LoginViewTests(TestCase):
	def setUp(self):
		self.user = Login.objects.create_user(
			username='citizen@example.com',
			password='Valid-password-123',
			usertype='citizen',
		)

	def test_valid_email_and_password_log_in_citizen(self):
		response = self.client.post(reverse('login'), {
			'email': 'citizen@example.com',
			'password': 'Valid-password-123',
		})

		self.assertRedirects(response, reverse('citizenhome'))
		self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

	def test_invalid_password_shows_error(self):
		response = self.client.post(reverse('login'), {
			'email': 'citizen@example.com',
			'password': 'wrong-password',
		})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Invalid username or password')

	def test_duplicate_email_is_rejected_during_citizen_registration(self):
		response = self.client.post(reverse('citizen_registration'), {
			'email': 'citizen@example.com',
		})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'An account with this email already exists.')
		self.assertEqual(Login.objects.count(), 1)

	def test_duplicate_email_is_rejected_when_adding_officer(self):
		response = self.client.post(reverse('add_officer'), {
			'email': 'citizen@example.com',
		})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'An account with this email already exists.')
		self.assertEqual(Login.objects.count(), 1)


class CitizenProfileViewTests(TestCase):
	def setUp(self):
		self.user = Login.objects.create_user(
			username='profile@example.com',
			password='Valid-password-123',
			usertype='citizen',
		)
		self.citizen = Citizen.objects.create(
			user=self.user,
			name='Test Citizen',
			email='profile@example.com',
			mobile='1234567890',
			address='1 Test Street',
			city='Test City',
			state='Test State',
			pincode='123456',
			proof='citizen_proofs/proof.pdf',
			aadhar='123456789012',
			profile_pic='citizen_profile_pics/profile.jpg',
		)
		self.client.force_login(self.user)

	def test_dashboard_renders_link_to_citizen_profile(self):
		response = self.client.get(reverse('citizenhome'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(
			response,
			reverse('view_citizen_profile'),
		)
		self.assertContains(response, reverse('citizen_view_officer_activity'))
		self.assertContains(response, 'Officer Activities')
		self.assertContains(response, '<h3>Officer Activities</h3>', html=True)

	def test_citizen_profile_route_renders_profile_page(self):
		response = self.client.get(
			reverse('view_citizen_profile', args=[self.citizen.pk])
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Citizen Profile')

	def test_citizen_profile_route_without_id_uses_logged_in_citizen(self):
		response = self.client.get(reverse('view_citizen_profile'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Citizen Profile')

	def test_citizen_profile_route_without_id_redirects_anonymous_user(self):
		self.client.logout()

		response = self.client.get(reverse('view_citizen_profile'))

		self.assertRedirects(response, reverse('login'))


class OfficerProfileViewTests(TestCase):
	def setUp(self):
		self.user = Login.objects.create_user(
			username='officer@example.com',
			password='Valid-password-123',
			usertype='officer',
		)
		self.officer = Officers.objects.create(
			user=self.user,
			name='Test Officer',
			email='officer@example.com',
			mobile='1234567890',
			address='1 Public Service Road',
			department='Community Services',
			district='Central District',
			state='Test State',
		)
		self.client.force_login(self.user)

	def test_dashboard_links_to_full_officer_profile(self):
		response = self.client.get(reverse('officerhome'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(
			response,
			reverse('view_officer_profile', args=[self.officer.pk]),
		)

	def test_profile_link_displays_officer_profile(self):
		response = self.client.get(
			reverse('view_officer_profile', args=[self.officer.pk])
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Professional information')
		self.assertContains(response, 'Test Officer')

	def test_officer_cannot_view_another_officers_profile(self):
		other_user = Login.objects.create_user(
			username='other-officer@example.com',
			password='Valid-password-123',
			usertype='officer',
		)
		other_officer = Officers.objects.create(
			user=other_user,
			name='Other Officer',
			email='other-officer@example.com',
			mobile='0987654321',
			address='2 Public Service Road',
			department='Public Works',
			district='North District',
			state='Test State',
		)

		response = self.client.get(
			reverse('view_officer_profile', args=[other_officer.pk])
		)

		self.assertEqual(response.status_code, 403)


class ActivityDurationValidationTests(TestCase):
	def setUp(self):
		self.user = Login.objects.create_user(
			username='activity-officer@example.com',
			password='Valid-password-123',
			usertype='officer',
		)
		self.officer = Officers.objects.create(
			user=self.user,
			name='Session Officer',
			email='activity-officer@example.com',
			mobile='1234567890',
			address='1 Public Service Road',
			department='Community Services',
			district='Central District',
			state='Test State',
		)
		self.client.force_login(self.user)

	def test_missing_duration_redirects_without_database_error(self):
		response = self.client.post(reverse('add_officer_activity'), {
			'reference_number': 'ACT-001',
		})

		self.assertRedirects(response, reverse('add_officer_activity'))
		self.assertEqual(activities.objects.count(), 0)

	def test_activity_report_is_saved_for_officer_in_login_session(self):
		response = self.client.post(reverse('add_officer_activity'), {
			'reference_number': 'ACT-SESSION-001',
			'duration': '02:30:00',
			'title': 'Road repair',
			'activity_type': 'infrastructure',
			'location': 'Central Ward',
			'status': 'completed',
			'before_description': 'Road surface was damaged.',
			'after_description': 'Road surface was repaired.',
			'action_taken': 'Repaired the main road.',
		})

		self.assertRedirects(response, reverse('view_officeractivity'), fetch_redirect_response=False)
		activity = activities.objects.get(reference_number='ACT-SESSION-001')
		self.assertEqual(activity.user, self.user)
		self.assertEqual(activity.department, self.officer.department)
		self.assertEqual(activity.name_of_activity, 'Road repair')
		self.assertEqual(activity.before_description, 'Road surface was damaged.')
		self.assertEqual(activity.after_description, 'Road surface was repaired.')

	def test_activity_submission_stores_every_before_and_after_image(self):
		response = self.client.post(
			reverse('add_officer_activity'),
			{
				'reference_number': 'ACT-IMAGES-001',
				'duration': '00:45:00',
				'title': 'Park improvement',
				'location': 'Central Ward',
				'before_images': [
					SimpleUploadedFile('before-one.jpg', b'before-one', content_type='image/jpeg'),
					SimpleUploadedFile('before-two.jpg', b'before-two', content_type='image/jpeg'),
				],
				'after_images': [
					SimpleUploadedFile('after-one.jpg', b'after-one', content_type='image/jpeg'),
					SimpleUploadedFile('after-two.jpg', b'after-two', content_type='image/jpeg'),
				],
			},
		)

		self.assertEqual(response.status_code, 302)
		activity = activities.objects.get(reference_number='ACT-IMAGES-001')
		self.assertEqual(activity.evidence_images.count(), 4)
		self.assertEqual(
			activity.evidence_images.filter(stage=ActivityEvidence.BEFORE).count(),
			2,
		)
		self.assertEqual(
			activity.evidence_images.filter(stage=ActivityEvidence.AFTER).count(),
			2,
		)
		list_response = self.client.get(reverse('view_officeractivity'))
		self.assertContains(list_response, 'before-one_')
		self.assertContains(list_response, 'before-two_')
		self.assertContains(list_response, 'after-one_')
		self.assertContains(list_response, 'after-two_')


class MyOfficerActivitiesViewTests(TestCase):
	def setUp(self):
		self.user = Login.objects.create_user(
			username='my-activities@example.com',
			password='Valid-password-123',
			usertype='officer',
		)
		self.officer = Officers.objects.create(
			user=self.user,
			name='Activities Officer',
			email='my-activities@example.com',
			mobile='1234567890',
			address='1 Public Service Road',
			department='Community Services',
			district='Central District',
			state='Test State',
		)
		self.activity = activities.objects.create(
			user=self.user,
			reference_number='ACT-MY-001',
			duration=timedelta(hours=1, minutes=30),
			name_of_activity='Community clean-up',
			department=self.officer.department,
			village='Central Ward',
			taluk='',
			district=self.officer.district,
			state=self.officer.state,
			pincode='123456',
			description='Removed waste from the public park.',
			image='',
			map_location='Central Ward',
		)
		self.client.force_login(self.user)

	def test_dashboard_links_to_my_activities(self):
		response = self.client.get(reverse('officerhome'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, reverse('view_officeractivity'))

	def test_activity_list_is_scoped_to_the_session_officer(self):
		other_user = Login.objects.create_user(
			username='another-officer@example.com',
			password='Valid-password-123',
			usertype='officer',
		)
		activities.objects.create(
			user=other_user,
			reference_number='ACT-OTHER-001',
			duration=timedelta(minutes=30),
			name_of_activity='Other officer report',
			department='Public Works',
			village='North Ward',
			taluk='',
			district='North District',
			state='Test State',
			pincode='654321',
			description='A separate report.',
			image='',
			map_location='North Ward',
		)

		response = self.client.get(reverse('view_officeractivity'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(list(response.context['my_activities']), [self.activity])
		self.assertEqual(response.context['total_activities'], 1)
		self.assertContains(response, 'Community clean-up')
		self.assertContains(response, 'ACT-MY-001')
		self.assertContains(response, 'Details')
		self.assertContains(response, 'Edit Activity')
		self.assertContains(response, 'Edit Before / After Evidence')
		self.assertContains(response, 'Delete Activity')

	def test_activity_list_requires_login(self):
		self.client.logout()

		response = self.client.get(reverse('view_officeractivity'))

		self.assertRedirects(
			response,
			f'{reverse("login")}?next={reverse("view_officeractivity")}',
		)

	def test_officer_can_edit_own_activity(self):
		page = self.client.get(
			reverse('edit_officeractivity', args=[self.activity.pk]),
		)

		self.assertEqual(page.status_code, 200)
		self.assertContains(page, 'Edit Activity')
		self.assertContains(page, 'Community clean-up')
		self.assertContains(page, 'Before the activity')
		self.assertContains(page, 'After the activity')

		response = self.client.post(
			reverse('edit_officeractivity', args=[self.activity.pk]),
			{
				'name_of_activity': 'Updated community clean-up',
				'reference_number': 'ACT-MY-002',
				'duration': '02:00:00',
				'location': 'South Ward',
				'description': 'Updated report details.',
				'before_description': 'Old road surface.',
				'after_description': 'Road resurfaced.',
			},
		)

		self.assertRedirects(response, reverse('view_officeractivity'))
		self.activity.refresh_from_db()
		self.assertEqual(self.activity.name_of_activity, 'Updated community clean-up')
		self.assertEqual(self.activity.reference_number, 'ACT-MY-002')
		self.assertEqual(self.activity.map_location, 'South Ward')
		self.assertEqual(self.activity.before_description, 'Old road surface.')
		self.assertEqual(self.activity.after_description, 'Road resurfaced.')

	def test_before_after_can_be_edited_from_activity_list(self):
		response = self.client.post(
			reverse('edit_officeractivity', args=[self.activity.pk]),
			{
				'before_description': 'Before detail from activity list.',
				'after_description': 'After detail from activity list.',
			},
		)

		self.assertRedirects(response, reverse('view_officeractivity'))
		self.activity.refresh_from_db()
		self.assertEqual(self.activity.before_description, 'Before detail from activity list.')
		self.assertEqual(self.activity.after_description, 'After detail from activity list.')
		self.assertEqual(self.activity.name_of_activity, 'Community clean-up')

	def test_officer_can_delete_own_activity(self):
		response = self.client.post(
			reverse('delete_officeractivity', args=[self.activity.pk]),
		)

		self.assertRedirects(response, reverse('view_officeractivity'))
		self.assertFalse(activities.objects.filter(pk=self.activity.pk).exists())

	def test_officer_cannot_edit_another_officers_activity(self):
		other_user = Login.objects.create_user(
			username='another-activity-officer@example.com',
			password='Valid-password-123',
			usertype='officer',
		)
		other_activity = activities.objects.create(
			user=other_user,
			reference_number='ACT-OTHER-002',
			duration=timedelta(minutes=30),
			name_of_activity='Other officer report',
			department='Public Works',
			village='North Ward',
			taluk='',
			district='North District',
			state='Test State',
			pincode='654321',
			description='A separate report.',
			image='',
			map_location='North Ward',
		)

		response = self.client.post(
			reverse('edit_officeractivity', args=[other_activity.pk]),
			{
				'name_of_activity': 'Changed by another officer',
				'reference_number': 'ACT-OTHER-002',
				'duration': '00:30:00',
			},
		)

		self.assertEqual(response.status_code, 404)

	def test_officer_cannot_delete_another_officers_activity(self):
		other_user = Login.objects.create_user(
			username='another-delete-officer@example.com',
			password='Valid-password-123',
			usertype='officer',
		)
		other_activity = activities.objects.create(
			user=other_user,
			reference_number='ACT-OTHER-DELETE',
			duration=timedelta(minutes=30),
			name_of_activity='Other officer report',
			department='Public Works',
			village='North Ward',
			taluk='',
			district='North District',
			state='Test State',
			pincode='654321',
			description='A separate report.',
			image='',
			map_location='North Ward',
		)

		response = self.client.post(
			reverse('delete_officeractivity', args=[other_activity.pk]),
		)

		self.assertEqual(response.status_code, 404)
		self.assertTrue(activities.objects.filter(pk=other_activity.pk).exists())


class PublicOfficerActivitiesViewTests(TestCase):
	def test_public_officer_activities_page_is_read_only(self):
		user = Login.objects.create_user(
			username='public-officer@example.com',
			password='Valid-password-123',
			usertype='officer',
		)
		activities.objects.create(
			user=user,
			reference_number='ACT-PUBLIC-001',
			duration=timedelta(minutes=45),
			name_of_activity='Public park improvement',
			department='Community Services',
			village='Central Ward',
			taluk='',
			district='Central District',
			state='Test State',
			pincode='123456',
			description='Improved the public park.',
			image='',
			map_location='Central Ward',
		)

		response = self.client.get(reverse('citizen_view_officer_activity'))

		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'officer/view_officeractivity.html')
		self.assertContains(response, 'Officer Activities')
		self.assertNotContains(response, reverse('citizen_feedback'))
		self.assertContains(response, 'Public park improvement')
		self.assertNotContains(response, 'Edit Before / After Evidence')
		self.assertNotContains(response, 'Delete Activity')

	def test_admin_activity_route_uses_admin_dashboard_shell(self):
		admin = Login.objects.create_user(
			username='activity-admin@example.com',
			password='Valid-password-123',
			usertype='admin',
		)
		self.client.force_login(admin)

		response = self.client.get(reverse('citizen_view_officer_activity'))

		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'admin/common.html')
		self.assertContains(response, 'View Citizens')
		self.assertContains(response, 'View Officer Activities')

	def test_citizen_activity_route_uses_citizen_dashboard_shell(self):
		citizen = Login.objects.create_user(
			username='activity-citizen@example.com',
			password='Valid-password-123',
			usertype='citizen',
		)
		Citizen.objects.create(
			user=citizen,
			name='Activity Reviewer',
			email='activity-citizen@example.com',
			mobile='1234567890',
			address='1 Citizen Street',
			city='Central City',
			state='Test State',
			pincode='123456',
			proof='',
			aadhar='123456789012',
			profile_pic='',
		)
		report = activities.objects.create(
			user=Login.objects.create_user(
				username='reported-officer@example.com',
				password='Valid-password-123',
				usertype='officer',
			),
			reference_number='ACT-FEEDBACK-001',
			duration=timedelta(minutes=30),
			name_of_activity='Citizen-visible activity',
			department='Community Services',
			village='Central Ward',
			taluk='',
			district='Central District',
			state='Test State',
			pincode='123456',
			description='Activity for feedback testing.',
			image='',
			map_location='Central Ward',
		)
		self.client.force_login(citizen)

		response = self.client.get(reverse('citizen_view_officer_activity'))

		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'citizen/view_officeractivity.html')
		self.assertContains(response, 'Officer Activities')
		self.assertContains(response, 'View details')
		self.assertContains(
			response,
			f'{reverse("citizen_feedback")}?activity_id={report.pk}',
		)
		self.assertContains(response, 'Edit Activity')
		self.assertContains(response, 'Delete Activity')

		edit_page = self.client.get(reverse('edit_officeractivity', args=[report.pk]))
		self.assertEqual(edit_page.status_code, 200)
		self.assertTemplateUsed(edit_page, 'citizen/common.html')
		self.assertContains(edit_page, reverse('citizen_view_officer_activity'))

		edit_response = self.client.post(
			reverse('edit_officeractivity', args=[report.pk]),
			{
				'name_of_activity': 'Updated citizen-visible activity',
				'reference_number': report.reference_number,
				'duration': '00:30:00',
			},
		)
		self.assertRedirects(edit_response, reverse('citizen_view_officer_activity'))
		report.refresh_from_db()
		self.assertEqual(report.name_of_activity, 'Updated citizen-visible activity')

		delete_response = self.client.post(
			reverse('delete_officeractivity', args=[report.pk]),
		)
		self.assertRedirects(delete_response, reverse('citizen_view_officer_activity'))
		self.assertFalse(activities.objects.filter(pk=report.pk).exists())

	def test_feedback_submission_is_saved_for_selected_activity(self):
		citizen_user = Login.objects.create_user(
			username='feedback-citizen@example.com',
			password='Valid-password-123',
			usertype='citizen',
		)
		citizen = Citizen.objects.create(
			user=citizen_user,
			name='Feedback Citizen',
			email='feedback-citizen@example.com',
			mobile='1234567890',
			address='1 Citizen Street',
			city='Central City',
			state='Test State',
			pincode='123456',
			proof='',
			aadhar='123456789012',
			profile_pic='',
		)
		report = activities.objects.create(
			user=Login.objects.create_user(
				username='feedback-officer@example.com',
				password='Valid-password-123',
				usertype='officer',
			),
			reference_number='ACT-FEEDBACK-POST',
			duration=timedelta(minutes=30),
			name_of_activity='Road repair',
			department='Public Works',
			village='Central Ward',
			taluk='',
			district='Central District',
			state='Test State',
			pincode='123456',
			description='Road was repaired.',
			image='',
			map_location='Central Ward',
		)
		self.client.force_login(citizen_user)

		feedback_url = f'{reverse("citizen_feedback")}?activity_id={report.pk}'
		page = self.client.get(feedback_url)
		self.assertEqual(page.status_code, 200)
		self.assertEqual(page.context['activity'], report)

		response = self.client.post(reverse('citizen_feedback'), {
			'activity_id': report.pk,
			'name': citizen.name,
			'email': citizen.email,
			'message': 'The repair was completed.',
			'feedback_text': 'The road is safer and easier to use.',
			'rating': '5',
			'improvement_suggestions': 'Add a crosswalk.',
		})

		self.assertRedirects(response, reverse('citizen_view_officer_activity'))
		feedback = CitizenFeedback.objects.get(citizen=citizen, activity=report)
		self.assertEqual(feedback.rating, 5)
		self.assertEqual(feedback.feedback_text, 'The road is safer and easier to use.')


class AdminOfficerManagementTests(TestCase):
	def setUp(self):
		self.admin = Login.objects.create_user(
			username='admin@example.com',
			password='Valid-password-123',
			usertype='admin',
		)
		self.officer_user = Login.objects.create_user(
			username='managed-officer@example.com',
			email='managed-officer@example.com',
			password='Valid-password-123',
			usertype='officer',
		)
		self.officer = Officers.objects.create(
			user=self.officer_user,
			name='Managed Officer',
			email='managed-officer@example.com',
			mobile='1234567890',
			address='1 Office Road',
			department='Community Services',
			district='Central District',
			state='Test State',
		)
		self.client.force_login(self.admin)

	def test_admin_dashboard_links_to_officer_activities(self):
		response = self.client.get(reverse('adminhome'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, reverse('citizen_view_officer_activity'))
		self.assertContains(response, 'Officer Activities')

	def test_admin_can_open_and_update_officer_edit_page(self):
		directory = self.client.get(reverse('view_officer'))
		self.assertEqual(directory.status_code, 200)
		self.assertContains(directory, reverse('edit_officer', args=[self.officer.pk]))
		self.assertContains(directory, reverse('delete_officer', args=[self.officer.pk]))

		url = reverse('edit_officer', args=[self.officer.pk])
		page = self.client.get(url)

		self.assertEqual(page.status_code, 200)
		self.assertTemplateUsed(page, 'admin/edit_officer.html')
		self.assertContains(page, 'Managed Officer')

		response = self.client.post(url, {
			'name': 'Updated Officer',
			'email': 'updated-officer@example.com',
			'mobile': '0987654321',
			'address': '2 Office Road',
			'department': 'Public Works',
			'district': 'North District',
			'state': 'New State',
		})

		self.assertRedirects(response, reverse('view_officer'))
		self.officer.refresh_from_db()
		self.officer_user.refresh_from_db()
		self.assertEqual(self.officer.name, 'Updated Officer')
		self.assertEqual(self.officer.email, 'updated-officer@example.com')
		self.assertEqual(self.officer_user.username, 'updated-officer@example.com')
		self.assertEqual(self.officer.department, 'Public Works')

	def test_admin_can_delete_officer_and_linked_account(self):
		response = self.client.post(reverse('delete_officer', args=[self.officer.pk]))

		self.assertRedirects(response, reverse('view_officer'))
		self.assertFalse(Officers.objects.filter(pk=self.officer.pk).exists())
		self.assertFalse(Login.objects.filter(pk=self.officer_user.pk).exists())

	def test_non_admin_cannot_edit_or_delete_officer(self):
		citizen = Login.objects.create_user(
			username='citizen-management-test@example.com',
			password='Valid-password-123',
			usertype='citizen',
		)
		self.client.force_login(citizen)

		edit_response = self.client.get(reverse('edit_officer', args=[self.officer.pk]))
		delete_response = self.client.post(reverse('delete_officer', args=[self.officer.pk]))

		self.assertEqual(edit_response.status_code, 403)
		self.assertEqual(delete_response.status_code, 403)
		self.assertTrue(Officers.objects.filter(pk=self.officer.pk).exists())

	def test_delete_officer_rejects_get(self):
		response = self.client.get(reverse('delete_officer', args=[self.officer.pk]))

		self.assertEqual(response.status_code, 405)


	def setUp(self):
		self.admin = Login.objects.create_user(
			username='citizen-admin@example.com',
			password='Valid-password-123',
			usertype='admin',
		)
		self.citizen_user = Login.objects.create_user(
			username='managed-citizen@example.com',
			email='managed-citizen@example.com',
			password='Valid-password-123',
			usertype='citizen',
		)
		self.citizen = Citizen.objects.create(
			user=self.citizen_user,
			name='Managed Citizen',
			email='managed-citizen@example.com',
			mobile='1234567890',
			address='1 Citizen Street',
			city='Central City',
			state='Test State',
			pincode='123456',
			proof='',
			aadhar='123456789012',
			profile_pic='',
		)
		self.client.force_login(self.admin)

	def test_citizen_directory_displays_uploaded_profile_photo_and_proof(self):
		self.citizen.profile_pic = 'citizen_profile_pics/managed-citizen.jpg'
		self.citizen.proof = 'citizen_proofs/identity-proof.pdf'
		self.citizen.save(update_fields=['profile_pic', 'proof'])

		response = self.client.get(reverse('view_citizen'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(
			response,
			'src="/media/citizen_profile_pics/managed-citizen.jpg"',
		)
		self.assertContains(
			response,
			'href="/media/citizen_proofs/identity-proof.pdf"',
		)

	def test_admin_can_open_and_update_citizen_edit_page(self):
		directory = self.client.get(reverse('view_citizen'))
		self.assertEqual(directory.status_code, 200)
		self.assertContains(directory, reverse('edit_citizen', args=[self.citizen.pk]))
		self.assertContains(directory, reverse('delete_citizen', args=[self.citizen.pk]))

		url = reverse('edit_citizen', args=[self.citizen.pk])
		page = self.client.get(url)
		self.assertEqual(page.status_code, 200)
		self.assertTemplateUsed(page, 'admin/edit_citizen.html')
		self.assertContains(page, 'Managed Citizen')

		response = self.client.post(url, {
			'name': 'Updated Citizen',
			'email': 'updated-citizen@example.com',
			'mobile': '0987654321',
			'address': '2 Citizen Street',
			'city': 'North City',
			'state': 'New State',
			'pincode': '654321',
			'aadhar': '210987654321',
		})

		self.assertRedirects(response, reverse('view_citizen'))
		self.citizen.refresh_from_db()
		self.citizen_user.refresh_from_db()
		self.assertEqual(self.citizen.name, 'Updated Citizen')
		self.assertEqual(self.citizen.email, 'updated-citizen@example.com')
		self.assertEqual(self.citizen_user.username, 'updated-citizen@example.com')
		self.assertEqual(self.citizen.city, 'North City')

	def test_admin_can_delete_citizen_and_linked_account(self):
		response = self.client.post(reverse('delete_citizen', args=[self.citizen.pk]))

		self.assertRedirects(response, reverse('view_citizen'))
		self.assertFalse(Citizen.objects.filter(pk=self.citizen.pk).exists())
		self.assertFalse(Login.objects.filter(pk=self.citizen_user.pk).exists())

	def test_non_admin_cannot_edit_or_delete_citizen(self):
		self.client.force_login(self.citizen_user)
		edit_response = self.client.get(reverse('edit_citizen', args=[self.citizen.pk]))
		delete_response = self.client.post(reverse('delete_citizen', args=[self.citizen.pk]))

		self.assertEqual(edit_response.status_code, 403)
		self.assertEqual(delete_response.status_code, 403)
		self.assertTrue(Citizen.objects.filter(pk=self.citizen.pk).exists())

	def test_delete_citizen_rejects_get(self):
		response = self.client.get(reverse('delete_citizen', args=[self.citizen.pk]))

		self.assertEqual(response.status_code, 405)
