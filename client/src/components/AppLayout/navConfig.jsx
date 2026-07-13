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

export const NAV_GROUPS = [
  {
    section: "Overview",
    items: [{ label: "Dashboard", icon: FaThLarge, to: "/dashboard" }],
  },
  {
    section: "Academics",
    items: [
      { label: "User Directory", icon: FaBook, to: "/UserDirectory" },
      { label: "Upcoming Batches", icon: FaLayerGroup, to: "/UpcomingBatches" },
    ],
  },
  {
    section: "Management",
    items: [
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
    ],
  },
  {
    section: "System",
    items: [
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
    ],
  },
];

// Flat list of every navigable destination — powers the sidebar search.
export const ALL_LINKS = NAV_GROUPS.flatMap((group) =>
  group.items.flatMap((item) =>
    item.links
      ? item.links.map((link) => ({ ...link, parent: item.label }))
      : [{ label: item.label, icon: item.icon, to: item.to, parent: group.section }],
  ),
);

export const titleForPath = (pathname) => {
  const match = ALL_LINKS.find((l) => l.to === pathname);
  return match ? match.label : "Fusion System Administrator";
};
