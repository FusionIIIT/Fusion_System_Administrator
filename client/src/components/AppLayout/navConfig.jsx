import {
  FaThLarge,
  FaBook,
  FaLayerGroup,
  FaUserAlt,
  FaChalkboardTeacher,
  FaUsersCog,
  FaKey,
  FaClone,
  FaUserShield,
  FaTasks,
  FaEdit,
  FaArchive,
  FaHdd,
  FaClock,
  FaTrashAlt,
} from "react-icons/fa";

export const NAV_SECTIONS = [
  { label: "Dashboard", icon: FaThLarge, to: "/dashboard" },
  { label: "User Directory", icon: FaBook, to: "/UserDirectory" },
  { label: "Upcoming Batches", icon: FaLayerGroup, to: "/UpcomingBatches" },
  {
    label: "User Management",
    icon: FaUserAlt,
    links: [
      { label: "Add Faculty", icon: FaChalkboardTeacher, to: "/UserManagement/CreateFaculty" },
      { label: "Add Staff", icon: FaUsersCog, to: "/UserManagement/CreateStaff" },
      { label: "Reset Password", icon: FaKey, to: "/UserManagement/ResetUserPassword" },
      { label: "Delete User", icon: FaTrashAlt, to: "/UserManagement/DeleteUser" },
    ],
  },
  {
    label: "Role Management",
    icon: FaClone,
    links: [
      { label: "Create Role", icon: FaUserShield, to: "/RoleManagement/CreateCustomRole" },
      { label: "Manage Role Access", icon: FaTasks, to: "/RoleManagement/ManageRoleAccess" },
      { label: "Edit Role", icon: FaEdit, to: "/RoleManagement/EditUserRole" },
    ],
  },
  {
    label: "Archive Management",
    icon: FaArchive,
    links: [
      { label: "Archive Students", icon: FaArchive, to: "/archive/students" },
      { label: "Archive Faculty", icon: FaArchive, to: "/archive/faculty" },
    ],
  },
  {
    label: "Backup Management",
    icon: FaHdd,
    links: [
      { label: "Backups", icon: FaHdd, to: "/backups" },
      { label: "Schedules", icon: FaClock, to: "/backups/schedules" },
    ],
  },
];

export const titleForPath = (pathname) => {
  for (const section of NAV_SECTIONS) {
    if (section.to === pathname) return section.label;
    if (section.links) {
      const match = section.links.find((l) => l.to === pathname);
      if (match) return match.label;
    }
  }
  return "Fusion System Administrator";
};
