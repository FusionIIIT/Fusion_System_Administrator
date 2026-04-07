import csv
import datetime
from django.http import HttpResponse
from django.db.models import Max, Q
from django.db.models.functions import Upper
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import GlobalsDesignation, GlobalsHoldsdesignation, GlobalsModuleaccess, AuthUser, Batch, Student, GlobalsDepartmentinfo, Programme, GlobalsFaculty, Staff, AuditLog
from .serializers import GlobalExtraInfoSerializer, GlobalsDesignationSerializer, GlobalsModuleaccessSerializer, AuthUserSerializer, GlobalsHoldsDesignationSerializer, StudentSerializer, GlobalsFacultySerializer, GlobalsDepartmentinfoSerializer, BatchSerializer, ProgrammeSerializer, StaffSerializer, ViewStudentsWithFiltersSerializer, ViewStaffWithFiltersSerializer, ViewFacultyWithFiltersSerializer, AuditLogSerializer
from io import StringIO
from .helpers import create_password, send_email, mail_to_user, configure_password_mail, add_user_extra_info, add_user_designation_info, add_student_info
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.conf import settings
from .audit import audit_log, create_audit_log, get_client_ip, log_failed_login, get_user_agent


# Role conflict rules definition
# Format: (role_name, [conflicting_role_names])
ROLE_CONFLICT_RULES = {
    'director': ['dean', 'hod'],  # Director cannot also be Dean or HOD
    'dean': ['director', 'hod'],  # Dean cannot also be Director or HOD
    'hod': ['director', 'dean'],  # HOD cannot also be Director or Dean
    # Add more conflict rules as needed
}


def check_role_conflicts(user_id, new_designation_id):
    """
    Check if assigning a new role to a user conflicts with existing roles.
    Returns a list of conflicting role names, or empty list if no conflicts.
    """
    try:
        new_designation = GlobalsDesignation.objects.get(id=new_designation_id)
        user_roles = GlobalsHoldsdesignation.objects.filter(user_id=user_id).select_related('designation')
        
        existing_role_names = [entry.designation.name for entry in user_roles]
        conflicting_roles = []
        
        # Check if new role conflicts with any existing role
        if new_designation.name in ROLE_CONFLICT_RULES:
            for conflicting_role in ROLE_CONFLICT_RULES[new_designation.name]:
                if conflicting_role in existing_role_names:
                    conflicting_roles.append(conflicting_role)
        
        # Check if any existing role conflicts with the new role
        for existing_role in existing_role_names:
            if existing_role in ROLE_CONFLICT_RULES:
                if new_designation.name in ROLE_CONFLICT_RULES[existing_role]:
                    if new_designation.name not in conflicting_roles:
                        conflicting_roles.append(new_designation.name)
        
        return conflicting_roles
    except GlobalsDesignation.DoesNotExist:
        return []


