"""
Service layer for System Administrator module
Contains all business logic separated from views
"""

from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime
import string
import random

from .models import (
    GlobalsDesignation, GlobalsHoldsdesignation, GlobalsModuleaccess,
    AuthUser, Batch, Student, GlobalsDepartmentinfo, Programme,
    GlobalsFaculty, Staff, GlobalsExtrainfo, Curriculum, Discipline
)
from .serializers import (
    GlobalExtraInfoSerializer, GlobalsDesignationSerializer,
    GlobalsModuleaccessSerializer, AuthUserSerializer,
    GlobalsHoldsDesignationSerializer, StudentSerializer,
    StaffSerializer, GlobalsFacultySerializer
)


class UserService:
    """Service class for user-related operations"""
    
    @staticmethod
    def generate_password(username, first_name=None):
        """Generate a random password for user"""
        special_characters = string.punctuation
        
        if first_name:
            # For existing users with first name
            random_specials = "".join(random.choice(special_characters) for _ in range(2))
            return f"{first_name.lower().capitalize().split(' ')[0]}{username[5:].upper()}{random_specials}"
        else:
            # For new users
            random_specials = ''.join(random.choice(special_characters) for _ in range(3))
            return f"{username.lower().capitalize()}{random_specials}"
    
    @staticmethod
    def create_auth_user(user_data):
        """Create authentication user"""
        auth_user_data = {
            "password": make_password(user_data.get('password', 'user@123')),
            "username": user_data['username'].upper(),
            "first_name": user_data.get('first_name', '').lower().capitalize(),
            "last_name": user_data.get('last_name', '').lower().capitalize(),
            "email": user_data.get('email', f"{user_data['username'].lower()}@iiitdmj.ac.in"),
            "is_staff": user_data.get('is_staff', False),
            "is_superuser": user_data.get('is_superuser', False),
            "is_active": user_data.get('is_active', True),
            "date_joined": datetime.now().strftime("%Y-%m-%d"),
        }
        serializer = AuthUserSerializer(data=auth_user_data)
        if serializer.is_valid():
            return serializer.save()
        return None, serializer.errors
    
    @staticmethod
    def create_extra_info(user, extra_info_data):
        """Create extra info for user"""
        default_department = GlobalsDepartmentinfo.objects.get(name='CSE').id
        
        data = {
            'id': user.username.lower(),
            'title': extra_info_data.get('title') or ('Mr.' if extra_info_data.get('sex', 'M')[0].upper() == 'M' else 'Ms.'),
            'sex': extra_info_data.get('sex', 'M')[0].upper(),
            'date_of_birth': extra_info_data.get("dob") or "2025-01-01",
            'user_status': "PRESENT",
            'address': extra_info_data.get("address") or "NA",
            'phone_no': extra_info_data.get("phone") or 9999999999,
            'about_me': "NA",
            'user_type': extra_info_data.get('user_type'),
            'profile_picture': None,
            'date_modified': datetime.now().strftime("%Y-%m-%d"),
            'department': extra_info_data.get("department") or default_department,
            'user': user.id,
        }
        
        serializer = GlobalExtraInfoSerializer(data=data)
        if serializer.is_valid():
            return serializer.save()
        return None, serializer.errors
    
    @staticmethod
    def assign_designation(user, designation):
        """Assign designation to user"""
        if isinstance(designation, str):
            designation_obj = get_object_or_404(GlobalsDesignation, name=designation)
        else:
            designation_obj = designation
            
        holds_data = {
            'designation': designation_obj.id,
            'user': user.id,
            'working': user.id,
        }
        
        serializer = GlobalsHoldsDesignationSerializer(data=holds_data)
        if serializer.is_valid():
            return serializer.save()
        return None, serializer.errors
    
    @staticmethod
    def create_student_profile(extra_info, student_data):
        """Create student academic profile"""
        batch = Batch.objects.filter(
            name=student_data.get('programme', 'B.Tech'),
            discipline__acronym=extra_info.department.name,
            year=student_data.get('batch', datetime.now().year)
        ).first()
        
        data = {
            'id': extra_info.id,
            'programme': student_data.get('programme', 'B.Tech'),
            'batch': student_data.get('batch', datetime.now().year),
            'batch_id': batch.id if batch else None,
            'cpi': 0.0,
            'category': student_data.get('category', 'GEN').upper(),
            'father_name': student_data.get('father_name'),
            'mother_name': student_data.get('mother_name'),
            'hall_no': student_data.get('hall_no', 3),
            'room_no': None,
            'specialization': None,
            'curr_semester_no': 2 * (datetime.now().year - int(student_data.get('batch', datetime.now().year))) + datetime.now().month // 7,
        }
        
        serializer = StudentSerializer(data=data)
        if serializer.is_valid():
            return serializer.save()
        return None, serializer.errors
    
    @staticmethod
    def create_staff_profile(extra_info):
        """Create staff profile"""
        data = {
            'id': extra_info.id,
        }
        serializer = StaffSerializer(data=data)
        if serializer.is_valid():
            return serializer.save()
        return None, serializer.errors
    
    @staticmethod
    def create_faculty_profile(extra_info):
        """Create faculty profile"""
        data = {
            'id': extra_info.id,
        }
        serializer = GlobalsFacultySerializer(data=data)
        if serializer.is_valid():
            return serializer.save()
        return None, serializer.errors


