"""
Database Query Selectors for System Administrator Module

This module contains all database queries, separated from business logic.
Follows the selector pattern for clean architecture.
"""

from django.db.models import Max, Q, Upper, Prefetch
from django.shortcuts import get_object_or_404

from .models import (
    GlobalsDesignation, GlobalsHoldsdesignation, GlobalsModuleaccess,
    AuthUser, Batch, Student, GlobalsDepartmentinfo, Programme,
    GlobalsFaculty, Staff, GlobalsExtrainfo, Curriculum, Discipline
)


class UserSelectors:
    """Database query selectors for user operations"""
    
    @staticmethod
    def get_user_by_username(username):
        """Get user by username (case-insensitive)"""
        try:
            return AuthUser.objects.annotate(
                username_upper=Upper('username')
            ).get(username_upper=username.upper())
        except AuthUser.DoesNotExist:
            return None
    
    @staticmethod
    def get_user_with_designations(username):
        """Get user with their designations"""
        try:
            user = AuthUser.objects.get(username__iexact=username)
            holds_designations = GlobalsHoldsdesignation.objects.filter(
                user=user
            ).select_related('designation')
            return user, holds_designations
        except AuthUser.DoesNotExist:
            return None, None
    
    @staticmethod
    def get_all_users():
        """Get all users"""
        return AuthUser.objects.all()
    
    @staticmethod
    def filter_students(programme=None, batch=None, discipline=None, 
                       category=None, gender=None):
        """Filter students with various criteria"""
        queryset = Student.objects.select_related(
            'id__user', 
            'id__department', 
            'batch_id'
        ).prefetch_related(
            Prefetch('batch_id__discipline')
        )
        
        if programme:
            queryset = queryset.filter(programme__iexact=programme)
        if batch:
            queryset = queryset.filter(batch=batch)
        if discipline:
            queryset = queryset.filter(
                batch_id__discipline__name__iexact=discipline
            )
        if category:
            queryset = queryset.filter(category__iexact=category)
        if gender:
            queryset = queryset.filter(id__sex__iexact=gender)
        
        return queryset
    
    @staticmethod
    def filter_faculty(designation=None, gender=None):
        """Filter faculty with various criteria"""
        queryset = GlobalsFaculty.objects.select_related(
            'id__user', 
            'id__department'
        ).prefetch_related(
            Prefetch('id__user__holds_designations__designation')
        )
        
        if designation:
            queryset = queryset.filter(
                id__user__holds_designations__designation__name__iexact=designation
            ).distinct()
        if gender:
            queryset = queryset.filter(id__sex__iexact=gender)
        
        return queryset
    
    @staticmethod
    def filter_staff(designation=None, gender=None):
        """Filter staff with various criteria"""
        queryset = Staff.objects.select_related(
            'id__user', 
            'id__department'
        ).prefetch_related(
            Prefetch('id__user__holds_designations__designation')
        )
        
        if designation:
            queryset = queryset.filter(
                id__user__holds_designations__designation__name__iexact=designation
            ).distinct()
        if gender:
            queryset = queryset.filter(id__sex__iexact=gender)
        
        return queryset
    
    @staticmethod
    def get_students_by_batch(batch_year):
        """Get all students from a specific batch year"""
        return Student.objects.filter(batch=batch_year).select_related(
            'id__user'
        )
    
    @staticmethod
    def check_user_exists(username):
        """Check if user exists (case-insensitive)"""
        return AuthUser.objects.filter(
            username__iexact=username
        ).exists()
    
    @staticmethod
    def check_student_exists(extrainfo_id):
        """Check if student exists"""
        return Student.objects.filter(id=extrainfo_id).exists()