@api_view(['GET'])
def get_all_departments(request):
    records = GlobalsDepartmentinfo.objects.all().order_by('id')
    serializer = GlobalsDepartmentinfoSerializer(records, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_all_batches(request):
    records = Batch.objects.distinct('year')
    serializer = BatchSerializer(records, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_all_programmes(request):
    records = Programme.objects.all().order_by('id')
    serializer = ProgrammeSerializer(records, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_user_role_by_username(request):
    username = request.query_params.get('username')
    
    if not username:
        return Response({"error": "Username parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = AuthUser.objects.get(username__iexact=username)
        holds_designation_entries = GlobalsHoldsdesignation.objects.filter(user=user)
        
        if not holds_designation_entries.exists():
            return Response({"error": "User has no designations."}, status=status.HTTP_404_NOT_FOUND)
        
        designation_ids = [entry.designation_id for entry in holds_designation_entries]
        
        roles = GlobalsDesignation.objects.filter(id__in=designation_ids)
        roles_serializer = GlobalsDesignationSerializer(roles, many=True)
        
        return Response({
            "user": AuthUserSerializer(user).data,
            "roles": roles_serializer.data,
        }, status=status.HTTP_200_OK)
        
    except AuthUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@audit_log(action='UPDATE_USER_ROLES', model_name='GlobalsHoldsdesignation')
def update_user_roles(request):
    username = request.data.get('username')
    roles_to_add = request.data.get('roles')

    if not username or not roles_to_add:
        return Response({"error": "Username and roles are required."}, status=status.HTTP_400_BAD_REQUEST)

    user = get_object_or_404(AuthUser, username__iexact=username)

    existing_roles = GlobalsHoldsdesignation.objects.filter(user=user)
    existing_role_names = set(existing_roles.values_list('designation__name', flat=True))

    processed_roles_to_add = set()

    for role in roles_to_add:
        if isinstance(role, dict):
            if 'name' in role:
                processed_roles_to_add.add(role['name'])
        elif isinstance(role, str):
            processed_roles_to_add.add(role)

    print("Processed roles_to_add:", processed_roles_to_add)

    # Validate roles before assignment
    for role_name in processed_roles_to_add:
        if role_name not in existing_role_names:
            try:
                designation = GlobalsDesignation.objects.get(name=role_name)
                
                # Check singular role constraint
                if designation.is_singular:
                    other_users_with_role = GlobalsHoldsdesignation.objects.filter(
                        designation=designation
                    ).exclude(user=user)
                    
                    if other_users_with_role.exists():
                        other_user = other_users_with_role.first().user
                        return Response({
                            "error": f"Role '{role_name}' is a singular role and can only be assigned to one user at a time.",
                            "current_holder": other_user.username
                        }, status=status.HTTP_409_CONFLICT)
                
                # Check role conflicts
                conflicts = check_role_conflicts(user.id, designation.id)
                if conflicts:
                    return Response({
                        "error": f"Role '{role_name}' conflicts with existing roles: {', '.join(conflicts)}",
                        "conflicting_roles": conflicts
                    }, status=status.HTTP_409_CONFLICT)
                    
            except GlobalsDesignation.DoesNotExist:
                return Response({"error": f"Role '{role_name}' does not exist."}, status=status.HTTP_404_NOT_FOUND)

    roles_to_remove = existing_role_names - processed_roles_to_add

    GlobalsHoldsdesignation.objects.filter(user=user, designation__name__in=roles_to_remove).delete()

    for role_name in processed_roles_to_add:
        if role_name not in existing_role_names:
            designation = get_object_or_404(GlobalsDesignation, name=role_name)
            
            # Get optional start_date and end_date from request
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')
            
            # Validate dates
            if start_date and end_date:
                from datetime import datetime
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                
                if end_dt <= start_dt:
                    return Response({
                        "error": "End date must be after start date."
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            GlobalsHoldsdesignation.objects.create(
                held_at=timezone.now(),
                designation=designation,
                user=user,
                working=user,
                start_date=start_date if start_date else None,
                end_date=end_date if end_date else None
            )

    return Response({"message": "User roles updated successfully."}, status=status.HTTP_200_OK)
        
@api_view(['GET'])
def global_designation_list(request):
    records = GlobalsDesignation.objects.all()
    serializer = GlobalsDesignationSerializer(records, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def get_category_designations(request):
    category = request.data.get('category', 'student')
    basic = request.data.get('basic', True)
    records = GlobalsDesignation.objects.all().filter(category=category, basic=basic)
    serializer = GlobalsDesignationSerializer(records, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@audit_log(action='CREATE_ROLE', model_name='GlobalsDesignation')
def add_designation(request):
    serializer = GlobalsDesignationSerializer(data=request.data)
    if serializer.is_valid():
        role = serializer.save()
        max_id = GlobalsModuleaccess.objects.aggregate(Max('id'))['id__max']
        new_id = (max_id or 0) + 1
        data = {
            'id': new_id,
            'designation' : role.name,
            'program_and_curriculum' : False,
            'course_registration' : False,
            'course_management' : False,
            'other_academics' : False,
            'spacs' : False,
            'department' : False,
            'examinations' : False,
            'hr' : False,
            'iwd' : False,
            'complaint_management' : False,
            'fts' : False,
            'purchase_and_store' : False,
            'rspc' : False,
            'hostel_management' : False,
            'mess_management' : False,
            'gymkhana' : False,
            'placement_cell' : False,
            'visitor_hostel' : False,
            'phc' : False,
            'inventory_management': False,
        }
        module_serializer = GlobalsModuleaccessSerializer(data=data)
        if module_serializer.is_valid():
            module_serializer.save()
        return Response({'role': serializer.data, 'modules': module_serializer.data}, status.HTTP_201_CREATED)
    else :
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@audit_log(action='UPDATE_ROLE', model_name='GlobalsDesignation')
def update_designation(request):
    name = request.data.get('name')
    
    if not name:
        return Response({"error": "No name provided."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        designation = GlobalsDesignation.objects.get(name=name)
    except GlobalsDesignation.DoesNotExist:
        return Response({"error": f"Designation with name '{name}' not found."}, status=status.HTTP_404_NOT_FOUND)
    
    partial = request.method == 'PATCH'
    serializer = GlobalsDesignationSerializer(designation, data=request.data, partial=partial)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@audit_log(action='RESET_PASSWORD', model_name='AuthUser')
def reset_password(request):
    user_name = request.data.get('username')
    try:
        user = AuthUser.objects.annotate(username_upper=Upper('username')).get(username_upper=user_name.upper())
        new_password = create_password(request.data)
        while new_password == user.password:
            new_password = create_password(request.data)
        
        user.password = new_password
        user.save()
        
        try:
            subject = 'Your Password has been reset!!'
            message = f"This Mail is to notify you that your password has been reset by the System Administrator.\n\nPlease check out the new password below:  {new_password}\n\nRegards,\nSystem Administrator,\nIIITDM Jabalpur."
            recipient_list = [f"{user.email}" if settings.EMAIL_TEST_MODE == 0 else settings.EMAIL_TEST_USER]
            send_email(subject=subject, message=message, recipient_list=recipient_list)
        except:
            print(e)
        finally:
            return Response({"password": new_password,"message": "Password reset successfully."}, status=status.HTTP_200_OK)
    except AuthUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_module_access(request):
    role_name = request.query_params.get('designation')
    
    if not role_name:
        return Response({"error": "No role provided."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        module_access = GlobalsModuleaccess.objects.get(designation=role_name)
    except GlobalsModuleaccess.DoesNotExist:
        return Response({"error": f"Module access for designation '{role_name}' not found."}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = GlobalsModuleaccessSerializer(module_access)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
@api_view(['PUT'])
@audit_log(action='MODIFY_MODULE_ACCESS', model_name='GlobalsModuleaccess')
def modify_moduleaccess(request):
    role_name = request.data.get('designation')
    
    if not role_name:
        return Response({"error": "No role provided."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        designation = GlobalsModuleaccess.objects.get(designation=role_name)
    except GlobalsModuleaccess.DoesNotExist:
        return Response({"error": f"Designation with name '{role_name}' not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = GlobalsModuleaccessSerializer(designation, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@audit_log(action='CREATE_STUDENT', model_name='AuthUser')
def add_individual_student(request):
    required_fields = ["username", "first_name", "last_name", "sex", "category", "father_name", "mother_name", "batch", "programme"]
    data = request.data
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    if missing_fields:
        return Response({
            "error": "Missing required fields.",
            "missing_fields": missing_fields
        }, status=status.HTTP_400_BAD_REQUEST)
    user_password = create_password(data)
    
    auth_user_data = {
        "password": make_password(user_password),
        "username": data['username'].upper(),
        "first_name": data['first_name'],
        "last_name": data.get('last_name', ""),
        "email": f"{data['username'].lower()}@iiitdmj.ac.in",
        "is_staff": False,
        "is_superuser": False,
        "is_active": True,
        "date_joined": datetime.datetime.now().strftime("%Y-%m-%d"),
    }
    auth_serializer = AuthUserSerializer(data=auth_user_data)
    user = None
    if auth_serializer.is_valid():
        user = auth_serializer.save()
    else:
        return Response({
            "message": "Error in adding user to auth user table",
            "data": auth_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    default_department = GlobalsDepartmentinfo.objects.get(name='CSE').id
    extra_info_data = {
        'id': data['username'].upper(),
        'title': data.get('title') if data.get('title') else 'Mr.' if data['sex'][0].upper() == 'M' else 'Ms.',
        'sex': data['sex'][0].upper(),
        'date_of_birth': data.get("dob") if data.get("dob") else "2025-01-01",
        'user_status': "PRESENT",
        'address': data.get("address") if data.get("address") else "NA",
        'phone_no': data.get("phone") if data.get("phone") else 9999999999,
        'about_me': "NA",
        'user_type': 'student',
        'profile_picture': None,
        'date_modified': datetime.datetime.now().strftime("%Y-%m-%d"),
        'department': data.get("department") if data.get("department") else default_department,
        'user': user.id,
    }
    extra_info_serializer = GlobalExtraInfoSerializer(data=extra_info_data)
    extra_info = None
    if extra_info_serializer.is_valid():
        extra_info = extra_info_serializer.save()
    else:
        return Response({
            "message": "Error in adding user to globals extra info table",
            "data": extra_info_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    designation_id = GlobalsDesignation.objects.get(name='student').id
    holds_designation_data = {
        'designation' : designation_id,
        'user' : user.id,
        'working' : user.id,
    }
    holds_designation_serializer = GlobalsHoldsDesignationSerializer(data=holds_designation_data)
    if holds_designation_serializer.is_valid():
        holds_designation_serializer.save()
    else:
        return Response({
            "message": "Error in adding user to globals holds designation table",
            "data": holds_designation_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    batch = Batch.objects.filter(name = data.get('programme'), discipline__acronym = extra_info.department.name, year = data.get('batch')).first()
    student_data = {
        'id' : extra_info.id,
        'programme' : data.get('programme') if data.get('programme') else 'B.Tech',
        'batch' : data.get('batch') if data.get('batch') else datetime.datetime.now().year,
        'batch_id' : batch.id if batch else None,
        'cpi': 0.0,
        'category' : data['category'].upper() if data['category'].upper() else 'GEN',
        'father_name' : data.get('father_name') if data.get('father_name') else None,
        'mother_name' : data.get('mother_name') if data.get('mother_name') else None,
        'hall_no': data.get('hall_no') if data.get('hall_no') else 3,
        'room_no': None,
        'specialization': None,
        'curr_semester_no' : 2*(datetime.datetime.now().year - data.get('batch')) + datetime.datetime.now().month // 7,
    }
    student_data_serializer = StudentSerializer(data=student_data)
    if student_data_serializer.is_valid():
        student_data_serializer.save()
    else:
        return Response({
            "message": "Error in adding user to academic information student table",
            "data": student_data_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    response_data = {
        "message": f"1 user created successfully.",
        "created_users": [auth_serializer.data],
        "skipped_users_count": 0,
    }

    return Response(response_data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@audit_log(action='CREATE_STAFF', model_name='AuthUser')
def add_individual_staff(request):
    required_fields = ["username", "first_name", "last_name", "sex", "designation"]
    data = request.data
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    if missing_fields:
        return Response({
            "error": "Missing required fields.",
            "missing_fields": missing_fields
        }, status=status.HTTP_400_BAD_REQUEST)
    user_password = create_password(data)
    auth_user_data = {
        "password": make_password(user_password),
        "username": data['username'].lower(),
        "first_name": data['first_name'].lower().capitalize(),
        "last_name": data.get('last_name').lower().capitalize(),
        "email": f"{data['username'].lower()}@iiitdmj.ac.in",
        "is_staff": True,
        "is_superuser": False,
        "is_active": True,
        "date_joined": datetime.datetime.now().strftime("%Y-%m-%d"),
    }
    auth_serializer = AuthUserSerializer(data=auth_user_data)
    user = None
    if auth_serializer.is_valid():
        user = auth_serializer.save()
    else:
        return Response({
            "message": "Error in adding user to auth user table",
            "data": auth_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    default_department = GlobalsDepartmentinfo.objects.get(name='CSE').id
    extra_info_data = {
        'id': data['username'].lower(),
        'title': data.get('title') if data.get('title') else 'Mr.' if data['sex'][0].upper() == 'M' else 'Ms.',
        'sex': data['sex'][0].upper(),
        'date_of_birth': data.get("dob") if data.get("dob") else "2025-01-01",
        'user_status': "PRESENT",
        'address': data.get("address") if data.get("address") else "NA",
        'phone_no': data.get("phone") if data.get("phone") else 9999999999,
        'about_me': "NA",
        'user_type': 'staff',
        'profile_picture': None,
        'date_modified': datetime.datetime.now().strftime("%Y-%m-%d"),
        'department': data.get("department") if data.get("department") else default_department,
        'user': user.id,
    }
    extra_info_serializer = GlobalExtraInfoSerializer(data=extra_info_data)
    extra_info = None
    if extra_info_serializer.is_valid():
        extra_info = extra_info_serializer.save()
    else:
        return Response({
            "message": "Error in adding user to globals extra info table",
            "data": extra_info_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    holds_designation_data = {
        'designation' : data.get('designation'),
        'user' : user.id,
        'working' : user.id,
    }
    holds_designation_serializer = GlobalsHoldsDesignationSerializer(data=holds_designation_data)
    if holds_designation_serializer.is_valid():
        holds_designation_serializer.save()
    else:
        return Response({
            "message": "Error in adding user to globals holds designation table",
            "data": holds_designation_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    staff_id = extra_info.id
    staff_data = {
        'id' : staff_id,
    }

    staff_serializer = GlobalsFacultySerializer(data=staff_data)
    if staff_serializer.is_valid():
        staff_serializer.save()
    else:
        return Response({
            "message": "Error in adding user to globals staff table",
            "data": staff_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "message": "Staff added successfully",
        "auth_user_data": auth_user_data,
        "extra_info_user_data": extra_info_data,
        "holds_designation_user_data": holds_designation_data,
        "globals_staff_data": staff_data,
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@audit_log(action='CREATE_FACULTY', model_name='AuthUser')
def add_individual_faculty(request):
    required_fields = ["username", "first_name", "last_name", "sex", "designation"]
    data = request.data
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    if missing_fields:
        return Response({
            "error": "Missing required fields.",
            "missing_fields": missing_fields
        }, status=status.HTTP_400_BAD_REQUEST)
    user_password = create_password(data)
    auth_user_data = {
        "password": make_password(user_password),
        "username": data['username'].lower(),
        "first_name": data['first_name'].lower().capitalize(),
        "last_name": data.get('last_name').lower().capitalize(),
        "email": f"{data['username'].lower()}@iiitdmj.ac.in",
        "is_staff": False,
        "is_superuser": False,
        "is_active": True,
        "date_joined": datetime.datetime.now().strftime("%Y-%m-%d"),
    }
    auth_serializer = AuthUserSerializer(data=auth_user_data)
    user = None
    if auth_serializer.is_valid():
        user = auth_serializer.save()
    else:
        return Response({
            "message": "Error in adding user to auth user table",
            "data": auth_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    default_department = GlobalsDepartmentinfo.objects.get(name='CSE').id
    extra_info_data = {
        'id': data['username'].lower(),
        'title': data.get('title') if data.get('title') else 'Mr.' if data['sex'][0].upper() == 'M' else 'Ms.',
        'sex': data['sex'][0].upper(),
        'date_of_birth': data.get("dob") if data.get("dob") else "2025-01-01",
        'user_status': "PRESENT",
        'address': data.get("address") if data.get("address") else "NA",
        'phone_no': data.get("phone") if data.get("phone") else 9999999999,
        'about_me': "NA",
        'user_type': 'faculty',
        'profile_picture': None,
        'date_modified': datetime.datetime.now().strftime("%Y-%m-%d"),
        'department': data.get("department") if data.get("department") else default_department,
        'user': user.id,
    }
    extra_info_serializer = GlobalExtraInfoSerializer(data=extra_info_data)
    extra_info = None
    if extra_info_serializer.is_valid():
        extra_info = extra_info_serializer.save()
    else:
        return Response({
            "message": "Error in adding user to globals extra info table",
            "data": extra_info_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    holds_designation_data = {
        'designation' : data.get('designation'),
        'user' : user.id,
        'working' : user.id,
    }
    holds_designation_serializer = GlobalsHoldsDesignationSerializer(data=holds_designation_data)
    if holds_designation_serializer.is_valid():
        holds_designation_serializer.save()
    else:
        return Response({
            "message": "Error in adding user to globals holds designation table",
            "data": holds_designation_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    faculty_id = extra_info.id
    faculty_data = {
        'id' : faculty_id,
    }

    faculty_serializer = GlobalsFacultySerializer(data=faculty_data)
    if faculty_serializer.is_valid():
        faculty_serializer.save()
    else:
        return Response({
            "message": "Error in adding user to globals faculty table",
            "data": faculty_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "message": "Faculty added successfully",
        "auth_user_data": auth_user_data,
        "extra_info_user_data": extra_info_data,
        "holds_designation_user_data": holds_designation_data,
        "globals_faculty_data": faculty_data,
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@audit_log(action='BULK_IMPORT_USERS', model_name='AuthUser')
def bulk_import_users(request):
    # CSV file headers:
    # 1 username
    # 2 first_name
    # 3 last_name
    # 4 sex
    # 5 category
    # 6 father_name
    # 7 mother_name
    # 8 batch
    # 9 programme
    # 10 title
    # 11 dob
    # 12 address
    # 13 phone_no
    # 14 department
    if 'file' not in request.FILES:
        return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    if not file.name.endswith('.csv'):
        return Response({"error": "Please upload a valid CSV file."}, status=status.HTTP_400_BAD_REQUEST)

    file_data = file.read().decode('utf-8')
    csv_data = csv.reader(StringIO(file_data))
    
    headers = next(csv_data)
    created_users = []
    failed_users = []
    
    for row in csv_data:
        if len(row) < 9:
            failed_users.append(row)
            continue
        try:
            user_data = {
                'password': make_password("user@123"),
                'username': row[0].upper(),
                'first_name': row[1].lower().capitalize() if len(row[1]) > 0 else 'NA',
                'last_name': row[2].lower().capitalize() if len(row[2]) > 0 else 'NA',
                'email': f"{row[0].lower()}@iiitdmj.ac.in",
                'is_staff': False,
                'is_superuser': False,
                'is_active': True,
            }
            serializer = AuthUserSerializer(data=user_data)
            user = None
            if serializer.is_valid():
                user = serializer.save()
            extra_info_serializer = add_user_extra_info(row, user)
            extra_serializer = None
            if extra_info_serializer:
                extra_serializer = extra_info_serializer.save()
            role_serializer = add_user_designation_info(user.id)
            if role_serializer:
                role_serializer.save()
            student_serializer = add_student_info(row, extra_serializer)
            if student_serializer:
                student_serializer.save()
            if user and extra_info_serializer and role_serializer and student_serializer:
                created_users.append(serializer.data)
        except Exception as e:
            print("error",e)
            failed_users.append(row)

    if(len(created_users) > 0):
        mail_to_user(created_users)
        
    response_data = {
        "message": f"{len(created_users)} users created successfully.",
        "created_users": created_users,
        "skipped_users_count": len(failed_users),
    }

    if failed_users:
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)

        for failed_user in failed_users:
            writer.writerow(failed_user)

        output.seek(0)
        response_data["skipped_users_csv"] = output.getvalue()

    return Response(response_data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def bulk_export_users(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser'])
    users = AuthUser.objects.all()
    
    for user in users:
        writer.writerow([user.username, user.first_name, user.last_name, user.email, user.is_staff, user.is_superuser])
    
    return response

@api_view(['POST'])
def mail_to_whole_batch(request):
    emails = EMAIL_TEST_ARRAY
    email_list = emails.split(',')
    if(len(email_list) != 1):
        students = Student.objects.filter(batch=request.data.get('batch'), id__user__email__in=email_list)
    else:
        students = Student.objects.filter(batch=request.data.get('batch'))
        
    students_data = [student.id.user for student in students]
    try:
        configure_password_mail(students_data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({"message": "Mail sent to whole batch successfully."}, status=status.HTTP_200_OK)

def download_sample_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sample.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "username", "first_name", "last_name", "sex", "category",
        "father_name", "mother_name", "batch", "programme", "title",
        "dob", "address", "phone_no", "department"
    ])
    return response

class UserListView(APIView):
    def get(self, request):
        user_type = request.GET.get('type')
        serializer = None

        if user_type == "student":
            students = Student.objects.select_related('id__user', 'id__department', 'batch_id')
            programme = request.GET.get("programme")
            batch = request.GET.get("batch")
            discipline = request.GET.get("discipline")
            category = request.GET.get("category")
            gender = request.GET.get("gender")

            if programme:
                students = students.filter(programme__iexact=programme)
            if batch:
                students = students.filter(batch=batch)
            if discipline:
                students = students.filter(batch_id__discipline__name__iexact=discipline)
            if category:
                students = students.filter(category__iexact=category)
            if gender:
                students = students.filter(id__sex__iexact=gender)

            serializer = ViewStudentsWithFiltersSerializer(students, many=True)

        elif user_type == "faculty":
            faculty = GlobalsFaculty.objects.select_related('id__user', 'id__department').prefetch_related('id__user__holds_designations__designation')
            designation = request.GET.get("designation")
            gender = request.GET.get("gender")

            if designation:
                faculty = faculty.filter(id__user__holds_designations__designation__name__iexact=designation).distinct()
            if gender:
                faculty = faculty.filter(id__sex__iexact=gender)

            serializer = ViewFacultyWithFiltersSerializer(faculty, many=True)

        elif user_type == "staff":
            staff = Staff.objects.select_related("id__user", "id__department").prefetch_related('id__user__holds_designations__designation')
            designation = request.GET.get("designation")
            gender = request.GET.get("gender")

            if designation:
                staff = staff.filter(id__user__holds_designations__designation__name__iexact=designation).distinct()
            if gender:
                staff = staff.filter(id__sex__iexact=gender)

            serializer = ViewStaffWithFiltersSerializer(staff, many=True)

        else:
            return Response({"error": "Invalid or missing user type."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@audit_log(action='ARCHIVE_USER', model_name='AuthUser')
def archive_user(request, username):
    """
    Archive a user account (deactivate account).
    Note: Since this uses an existing database table, we use is_active flag.
    """
    try:
        user = get_object_or_404(AuthUser, username=username)

        # Check if user is already archived (inactive)
        if not user.is_active:
            return Response({
                "error": "User is already archived (inactive)"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check 30-day minimum period
        if user.date_joined:
            days_since_joined = (timezone.now() - user.date_joined).days
            if days_since_joined < 30:
                return Response({
                    "error": f"User must be at least 30 days old to archive. Current age: {days_since_joined} days"
                }, status=status.HTTP_400_BAD_REQUEST)

        # Archive the user (deactivate)
        user.is_active = False
        user.save()

        create_audit_log(
            user=request.user,
            action='ARCHIVE_USER',
            model_name='AuthUser',
            object_id=str(user.id),
            description=f"User {user.username} archived (deactivated) by {request.user.username}",
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            status='SUCCESS'
        )

        return Response({
            "message": f"User {user.username} archived successfully"
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "error": f"Failed to archive user: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@audit_log(action='RESTORE_USER', model_name='AuthUser')
def restore_user(request, username):
    """
    Restore an archived user account (reactivate account).
    """
    try:
        user = get_object_or_404(AuthUser, username=username)

        # Check if user is active (not archived)
        if user.is_active:
            return Response({
                "error": "User is not archived (already active)"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Restore the user (activate)
        user.is_active = True
        user.save()

        create_audit_log(
            user=request.user,
            action='RESTORE_USER',
            model_name='AuthUser',
            object_id=str(user.id),
            description=f"User {user.username} restored (reactivated) by {request.user.username}",
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            status='SUCCESS'
        )

        return Response({
            "message": f"User {user.username} restored successfully"
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "error": f"Failed to restore user: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_audit_logs(request):
    """
    Retrieve audit logs with filtering support.
    Query params:
    - start_date: Filter logs from this date (YYYY-MM-DD)
    - end_date: Filter logs until this date (YYYY-MM-DD)
    - user: Filter by username
    - action: Filter by action type
    - status: Filter by status (SUCCESS/FAILED)
    - page: Page number (default 1)
    - page_size: Number of results per page (default 50, max 200)
    """
    # Start with all logs
    logs = AuditLog.objects.all()
    
    # Apply filters
    start_date = request.query_params.get('start_date')
    if start_date:
        try:
            from datetime import datetime
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            logs = logs.filter(timestamp__gte=start_dt)
        except ValueError:
            return Response({"error": "Invalid start_date format. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
    
    end_date = request.query_params.get('end_date')
    if end_date:
        try:
            from datetime import datetime, timedelta
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            logs = logs.filter(timestamp__lt=end_dt)
        except ValueError:
            return Response({"error": "Invalid end_date format. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
    
    username = request.query_params.get('user')
    if username:
        logs = logs.filter(user__username__icontains=username)
    
    action = request.query_params.get('action')
    if action:
        logs = logs.filter(action__icontains=action)
    
    status_filter = request.query_params.get('status')
    if status_filter:
        logs = logs.filter(status=status_filter.upper())
    
    # Pagination
    try:
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))
        page_size = min(page_size, 200)  # Max 200 per page
    except ValueError:
        return Response({"error": "Invalid page or page_size parameter"}, status=status.HTTP_400_BAD_REQUEST)
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    # Get total count and paginated results
    total_count = logs.count()
    logs = logs[start_idx:end_idx]
    
    serializer = AuditLogSerializer(logs, many=True)
    
    return Response({
        'count': total_count,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_count + page_size - 1) // page_size,
        'results': serializer.data
    }, status=status.HTTP_200_OK)


# ==================== AUTHENTICATION VIEWS ====================

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from datetime import timedelta, datetime as dt
from backend.settings import MAX_FAILED_LOGIN_ATTEMPTS, FAILED_LOGIN_ATTEMPT_DURATION


@api_view(['POST'])
def login_view(request):
    """
    Authenticate user and return JWT tokens.
    Accepts username OR email + password.
    """
    username_or_email = request.data.get('username')
    password = request.data.get('password')
    
    if not username_or_email or not password:
        return Response(
            {"error": "Username/email and password are required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Try to find user by username or email
        if '@' in username_or_email:
            user = AuthUser.objects.get(email__iexact=username_or_email)
            print(f"[LOGIN] Found user by email: {user.username}")
        else:
            user = AuthUser.objects.get(username__iexact=username_or_email)
            print(f"[LOGIN] Found user by username: {user.username}")

        # Check for account lockout due to failed login attempts
        from backend.settings import LOGIN_LOCKOUT_ENABLED, MAX_FAILED_LOGIN_ATTEMPTS, FAILED_LOGIN_ATTEMPT_DURATION
        if LOGIN_LOCKOUT_ENABLED:
            lockout_window = timezone.now() - timedelta(seconds=FAILED_LOGIN_ATTEMPT_DURATION)
            recent_failures = AuditLog.objects.filter(
                action='FAILED_LOGIN',
                description__contains=username_or_email,
                timestamp__gte=lockout_window
            ).count()

            if recent_failures >= MAX_FAILED_LOGIN_ATTEMPTS:
                print(f"[LOGIN] Account locked for {username_or_email} due to {recent_failures} failed attempts")
                return Response({
                    "error": f"Account locked due to multiple failed login attempts. Please try again after {FAILED_LOGIN_ATTEMPT_DURATION // 60} minutes."
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)

    except AuthUser.DoesNotExist:
        print(f"[LOGIN] User not found: {username_or_email}")
        # Log failed login attempt
        try:
            log_failed_login(
                username_or_email=username_or_email,
                reason='User does not exist',
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request)
            )
        except Exception as e:
            print(f"[ERROR] Failed to log failed login: {e}")
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Check password
    if not check_password(password, user.password):
        print(f"[LOGIN] Invalid password for user: {user.username}")
        # Log failed login attempt
        try:
            log_failed_login(
                username_or_email=username_or_email,
                reason='Invalid password',
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request)
            )
        except Exception as e:
            print(f"[ERROR] Failed to log failed login: {e}")
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        print(f"[LOGIN] Account disabled for user: {user.username}")
        # Log failed login attempt
        try:
            log_failed_login(
                username_or_email=username_or_email,
                reason='Account is disabled',
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request)
            )
        except Exception as e:
            print(f"[ERROR] Failed to log failed login: {e}")
        return Response(
            {"error": "Account is disabled"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Generate tokens
    try:
        refresh = RefreshToken.for_user(user)
        user.last_login = timezone.now()
        user.save()
        
        user_roles = GlobalsHoldsdesignation.objects.filter(user=user).select_related('designation')
        roles = [entry.designation.name for entry in user_roles]
        
        print(f"[LOGIN] Successful login for: {user.username}, roles: {roles}")
        
        create_audit_log(
            user=user,
            action='USER_LOGIN',
            model_name='AuthUser',
            object_id=str(user.id),
            description=f"User {user.username} logged in successfully",
            ip_address=get_client_ip(request),
            status='SUCCESS'
        )
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'roles': roles,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"[LOGIN] Error generating tokens for {user.username}: {str(e)}")
        return Response(
            {"error": "Failed to generate authentication tokens", "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class CustomTokenRefreshView(TokenRefreshView):
    """Custom token refresh that returns user data"""
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            try:
                refresh = RefreshToken(request.data.get('refresh'))
                user_id = refresh['user_id']
                user = AuthUser.objects.get(id=user_id)
                
                user_roles = GlobalsHoldsdesignation.objects.filter(user=user).select_related('designation')
                roles = [entry.designation.name for entry in user_roles]
                
                response.data['user'] = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'roles': roles,
                    'is_staff': user.is_staff,
                }
            except Exception as e:
                print(f"Error getting user data: {e}")
        
        return response


@api_view(['POST'])
def logout_view(request):
    """Log out user and record audit trail"""
    user = request.user
    
    if user.is_authenticated:
        create_audit_log(
            user=user,
            action='USER_LOGOUT',
            model_name='AuthUser',
            object_id=str(user.id),
            description=f"User {user.username} logged out",
            ip_address=get_client_ip(request),
            status='SUCCESS'
        )
        
        return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
    
    return Response({"error": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """Get current authenticated user's information"""
    user = request.user
    
    try:
        user_roles = GlobalsHoldsdesignation.objects.filter(user=user).select_related('designation')
        roles = [entry.designation.name for entry in user_roles]
        
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'roles': roles,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'last_login': user.last_login
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Failed to fetch user information',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

