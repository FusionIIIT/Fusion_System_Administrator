-- List login accounts that the bulk student import left half-registered.
--
-- Before bulk_import_users ran each row in a transaction, a CSV row that failed
-- part-way left its auth_user row behind without the rest of the registration:
-- globals_extrainfo, the "student" role in globals_holdsdesignation and
-- academic_information_student. Importing the corrected row then failed because
-- the username already existed.
--
-- This script only reads. It deletes nothing: review the rows, then decide per
-- account whether to complete the registration or remove the leftover by hand.
-- Staff and superuser accounts are left out, since the import never creates them
-- and admin or service accounts legitimately have no profile row. Accounts
-- without a profile row that are neither staff nor superuser are listed too, so
-- check each one before acting on it.
--
-- Safe to run any number of times.

select u.id                       as user_id,
       u.username,
       u.date_joined,
       e.id is not null           as has_extrainfo,
       exists (select 1
               from globals_holdsdesignation h
               join globals_designation d on d.id = h.designation_id
               where h.user_id = u.id and d.name = 'student') as has_student_role,
       s.id_id is not null        as has_student_record
from auth_user u
left join globals_extrainfo e on e.user_id = u.id
left join academic_information_student s on s.id_id = e.id
where not u.is_superuser
  and not u.is_staff
  and (e.id is null
       or (e.user_type = 'student'
           and (s.id_id is null
                or not exists (select 1
                               from globals_holdsdesignation h
                               join globals_designation d on d.id = h.designation_id
                               where h.user_id = u.id and d.name = 'student'))))
order by u.date_joined desc, u.username;
