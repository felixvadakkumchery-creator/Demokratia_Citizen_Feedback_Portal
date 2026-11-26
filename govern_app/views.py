from urllib import request

from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.db import IntegrityError, transaction
from django.shortcuts import redirect
from .models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.db.models import Prefetch
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.crypto import get_random_string
from django.utils.dateparse import parse_duration
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.shortcuts import redirect

# Create your views here.
def index(request):
    return render(request,'index.html')
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

from pathlib import Path

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password





import re
from pathlib import Path

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import redirect, render


# First bytes of each allowed file type
FILE_SIGNATURES = {
    '.pdf':  lambda h: h.startswith(b'%PDF-'),
    '.jpg':  lambda h: h.startswith(b'\xff\xd8\xff'),
    '.jpeg': lambda h: h.startswith(b'\xff\xd8\xff'),
    '.png':  lambda h: h.startswith(b'\x89PNG\r\n\x1a\n'),
    '.webp': lambda h: h[:4] == b'RIFF' and h[8:12] == b'WEBP',
}


def check_upload(file, label, allowed, max_mb):
    """Return an error message, or None if the file is fine."""
    if not file:
        return f'Please upload your {label.lower()}.'

    ext = Path(file.name).suffix.lower()

    if ext not in allowed:
        return f'{label} must be one of: {", ".join(allowed)}.'
    if file.size == 0:
        return f'{label} is empty.'
    if file.size > max_mb * 1024 * 1024:
        return f'{label} must not exceed {max_mb} MB.'

    header = file.read(12)
    file.seek(0)
    if not FILE_SIGNATURES[ext](header):
        return f'{label} does not match its file extension.'

    return None

import re
from pathlib import Path

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import redirect, render

from .locations import INDIA_LOCATIONS



def check_file(file, label, allowed, max_mb):
    """Return an error message, or None if the file is fine."""
    if not file:
        return f'Please upload your {label}.'

    ext = Path(file.name).suffix.lower()
    if ext not in allowed:
        return f'{label} must be one of: {", ".join(allowed)}.'
    if file.size == 0:
        return f'{label} is empty.'
    if file.size > max_mb * 1024 * 1024:
        return f'{label} must not exceed {max_mb} MB.'
    return None
import re
from pathlib import Path

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import redirect, render

from .locations import INDIA_LOCATIONS



def check_file(file, label, allowed, max_mb):
    """Return an error message, or None if the file is fine."""
    if not file:
        return f'Please upload your {label}.'

    ext = Path(file.name).suffix.lower()
    if ext not in allowed:
        return f'{label} must be one of: {", ".join(allowed)}.'
    if file.size == 0:
        return f'{label} is empty.'
    if file.size > max_mb * 1024 * 1024:
        return f'{label} must not exceed {max_mb} MB.'
    return None