class RoleManagementService:
    """Service class for role and designation management"""
    
    @staticmethod
    def get_user_roles(username):
        """Get all roles for a user"""
        try:
            user = AuthUser.objects.get(username__iexact=username)
            holds_designations = GlobalsHoldsdesignation.objects.filter(user=user)
            
            if not holds_designations.exists():
                return None, "User has no designations"
            
            designation_ids = [entry.designation_id for entry in holds_designations]
            roles = GlobalsDesignation.objects.filter(id__in=designation_ids)
            
            return {
                'user': AuthUserSerializer(user).data,
                'roles': GlobalsDesignationSerializer(roles, many=True).data,
            }, None
        except AuthUser.DoesNotExist:
            return None, "User not found"
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def update_user_roles(username, roles_to_add):
        """Update roles for a user"""
        user = get_object_or_404(AuthUser, username__iexact=username)
        
        existing_roles = GlobalsHoldsdesignation.objects.filter(user=user)
        existing_role_names = set(existing_roles.values_list('designation__name', flat=True))
        
        # Process roles to add
        processed_roles = set()
        for role in roles_to_add:
            if isinstance(role, dict) and 'name' in role:
                processed_roles.add(role['name'])
            elif isinstance(role, str):
                processed_roles.add(role)
        
        # Remove roles not in new list
        roles_to_remove = existing_role_names - processed_roles
        GlobalsHoldsdesignation.objects.filter(
            user=user, 
            designation__name__in=roles_to_remove
        ).delete()
        
        # Add new roles
        for role_name in processed_roles:
            if role_name not in existing_role_names:
                designation = get_object_or_404(GlobalsDesignation, name=role_name)
                GlobalsHoldsdesignation.objects.create(
                    held_at=timezone.now(),
                    designation=designation,
                    user=user,
                    working=user
                )
        
        return "User roles updated successfully"
    
    @staticmethod
    def create_designation_and_module_access(designation_data):
        """Create designation with default module access"""
        # Create designation
        designation_serializer = GlobalsDesignationSerializer(data=designation_data)
        if not designation_serializer.is_valid():
            return None, designation_serializer.errors
        
        role = designation_serializer.save()
        
        # Create default module access
        max_id = GlobalsModuleaccess.objects.aggregate(Max('id'))['id__max']
        new_id = (max_id or 0) + 1
        
        module_data = {
            'id': new_id,
            'designation': role.name,
            'program_and_curriculum': False,
            'course_registration': False,
            'course_management': False,
            'other_academics': False,
            'spacs': False,
            'department': False,
            'examinations': False,
            'hr': False,
            'iwd': False,
            'complaint_management': False,
            'fts': False,
            'purchase_and_store': False,
            'rspc': False,
            'hostel_management': False,
            'mess_management': False,
            'gymkhana': False,
            'placement_cell': False,
            'visitor_hostel': False,
            'phc': False,
            'inventory_management': False,
        }
        
        module_serializer = GlobalsModuleaccessSerializer(data=module_data)
        if not module_serializer.is_valid():
            return None, module_serializer.errors
        
        module_serializer.save()
        
        return {
            'role': designation_serializer.data,
            'modules': module_serializer.data
        }, None
    
    @staticmethod
    def update_designation(name, update_data, partial=True):
        """Update designation details"""
        try:
            designation = GlobalsDesignation.objects.get(name=name)
        except GlobalsDesignation.DoesNotExist:
            return None, f"Designation with name '{name}' not found"
        
        serializer = GlobalsDesignationSerializer(
            designation, 
            data=update_data, 
            partial=partial
        )
        
        if serializer.is_valid():
            serializer.save()
            return serializer.data, None
        return None, serializer.errors


class ModuleAccessService:
    """Service class for module access management"""
    
    @staticmethod
    def get_module_access(designation):
        """Get module access for a designation"""
        try:
            module_access = GlobalsModuleaccess.objects.get(designation=designation)
            return GlobalsModuleaccessSerializer(module_access).data, None
        except GlobalsModuleaccess.DoesNotExist:
            return None, f"Module access for designation '{designation}' not found"
    
    @staticmethod
    def update_module_access(designation, update_data):
        """Update module access for a designation"""
        try:
            module_access = GlobalsModuleaccess.objects.get(designation=designation)
        except GlobalsModuleaccess.DoesNotExist:
            return None, f"Module access for designation '{designation}' not found"
        
        serializer = GlobalsModuleaccessSerializer(
            module_access,
            data=update_data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return serializer.data, None
        return None, serializer.errors


class BatchDataService:
    """Service class for batch-related data"""
    
    @staticmethod
    def get_all_departments():
        """Get all departments"""
        return GlobalsDepartmentinfo.objects.all().order_by('id')
    
    @staticmethod
    def get_all_batches():
        """Get all distinct batches by year"""
        return Batch.objects.distinct('year')
    
    @staticmethod
    def get_all_programmes():
        """Get all programmes"""
        return Programme.objects.all().order_by('id')
    
    @staticmethod
    def get_all_designations():
        """Get all designations"""
        return GlobalsDesignation.objects.all()
    
    @staticmethod
    def get_designations_by_category(category='student', basic=True):
        """Get designations filtered by category"""
        return GlobalsDesignation.objects.filter(
            category=category, 
            basic=basic
        )