class RoleSelectors:
    """Database query selectors for role operations"""
    
    @staticmethod
    def get_all_designations():
        """Get all designations"""
        return GlobalsDesignation.objects.all()
    
    @staticmethod
    def get_designations_by_category(category='student', basic=True):
        """Get designations filtered by category and basic flag"""
        return GlobalsDesignation.objects.filter(
            category=category,
            basic=basic
        )
    
    @staticmethod
    def get_designation_by_name(name):
        """Get designation by name"""
        try:
            return GlobalsDesignation.objects.get(name=name)
        except GlobalsDesignation.DoesNotExist:
            return None
    
    @staticmethod
    def get_user_roles(user):
        """Get all roles held by a user"""
        return GlobalsHoldsdesignation.objects.filter(
            user=user
        ).select_related('designation')
    
    @staticmethod
    def get_role_holders(designation_name):
        """Get all users holding a specific designation"""
        return GlobalsHoldsdesignation.objects.filter(
            designation__name=designation_name
        ).select_related('user', 'designation')
    
    @staticmethod
    def check_designation_exists(name):
        """Check if designation exists"""
        return GlobalsDesignation.objects.filter(name=name).exists()


class ModuleAccessSelectors:
    """Database query selectors for module access operations"""
    
    @staticmethod
    def get_module_access_by_designation(designation):
        """Get module access for a designation"""
        try:
            return GlobalsModuleaccess.objects.get(
                designation=designation
            )
        except GlobalsModuleaccess.DoesNotExist:
            return None
    
    @staticmethod
    def get_all_module_access():
        """Get all module access records"""
        return GlobalsModuleaccess.objects.all()
    
    @staticmethod
    def check_module_access_exists(designation):
        """Check if module access exists for designation"""
        return GlobalsModuleaccess.objects.filter(
            designation=designation
        ).exists()
    
    @staticmethod
    def get_next_module_access_id():
        """Get next available ID for module access"""
        max_id = GlobalsModuleaccess.objects.aggregate(
            Max('id')
        )['id__max']
        return (max_id or 0) + 1


class DepartmentSelectors:
    """Database query selectors for department operations"""
    
    @staticmethod
    def get_all_departments():
        """Get all departments"""
        return GlobalsDepartmentinfo.objects.all().order_by('id')
    
    @staticmethod
    def get_department_by_name(name):
        """Get department by name"""
        try:
            return GlobalsDepartmentinfo.objects.get(name=name)
        except GlobalsDepartmentinfo.DoesNotExist:
            return None
    
    @staticmethod
    def check_department_exists(name):
        """Check if department exists"""
        return GlobalsDepartmentinfo.objects.filter(name=name).exists()


class BatchSelectors:
    """Database query selectors for batch operations"""
    
    @staticmethod
    def get_all_batches():
        """Get all distinct batches by year"""
        return Batch.objects.distinct('year')
    
    @staticmethod
    def get_batch_by_programme_discipline_year(programme, discipline_acronym, year):
        """Get batch by programme, discipline and year"""
        try:
            return Batch.objects.filter(
                name=programme,
                discipline__acronym=discipline_acronym,
                year=year
            ).first()
        except Exception:
            return None
    
    @staticmethod
    def get_batches_by_year(year):
        """Get all batches for a specific year"""
        return Batch.objects.filter(year=year)
    
    @staticmethod
    def get_batches_by_discipline(discipline_acronym):
        """Get all batches for a specific discipline"""
        return Batch.objects.filter(discipline__acronym=discipline_acronym)


class ProgrammeSelectors:
    """Database query selectors for programme operations"""
    
    @staticmethod
    def get_all_programmes():
        """Get all programmes"""
        return Programme.objects.all().order_by('id')
    
    @staticmethod
    def get_programme_by_name(name):
        """Get programme by name"""
        try:
            return Programme.objects.get(name=name)
        except Programme.DoesNotExist:
            return None
    
    @staticmethod
    def get_programmes_by_category(category):
        """Get programmes by category"""
        return Programme.objects.filter(category=category)


class ExtrainfoSelectors:
    """Database query selectors for extra info operations"""
    
    @staticmethod
    def get_extrainfo_by_id(extrainfo_id):
        """Get extra info by ID"""
        try:
            return GlobalsExtrainfo.objects.get(id=extrainfo_id)
        except GlobalsExtrainfo.DoesNotExist:
            return None
    
    @staticmethod
    def get_extrainfo_by_user(user):
        """Get extra info for a user"""
        try:
            return GlobalsExtrainfo.objects.get(user=user)
        except GlobalsExtrainfo.DoesNotExist:
            return None
    
    @staticmethod
    def check_extrainfo_exists(extrainfo_id):
        """Check if extra info exists"""
        return GlobalsExtrainfo.objects.filter(id=extrainfo_id).exists()