def citizen_registration(request):

    context = {
        'states': sorted(INDIA_LOCATIONS),
        'locations': INDIA_LOCATIONS,
        'errors': [],
        'data': {},
    }

    if request.method != 'POST':
        return render(request, 'citizen_registration.html', context)

    # ---------- Collect data ----------
    fields = ['name', 'email', 'mobile', 'address', 'city', 'pincode', 'state', 'district']
    data = {f: request.POST.get(f, '').strip() for f in fields}
    data['email'] = data['email'].lower()

    password = request.POST.get('password', '')
    confirm_password = request.POST.get('confirm_password', '')
    aadhar = request.POST.get('aadhar', '').strip()
    proof = request.FILES.get('proof')
    profile_pic = request.FILES.get('profile_pic')

    errors = []

    # ---------- Validate ----------
    if not 2 <= len(data['name']) <= 100:
        errors.append('Name must be between 2 and 100 characters.')
    elif any(ch.isdigit() for ch in data['name']):
        errors.append('Name cannot contain numbers.')

    try:
        validate_email(data['email'])
    except ValidationError:
        errors.append('Please enter a valid email address.')

    if not re.fullmatch(r'[6-9][0-9]{9}', data['mobile']):
        errors.append('Mobile number must be 10 digits and start with 6, 7, 8 or 9.')

    if len(data['address']) < 5:
        errors.append('Please enter your residential address.')

    if not re.fullmatch(r'[1-9][0-9]{5}', data['pincode']):
        errors.append('Please enter a valid 6-digit PIN code.')

    if data['state'] not in INDIA_LOCATIONS:
        errors.append('Please select a valid State.')
    elif data['district'] not in INDIA_LOCATIONS[data['state']]:
        errors.append('Please select a District of the selected State.')

    if not re.fullmatch(r'[0-9]{12}', aadhar):
        errors.append('Aadhaar number must contain exactly 12 digits.')

    if not password:
        errors.append('Please enter a password.')
    else:
        try:
            validate_password(password, user=Login(username=data['email'], email=data['email']))
        except ValidationError as e:
            errors.extend(e.messages)
        if password != confirm_password:
            errors.append('Password and confirm password do not match.')

    if Login.objects.filter(
        Q(username__iexact=data['email']) | Q(email__iexact=data['email'])
    ).exists():
        errors.append('An account with this email already exists.')

    for file, label, allowed, max_mb in (
        (proof, 'Identity proof', ('.pdf', '.jpg', '.jpeg', '.png'), 5),
        (profile_pic, 'Profile picture', ('.jpg', '.jpeg', '.png', '.webp'), 2),
    ):
        problem = check_file(file, label, allowed, max_mb)
        if problem:
            errors.append(problem)

    if errors:
        context.update(errors=errors, data=data)
        return render(request, 'citizen_registration.html', context)

    # ---------- Save ----------
    try:
        with transaction.atomic():
            user = Login.objects.create_user(
                username=data['email'],
                email=data['email'],
                password=password,
                usertype='citizen',
                viewpassword=confirm_password,
            )

            Citizen.objects.create(
                user=user,
                name=data['name'],
                email=data['email'],
                mobile=data['mobile'],
                address=data['address'],
                city=data['city'] or data['district'],
                state=data['state'],
                district=data['district'],
                pincode=data['pincode'],
                proof=proof,
                aadhar=aadhar,
                profile_pic=profile_pic,
            )
        return redirect('login')

    except IntegrityError:
        errors.append('Registration could not be completed. Please try again.')
        context.update(errors=errors, data=data)
        return render(request, 'citizen_registration.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Citizen


@login_required(login_url='login')
def citizenhome(request):

    citizen = Citizen.objects.select_related('user').filter(
        user=request.user
    ).first()

    return render(
        request,
        'citizen/citizenhome.html',
        {
            'citizen': citizen
        }
    )
def adminhome(request):
    return render(request,'admin/adminhome.html')


def view_login(request):
    if request.method=='POST':
        email=request.POST.get('email', '').strip()
        password=request.POST.get('password', '')
        user=authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            if user.usertype=='':
                return redirect('adminhome')
            elif user.usertype=='citizen':
                return redirect('citizenhome')
            elif user.usertype=='officer':
                return redirect('officerhome')
            return render(request, 'login.html', {
                'error': 'Invalid username or password',
                'entered_email': email,
            })
        else:
            return render(request, 'login.html', {
                'error': 'Invalid username or password',
                'entered_email': email,
            })
    else:
        return render(request,'login.html')
def view_citizen(request):
    citizens = Citizen.objects.select_related('user').all()

    return render(request, 'admin/view_citizen.html', {
        'citizens': citizens,
        'total_citizens': citizens.count(),
    })

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


LGD_API_BASE = "https://lgd-json-api.vercel.app/api"


def get_lgd_records(endpoint, **parameters):

    parameters['page'] = 1
    parameters['limit'] = 100

    url = (
        f"{LGD_API_BASE}/{endpoint}?"
        f"{urlencode(parameters)}"
    )

    request = Request(
        url,
        headers={
            'Accept': 'application/json',
            'User-Agent': 'Demokratia.com'
        }
    )

    with urlopen(request, timeout=10) as response:
        result = json.loads(response.read().decode('utf-8'))

    return result.get('data', [])


def validate_officer_location(location):

    state = location.get('state', '').strip()
    district = location.get('district', '').strip()
    taluk = location.get('taluk', '').strip()

    state_code = str(location.get('state_code', '')).strip()
    district_code = str(location.get('district_code', '')).strip()
    taluk_code = str(location.get('taluk_code', '')).strip()

    errors = []

    # -----------------------------------------
    # Required location fields
    # -----------------------------------------

    if not all([
        state,
        district,
        taluk,
        state_code,
        district_code,
        taluk_code
    ]):
        return [
            'Please select a State, District and Taluk.'
        ]

    try:

        # -----------------------------------------
        # Validate State
        # -----------------------------------------

        states = get_lgd_records(
            'states',
            code=state_code
        )

        valid_state = any(
            str(item.get('code', '')) == state_code
            and item.get('name', '').strip().casefold()
                == state.casefold()
            for item in states
        )

        if not valid_state:
            return [
                'Invalid State selection.'
            ]

        # -----------------------------------------
        # Validate District
        # -----------------------------------------

        districts = get_lgd_records(
            'districts',
            stateCode=state_code,
            code=district_code
        )

        valid_district = any(
            str(item.get('code', '')) == district_code
            and str(item.get('stateCode', '')) == state_code
            and item.get('name', '').strip().casefold()
                == district.casefold()
            for item in districts
        )

        if not valid_district:
            return [
                'The selected District does not belong '
                'to the selected State.'
            ]

        # -----------------------------------------
        # Validate Taluk
        # -----------------------------------------

        taluks = get_lgd_records(
            'subdistricts',
            districtCode=district_code,
            code=taluk_code
        )

        valid_taluk = any(
            str(item.get('code', '')) == taluk_code
            and str(item.get('districtCode', '')) == district_code
            and item.get('name', '').strip().casefold()
                == taluk.casefold()
            for item in taluks
        )

        if not valid_taluk:
            return [
                'The selected Taluk does not belong '
                'to the selected District.'
            ]

    except (
        HTTPError,
        URLError,
        TimeoutError,
        OSError,
        ValueError,
        KeyError,
        TypeError
    ):

        return [
            'Unable to verify the State, District and Taluk. '
            'Please check your internet connection and try again.'
        ]

    # -----------------------------------------
    # Validation successful
    # -----------------------------------------

    return []

def add_officer(request):

    # Department options
    departments = [
        'Revenue',
        'Police',
        'Health',
        'Education',
        'Local Self Government',
        'Public Works',
        'Other'
    ]

    # Check existing admin login session
    if not request.user.is_authenticated or request.user.usertype != '':

        return render(request, 'admin/add_officer.html', {
            'errors': ['You are not authorized to add government officers.'],
            'data': {},
            'departments': departments
        })


    # Display registration page
    if request.method != 'POST':

        return render(request, 'admin/add_officer.html', {
            'data': {},
            'departments': departments,
            'errors': []
        })


    # =========================================
    # COLLECT FORM DATA
    # =========================================

    data = {

        'name': request.POST.get('name', '').strip(),

        'email': request.POST.get('email', '').strip(),

        'mobile': request.POST.get('mobile', '').strip(),

        'address': request.POST.get('address', '').strip(),

        'department': request.POST.get('department', '').strip(),

        'state': request.POST.get('state', '').strip(),

        'state_code': request.POST.get('state_code', '').strip(),

        'district': request.POST.get('district', '').strip(),

        'district_code': request.POST.get('district_code', '').strip(),

        'taluk': request.POST.get('taluk', '').strip(),

        'taluk_code': request.POST.get('taluk_code', '').strip(),

    }

    password = request.POST.get('password', '')

    confirm_password = request.POST.get('confirm_password', '')

    errors = []


    # =========================================
    # PERSONAL INFORMATION VALIDATION
    # =========================================

    name = data['name']
    email = data['email']
    mobile = data['mobile']
    address = data['address']
    department = data['department']

    if not name:
        errors.append('Please enter the officer name.')

    elif len(name) > 100:
        errors.append('Officer name cannot exceed 100 characters.')


    # Email validation
    if not email:

        errors.append('Please enter the officer email address.')

    else:

        try:
            validate_email(email)

        except ValidationError:
            errors.append('Please enter a valid email address.')


    # Mobile validation
    if not mobile:

        errors.append('Please enter the mobile number.')

    elif not mobile.isdigit() or len(mobile) != 10:

        errors.append('Mobile number must contain exactly 10 digits.')


    # Address validation
    if not address:

        errors.append('Please enter the office address.')


    # Department validation
    if not department:

        errors.append('Please select a department.')

    elif department not in departments:

        errors.append('Please select a valid department.')


    # =========================================
    # LOCATION VALIDATION
    # =========================================

    location_data = {

        'state': data['state'],

        'state_code': data['state_code'],

        'district': data['district'],

        'district_code': data['district_code'],

        'taluk': data['taluk'],

        'taluk_code': data['taluk_code'],

    }

    location_errors = validate_officer_location(location_data)

    errors.extend(location_errors)


    # =========================================
    # PASSWORD VALIDATION
    # =========================================

    if not password:

        errors.append('Please enter an initial password.')

    elif len(password) < 12:

        errors.append('Password must contain at least 12 characters.')

    else:

        try:

            validate_password(password)

        except ValidationError as e:

            errors.extend(e.messages)


    if not confirm_password:

        errors.append('Please confirm the password.')

    elif password != confirm_password:

        errors.append('Password and confirm password do not match.')


    # =========================================
    # CHECK DUPLICATE EMAIL
    # =========================================

    if email:

        if Login.objects.filter(
            Q(username__iexact=email) |
            Q(email__iexact=email)
        ).exists():

            errors.append(
                'An account with this email address already exists.'
            )


        elif Officers.objects.filter(
            email__iexact=email
        ).exists():

            errors.append(
                'An officer with this email address already exists.'
            )


    # =========================================
    # DISPLAY VALIDATION ERRORS
    # =========================================

    if errors:

        return render(request, 'admin/add_officer.html', {

            'errors': errors,

            'data': data,

            'departments': departments

        })


    # =========================================
    # CREATE OFFICER ACCOUNT
    # =========================================

    try:

        with transaction.atomic():

            # Create Login account
            user = Login(
                username=email,
                email=email,
                usertype='officer',
                viewpassword=''
            )

            # Securely hash password
            user.set_password(password)

            user.save()


            # Create Officer profile
            officer = Officers.objects.create(

                user=user,

                name=name,

                email=email,

                mobile=mobile,

                address=address,

                department=department,

                state=data['state'],

                district=data['district'],

                taluk=data['taluk']

            )


        # Successfully created officer
        return redirect('adminhome')


    except IntegrityError:

        errors.append(
            'Unable to create the officer account because this email '
            'or account already exists.'
        )

        return render(request, 'admin/add_officer.html', {

            'errors': errors,

            'data': data,

            'departments': departments

        })
def view_officer(request):
    officers=Officers.objects.select_related('user').all()

    return render(request, 'admin/view_officer.html', {
        'officers': officers,
        'total_officers': officers.count(),
    })


def _is_admin_user(user):
    return (
        user.is_authenticated
        and (
            user.is_superuser
            or user.is_staff
            or getattr(user, 'usertype', '') == 'admin'
        )
    )


@login_required(login_url='login')
@require_http_methods(['GET', 'POST'])
def edit_citizen(request, citizen_id):
    if not _is_admin_user(request.user):
        return HttpResponseForbidden('You are not authorized to edit citizens.')

    citizen = get_object_or_404(Citizen.objects.select_related('user'), pk=citizen_id)
    data = {
        'name': citizen.name,
        'email': citizen.email,
        'mobile': citizen.mobile,
        'address': citizen.address,
        'city': citizen.city,
        'state': citizen.state,
        'pincode': citizen.pincode,
        'aadhar': citizen.aadhar,
    }
    errors = []

    if request.method == 'POST':
        data = {
            'name': request.POST.get('name', '').strip(),
            'email': request.POST.get('email', '').strip().lower(),
            'mobile': request.POST.get('mobile', '').strip(),
        }
        email_in_use = (
            User.objects
            .filter(email=data['email'])
            .exclude(pk=citizen.pk)
            .exists()
        )
        if email_in_use:
            errors.append('An account with this email already exists.')

        if not errors:
            try:
                with transaction.atomic():
                    citizen.user.username = data['email']
                    citizen.user.email = data['email']
                    citizen.user.save(update_fields=['username', 'email'])
                    for field, value in data.items():
                        setattr(citizen, field, value)
                    if request.FILES.get('proof'):
                        citizen.proof = request.FILES['proof']
                    if request.FILES.get('profile_pic'):
                        citizen.profile_pic = request.FILES['profile_pic']
                    citizen.save()
            except IntegrityError:
                errors.append('This email is already in use by another account.')
            else:
                messages.success(request, f'Citizen record for {citizen.name} was updated.')
                return redirect('view_citizen')

    return render(request, 'admin/edit_citizen.html', {
        'citizen': citizen,
        'data': data,
        'errors': errors,
    })



from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction

@login_required
@require_POST
def delete_citizen(request, citizen_id):

    # Allow only admin users to delete citizen records
    if request.user.usertype != '':
        messages.error(request, 'You are not authorized to delete citizens.')
        return redirect('adminhome')

    # Retrieve the citizen record
    citizen = get_object_or_404(Citizen, id=citizen_id)

    try:
        with transaction.atomic():

            # Check whether the citizen has a linked login account
            linked_user = citizen.user

            if linked_user is not None:
                # Delete the linked account.
                # Django CASCADE will delete the citizen record
                # if the ForeignKey uses on_delete=models.CASCADE.
                linked_user.delete()

            else:
                # Delete only the citizen record if no user is linked
                citizen.delete()

        messages.success(
            request,
            'Citizen record deleted successfully.'
        )

    except Exception as e:
        messages.error(
            request,
            f'Unable to delete citizen record: {str(e)}'
        )

    return redirect('view_citizen')


def edit_officer(request, officer_id):

    # =========================================
    # DEPARTMENT OPTIONS
    # =========================================

    departments = [
        'Revenue',
        'Police',
        'Health',
        'Education',
        'Local Self Government',
        'Public Works',
        'Other'
    ]


    # =========================================
    # ADMIN AUTHORIZATION
    # =========================================

    if not _is_admin_user(request.user):
        return HttpResponseForbidden(
            'You are not authorized to edit officers.'
        )


    # =========================================
    # GET OFFICER RECORD
    # =========================================

    officer = get_object_or_404(
        Officers.objects.select_related('user'),
        pk=officer_id
    )


    # =========================================
    # EXISTING OFFICER INFORMATION
    # =========================================

    data = {

        'name': officer.name,

        'email': officer.email,

        'mobile': officer.mobile,

        'address': officer.address,

        'department': officer.department,

        'state': officer.state,

        'district': officer.district,

        'taluk': officer.taluk,

    }

    errors = []


    # =========================================
    # COLLECT FORM DATA
    # =========================================

    if request.method == 'POST':

        data = {

            'name': request.POST.get('name', '').strip(),

            'email': request.POST.get('email', '').strip().lower(),

            'mobile': request.POST.get('mobile', '').strip(),

            'address': request.POST.get('address', '').strip(),

            'department': request.POST.get('department', '').strip(),

            'state': request.POST.get('state', '').strip(),

            'district': request.POST.get('district', '').strip(),

            'taluk': request.POST.get('taluk', '').strip(),

        }


        # =========================================
        # PERSONAL INFORMATION VALIDATION
        # =========================================

        name = data['name']
        email = data['email']
        mobile = data['mobile']
        address = data['address']
        department = data['department']


        if not name:

            errors.append(
                'Please enter the officer name.'
            )

        elif len(name) > 100:

            errors.append(
                'Officer name cannot exceed 100 characters.'
            )


        # Email validation
        if not email:

            errors.append(
                'Please enter the officer email address.'
            )

        else:

            if len(email) > 254:

                errors.append(
                    'Email address cannot exceed 254 characters.'
                )

            try:

                validate_email(email)

            except ValidationError:

                errors.append(
                    'Please enter a valid email address.'
                )


        # Mobile validation
        if not mobile:

            errors.append(
                'Please enter the mobile number.'
            )

        elif not mobile.isdigit() or len(mobile) != 10:

            errors.append(
                'Mobile number must contain exactly 10 digits.'
            )


        # Address validation
        if not address:

            errors.append(
                'Please enter the office address.'
            )


        # =========================================
        # DEPARTMENT VALIDATION
        # =========================================

        if not department:

            errors.append(
                'Please select a department.'
            )

        elif department not in departments:

            errors.append(
                'Please select a valid department.'
            )


        # =========================================
        # LOCATION VALIDATION
        # =========================================

        if not data['state']:

            errors.append(
                'Please select or enter the state.'
            )

        elif len(data['state']) > 100:

            errors.append(
                'State name cannot exceed 100 characters.'
            )


        if not data['district']:

            errors.append(
                'Please select or enter the district.'
            )

        elif len(data['district']) > 100:

            errors.append(
                'District name cannot exceed 100 characters.'
            )


        if not data['taluk']:

            errors.append(
                'Please select or enter the taluk.'
            )

        elif len(data['taluk']) > 100:

            errors.append(
                'Taluk name cannot exceed 100 characters.'
            )


        # =========================================
        # CHECK DUPLICATE EMAIL
        # =========================================

        if email:

            # Check other login accounts
            username_exists = Login.objects.filter(
                username__iexact=email
            ).exclude(
                pk=officer.user_id
            ).exists()


            # Check other login email addresses
            login_email_exists = Login.objects.filter(
                email__iexact=email
            ).exclude(
                pk=officer.user_id
            ).exists()


            # Check other officer records
            officer_email_exists = Officers.objects.filter(
                email__iexact=email
            ).exclude(
                pk=officer.pk
            ).exists()


            if (
                username_exists
                or login_email_exists
                or officer_email_exists
            ):

                errors.append(
                    'An account with this email already exists.'
                )


        # =========================================
        # DISPLAY VALIDATION ERRORS
        # =========================================

        if not errors:

            try:

                # =========================================
                # UPDATE OFFICER AND LOGIN ACCOUNT
                # =========================================

                with transaction.atomic():

                    # Update linked Login account
                    officer.user.username = email

                    officer.user.email = email

                    officer.user.save(
                        update_fields=[
                            'username',
                            'email'
                        ]
                    )


                    # Update Officer profile
                    officer.name = name

                    officer.email = email

                    officer.mobile = mobile

                    officer.address = address

                    officer.department = department

                    officer.state = data['state']

                    officer.district = data['district']

                    officer.taluk = data['taluk']


                    officer.save(
                        update_fields=[
                            'name',
                            'email',
                            'mobile',
                            'address',
                            'department',
                            'state',
                            'district',
                            'taluk'
                        ]
                    )


            except IntegrityError:

                errors.append(
                    'This email is already in use by another account.'
                )


            else:

                # =========================================
                # SUCCESS MESSAGE
                # =========================================

                messages.success(
                    request,
                    f'Officer record for {officer.name} was updated successfully.'
                )

                return redirect('view_officer')


    # =========================================
    # DISPLAY EDIT OFFICER PAGE
    # =========================================

    return render(
        request,
        'admin/edit_officer.html',
        {
            'officer': officer,
            'data': data,
            'errors': errors,
            'departments': departments,
        }
    )

def delete_officer(request, officer_id):

    # =========================================
    # ADMIN AUTHORIZATION
    # =========================================

    if not request.user.is_authenticated or not _is_admin_user(request.user):

        return HttpResponseForbidden(
            'You are not authorized to delete government officers.'
        )


    # =========================================
    # GET OFFICER RECORD
    # =========================================

    officer = get_object_or_404(
        Officers.objects.select_related('user'),
        pk=officer_id
    )

    officer_name = officer.name
    officer_email = officer.email


    # =========================================
    # DELETE OFFICER AND LOGIN ACCOUNT
    # =========================================

    try:

        with transaction.atomic():

            # Delete the associated login account.
            # The linked officer profile will also be deleted
            # if the ForeignKey uses on_delete=models.CASCADE.

            officer.user.delete()


        # =========================================
        # SUCCESS MESSAGE
        # =========================================

        messages.success(
            request,
            f'Officer account for {officer_name} ({officer_email}) '
            f'was successfully deleted.'
        )

        return redirect('view_officer')


    # =========================================
    # DATABASE ERROR HANDLING
    # =========================================

    except IntegrityError:

        messages.error(
            request,
            f'Unable to delete officer account for {officer_name}. '
            'The account may be associated with other records.'
        )

        return redirect('view_officer')
def officerhome(request):
    officer = get_object_or_404(Officers, user=request.user)
    return render(request, 'officer/officerhome.html', {'officer': officer})
def help(request):
    return render(request, 'help.html')
def privacy(request):
    return render(request, 'privacy.html')
def terms(request):
    return render(request, 'terms.html')


def accessibility(request):
    return render(request, 'accessibility.html')


def contact(request):
    return render(request, 'contact.html')



def logout_view(request):
    return redirect('index')


def view_citizen_profile(request, citizen_id=None):

    # -----------------------------------------
    # VIEW LOGGED-IN CITIZEN'S OWN PROFILE
    # -----------------------------------------
    if citizen_id is None:

        if not request.user.is_authenticated:
            return redirect('login')

        citizen = get_object_or_404(
            Citizen.objects.select_related('user'),
            user=request.user
        )

    # -----------------------------------------
    # VIEW A PARTICULAR CITIZEN PROFILE
    # -----------------------------------------
    else:

        try:
            citizen = Citizen.objects.select_related('user').get(
                id=citizen_id
            )

        except Citizen.DoesNotExist:
            return render(request, 'error.html', {
                'message': 'Citizen not found.'
            })

    # -----------------------------------------
    # PROFILE CONTEXT
    # -----------------------------------------
    context = {
        'citizen': citizen,
    }

    return render(
        request,
        'citizen/view_citizen_profile.html',
        context
    )
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden

def view_officer_profile(request, officer_id):

    # =========================================
    # CHECK LOGIN SESSION
    # =========================================

    if not request.user.is_authenticated:
        return HttpResponseForbidden(
            'Please log in to access this officer profile.'
        )

    # =========================================
    # CHECK ADMIN PERMISSION
    # =========================================

    is_admin = (
        request.user.is_superuser
        or request.user.is_staff
        or getattr(request.user, 'usertype', '') in ('', 'admin')
    )

    # =========================================
    # GET OFFICER INFORMATION
    # =========================================

    officer = get_object_or_404(
        Officers.objects.select_related('user'),
        pk=officer_id
    )

    # =========================================
    # CHECK OFFICER PROFILE OWNERSHIP
    # =========================================

    is_own_profile = (
        officer.user_id == request.user.id
    )

    # Administrators can view every officer.
    # Officers can view only their own profile.

    if not is_admin and not is_own_profile:
        return HttpResponseForbidden(
            'You are not authorized to view this officer profile.'
        )

    # =========================================
    # DISPLAY OFFICER PROFILE
    # =========================================

    return render(
        request,
        'officer/view_officer_profile.html',
        {
            'officer': officer,
            'is_admin': is_admin,
            'is_own_profile': is_own_profile,
        }
    )
def view_officer_activity(request):
    activities_list = activities.objects.select_related('user').prefetch_related(
        Prefetch(
            'evidence_images',
            queryset=ActivityEvidence.objects.filter(stage=ActivityEvidence.BEFORE),
            to_attr='before_photos',
        ),
        Prefetch(
            'evidence_images',
            queryset=ActivityEvidence.objects.filter(stage=ActivityEvidence.AFTER),
            to_attr='after_photos',
        ),
    ).order_by('-timestamp')
    context = {
        'my_activities': activities_list,
        'total_activities': activities_list.count(),
        'public_view': True,
        'can_manage_activities': _is_admin_user(request.user)
        or getattr(request.user, 'usertype', '') == 'citizen',
    }
    if request.user.is_authenticated and getattr(request.user, 'usertype', '') == 'citizen':
        context['citizen'] = get_object_or_404(Citizen, user=request.user)
        return render(request, 'citizen/view_officeractivity.html', context)

    context['base_template'] = (
        'admin/common.html' if _is_admin_user(request.user) else 'common.html'
    )
    return render(request, 'officer/view_officeractivity.html', context)
@login_required
def add_officer_activity(request):
    officer = get_object_or_404(Officers, user=request.user)

    if request.method == 'POST':
        reference_number = request.POST.get('reference_number', '').strip()
        duration_value = request.POST.get('duration', '').strip()
        duration = parse_duration(duration_value)
        if not duration_value or duration is None:
            messages.error(request, 'Enter a valid activity duration in HH:MM:SS format.')
            return redirect('add_officer_activity')

        location = request.POST.get('location', '').strip()
        name_of_activity = (
            request.POST.get('name_of_activity')
            or request.POST.get('title', '')
        ).strip()
        report_details = [
            ('Category', request.POST.get('activity_type', '').strip()),
            ('Status', request.POST.get('status', '').strip()),
            ('Before', request.POST.get('before_description', '').strip()),
            ('After', request.POST.get('after_description', '').strip()),
            ('Action taken', request.POST.get('action_taken', '').strip()),
            ('Citizen impact', request.POST.get('citizen_impact', '').strip()),
        ]
        before_description = request.POST.get('before_description', '').strip()
        after_description = request.POST.get('after_description', '').strip()
        description = '\n\n'.join(
            f'{label}: {value}' for label, value in report_details if value
        )
        before_images = request.FILES.getlist('before_images')
        after_images = request.FILES.getlist('after_images')
        before_image = before_images[0] if before_images else ''
        after_image = after_images[0] if after_images else ''
        evidence = (
            request.FILES.get('image')
            or before_image
            or after_image
        )

        activity = activities.objects.create(
            user=request.user,
            reference_number=reference_number,
            duration=duration,
            name_of_activity=name_of_activity,
            department=officer.department,
            village=request.POST.get('village', '').strip() or location,
            taluk=request.POST.get('taluk', '').strip(),
            district=request.POST.get('district', '').strip() or officer.district,
            state=request.POST.get('state', '').strip() or officer.state,
            pincode=request.POST.get('pincode', '').strip(),
            description=description,
            image=evidence,
            before_description=before_description,
            before_image=before_image,
            after_description=after_description,
            after_image=after_image,
            map_location=request.POST.get('map_location', '').strip() or location,
        )
        for image in before_images:
            ActivityEvidence.objects.create(
                activity=activity,
                stage=ActivityEvidence.BEFORE,
                image=image,
            )
        for image in after_images:
            ActivityEvidence.objects.create(
                activity=activity,
                stage=ActivityEvidence.AFTER,
                image=image,
            )

        return redirect('view_officeractivity')

    return render(request, 'officer/add_officer_activity.html', {'officer': officer})
@login_required(login_url='login')
def view_officeractivity(request):
    officer = get_object_or_404(Officers, user=request.user)
    activities_list = activities.objects.filter(user=request.user).prefetch_related(
        Prefetch(
            'evidence_images',
            queryset=ActivityEvidence.objects.filter(stage=ActivityEvidence.BEFORE),
            to_attr='before_photos',
        ),
        Prefetch(
            'evidence_images',
            queryset=ActivityEvidence.objects.filter(stage=ActivityEvidence.AFTER),
            to_attr='after_photos',
        ),
    ).order_by('-timestamp')
    return render(request, 'officer/view_officeractivity.html', {
        'my_activities': activities_list,
        'total_activities': activities_list.count(),
        'officer': officer,
        'base_template': 'officer/common.html',
    })
@login_required(login_url='login')
@require_http_methods(['GET', 'POST'])
def edit_officeractivity(request, activity_id):
    is_admin = _is_admin_user(request.user)
    is_citizen = getattr(request.user, 'usertype', '') == 'citizen'
    activity_query = activities.objects.filter(pk=activity_id)
    if not is_admin and not is_citizen:
        activity_query = activity_query.filter(user=request.user)
    activity = get_object_or_404(activity_query)
    return_view = (
        'view_officeractivity'
        if not is_admin and not is_citizen
        else 'citizen_view_officer_activity'
    )

    if request.method == 'GET':
        base_template = (
            'admin/common.html' if is_admin
            else 'citizen/common.html' if is_citizen
            else 'officer/common.html'
        )
        return render(request, 'officer/edit_officeractivity.html', {
            'activity': activity,
            'base_template': base_template,
            'activity_list_url_name': return_view,
        })

    duration_value = request.POST.get('duration', '').strip()
    duration = (
        parse_duration(duration_value)
        if 'duration' in request.POST
        else activity.duration
    )
    name = request.POST.get('name_of_activity', activity.name_of_activity).strip()
    reference_number = request.POST.get('reference_number', activity.reference_number).strip()

    if duration is None or not name or not reference_number:
        messages.error(request, 'Enter an activity name, reference number, and valid duration.')
        return redirect(return_view)

    location = request.POST.get('location', '').strip()
    activity.name_of_activity = name
    activity.reference_number = reference_number
    activity.duration = duration
    activity.village = request.POST.get('village', activity.village).strip() or location or activity.village
    activity.taluk = request.POST.get('taluk', activity.taluk).strip()
    activity.district = request.POST.get('district', activity.district).strip() or activity.district
    activity.state = request.POST.get('state', activity.state).strip() or activity.state
    activity.pincode = request.POST.get('pincode', activity.pincode).strip() or activity.pincode
    activity.description = request.POST.get('description', activity.description).strip()
    activity.map_location = request.POST.get('map_location', '').strip() or location or activity.map_location
    if request.FILES.get('image'):
        activity.image = request.FILES['image']
    activity.before_description = request.POST.get(
        'before_description', activity.before_description
    ).strip()
    activity.after_description = request.POST.get(
        'after_description', activity.after_description
    ).strip()
    if request.FILES.get('before_image'):
        activity.before_image = request.FILES['before_image']
    if request.FILES.get('after_image'):
        activity.after_image = request.FILES['after_image']
    activity.save()

    messages.success(request, 'Activity report updated.')
    return redirect(return_view)


@login_required(login_url='login')
@require_POST
def delete_officeractivity(request, activity_id):
    is_admin = _is_admin_user(request.user)
    is_citizen = getattr(request.user, 'usertype', '') == 'citizen'
    activity_query = activities.objects.filter(pk=activity_id)
    if not is_admin and not is_citizen:
        activity_query = activity_query.filter(user=request.user)
    activity = get_object_or_404(activity_query)
    activity.delete()
    messages.success(request, 'Activity report deleted.')
    if is_admin or is_citizen:
        return redirect('citizen_view_officer_activity')
    

from django.shortcuts import render, redirect
from django.urls import reverse

from django.shortcuts import render, redirect
from django.urls import reverse




def add_citizen_feedback(request):

    # Get the Citizen linked to the logged-in user
    citizen = None

    if request.user.is_authenticated:
        citizen = Citizen.objects.filter(user=request.user).first()

    # Get activity ID
    activity_id = (
        request.POST.get('activity_id')
        or request.GET.get('activity_id')
    )

    activity = None

    if activity_id and str(activity_id).isdigit():
        activity = activities.objects.filter(id=int(activity_id)).first()

    if not activity:
        return render(request, 'citizen/add_citizen_feedback.html', {
            'citizen': citizen,
            'activity': None,
            'error_message': 'Activity not found. Please select an activity again.'
        })

    if request.method == 'POST':

        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()
        feedback_text = request.POST.get('feedback_text', '').strip()
        rating = request.POST.get('rating')
        image = request.FILES.get('image')
        improvement_suggestions = request.POST.get(
            'improvement_suggestions', ''
        ).strip()

        if not all([name, email, message, feedback_text, rating]):
            return render(request, 'citizen/add_citizen_feedback.html', {
                'citizen': citizen,
                'activity': activity,
                'error_message': 'Please fill in all required fields.'
            })

        try:
            rating = int(rating)
        except (TypeError, ValueError):
            rating = 0

        if rating not in [1, 2, 3, 4, 5]:
            return render(request, 'citizen/add_citizen_feedback.html', {
                'citizen': citizen,
                'activity': activity,
                'error_message': 'Please select a valid rating.'
            })

        # Save feedback linked to the logged-in citizen
        CitizenFeedback.objects.create(
            citizen=citizen,          # saves citizen_id automatically
            name=name,
            email=email,
            message=message,
            feedback_text=feedback_text,
            rating=rating,
            image=image,
            improvement_suggestions=improvement_suggestions or None,
            activity=activity
        )

        request.session['feedback_submitted'] = True

        return redirect(
            f"{reverse('add_citizen_feedback')}?activity_id={activity.id}"
        )

    submitted_successfully = request.session.pop('feedback_submitted', False)

    return render(request, 'citizen/add_citizen_feedback.html', {
        'citizen': citizen,
        'activity': activity,
        'submitted_successfully': submitted_successfully
    })


def view_citizen_feedback(request):

    # Citizen profile of the logged-in user
    citizen = Citizen.objects.filter(user=request.user).first()

    if not citizen:
        return render(request, 'citizen/view_citizen_feedback.html', {
            'feedbacks': [],
            'total_feedback': 0,
            'error_message': 'Please log in using your Citizen account to view your feedback.'
        })

    # Link earlier feedback submitted without a login (same email)
    CitizenFeedback.objects.filter(
        citizen__isnull=True,
        email__iexact=citizen.email
    ).update(citizen=citizen)

    # All feedback given by this citizen, newest first
    feedbacks = (
        CitizenFeedback.objects
        .filter(citizen=citizen)
        .select_related('activity')
        .order_by('-timestamp')
    )

    return render(request, 'citizen/view_citizen_feedback.html', {
        'feedbacks': feedbacks,
        'total_feedback': feedbacks.count(),
    })




def edit_citizen_feedback(request, feedback_id):

    # Get authenticated Django user
    if not request.user.is_authenticated:

        return render(
            request,
            'citizen/edit_citizen_feedback.html',
            {
                'feedback': None,
                'feedback_id': feedback_id,
                'error_message': 'Please log in to edit your feedback.'
            }
        )

    # Retrieve Login account
    login_user = Login.objects.filter(
        id=request.user.id
    ).first()

    if not login_user:

        return render(
            request,
            'citizen/edit_citizen_feedback.html',
            {
                'feedback': None,
                'feedback_id': feedback_id,
                'error_message': 'Login account not found.'
            }
        )

    # Retrieve Citizen profile
    citizen = Citizen.objects.filter(
        user=login_user
    ).first()

    if not citizen:

        return render(
            request,
            'citizen/edit_citizen_feedback.html',
            {
                'feedback': None,
                'feedback_id': feedback_id,
                'error_message': 'Citizen profile not found.'
            }
        )

    # Retrieve feedback belonging to this Citizen
    feedback = CitizenFeedback.objects.filter(
        id=feedback_id,
        citizen=citizen
    ).select_related('activity').first()

    if not feedback:

        return render(
            request,
            'citizen/edit_citizen_feedback.html',
            {
                'feedback': None,
                'feedback_id': feedback_id,
                'citizen': citizen,
                'error_message': 'Feedback not found or access denied.'
            }
        )

    # UPDATE FEEDBACK
    if request.method == 'POST':

        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()
        feedback_text = request.POST.get('feedback_text', '').strip()

        rating = request.POST.get('rating')

        improvement_suggestions = request.POST.get(
            'improvement_suggestions', ''
        ).strip()

        # Validate required fields
        if not name or not email or not message or not feedback_text:

            return render(
                request,
                'citizen/edit_citizen_feedback.html',
                {
                    'feedback': feedback,
                    'feedback_id': feedback.id,
                    'citizen': citizen,
                    'error_message': 'Please fill in all required fields.'
                }
            )

        # Validate rating
        try:

            rating = int(rating)

            if rating not in [1, 2, 3, 4, 5]:
                raise ValueError

        except (ValueError, TypeError):

            return render(
                request,
                'citizen/edit_citizen_feedback.html',
                {
                    'feedback': feedback,
                    'feedback_id': feedback.id,
                    'citizen': citizen,
                    'error_message': 'Please select a valid rating.'
                }
            )

        # Update feedback details
        feedback.name = name
        feedback.email = email
        feedback.message = message
        feedback.feedback_text = feedback_text
        feedback.rating = rating
        feedback.improvement_suggestions = improvement_suggestions

        # Update image if a new image is uploaded
        if request.FILES.get('image'):

            feedback.image = request.FILES.get('image')

        # Save changes
        feedback.save()

        # Redirect after successful update
        return redirect('view_citizen_feedback')

    # DISPLAY EDIT PAGE
    return render(
        request,
        'citizen/edit_citizen_feedback.html',
        {
            'feedback': feedback,
            'feedback_id': feedback.id,
            'citizen': citizen
        }
    )
def delete_citizen_feedback(request, feedback_id):

    # Only allow POST requests to delete feedback
    if request.method != 'POST':
        return redirect('view_citizen_feedback')

    # Check whether the user is logged in
    if not request.user.is_authenticated:
        return redirect('login')

    # Retrieve Login account
    login_user = Login.objects.filter(
        id=request.user.id
    ).first()

    if not login_user:
        return redirect('view_citizen_feedback')

    # Retrieve Citizen profile
    citizen = Citizen.objects.filter(
        user=login_user
    ).first()

    if not citizen:
        return redirect('view_citizen_feedback')

    # Retrieve feedback belonging to this Citizen
    feedback = CitizenFeedback.objects.filter(
        id=feedback_id,
        citizen=citizen
    ).first()

    if not feedback:
        return redirect('view_citizen_feedback')

    # Delete feedback
    feedback.delete()

    # Redirect to View Citizen Feedback
    return redirect('view_citizen_feedback')
def view_officer_feedback(request):

    # Check the existing Django login session
    if not request.user.is_authenticated:
        return render(request, 'officer/view_officer_feedback.html', {
            'feedbacks': [],
            'total_feedback': 0,
            'error_message': 'Your session has expired. Please log in again.'
        })

    # Get the currently logged-in officer
    officer_user = request.user

    # Check whether the logged-in account is an officer
    if officer_user.usertype != 'officer':
        return render(request, 'officer/view_officer_feedback.html', {
            'feedbacks': [],
            'total_feedback': 0,
            'error_message': 'You are not authorized to access officer feedback.'
        })

    # Retrieve feedback submitted for this officer's activities
    feedbacks = CitizenFeedback.objects.filter(
        activity__user=officer_user
    ).select_related(
        'citizen',
        'activity'
    ).order_by('-timestamp')

    # Count feedback records
    total_feedback = feedbacks.count()

    return render(request, 'officer/view_officer_feedback.html', {
        'feedbacks': feedbacks,
        'total_feedback': total_feedback,
        'officer': officer_user
    })
from django.db.models import Avg

def view_all_citizen_feedback(request):

    # Check existing Django login session
    if not request.user.is_authenticated:
        return render(request, 'admin/view_all_citizen_feedback.html', {
            'feedbacks': [],
            'total_feedback': 0,
            'average_rating': 0,
            'error_message': 'Please log in to access citizen feedback.'
        })

    # Verify admin user
    if request.user.usertype != '':
        return render(request, 'admin/view_all_citizen_feedback.html', {
            'feedbacks': [],
            'total_feedback': 0,
            'average_rating': 0,
            'error_message': 'You are not authorized to access this page.'
        })

    # Retrieve ALL citizen feedback
    feedbacks = CitizenFeedback.objects.all().select_related(
        'citizen',
        'activity',
        'activity__user'
    ).order_by('-timestamp')

    # Total feedback count
    total_feedback = feedbacks.count()

    # Calculate average citizen rating
    average_rating = feedbacks.aggregate(
        average=Avg('rating')
    )['average'] or 0

    # Display all feedback to admin
    return render(request, 'admin/view_all_citizen_feedback.html', {
        'feedbacks': feedbacks,
        'total_feedback': total_feedback,
        'average_rating': average_rating,
    })