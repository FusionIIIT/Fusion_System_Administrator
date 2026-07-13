/* eslint-disable react/prop-types */
import { AppShell, Box, Burger, Button, Group, NavLink, ScrollArea, Text, Title } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { useLocation, useNavigate } from "react-router-dom";
import { FaSignOutAlt } from "react-icons/fa";
import { useAuth } from "../../context/AuthContext";
import { NAV_SECTIONS, titleForPath } from "./navConfig";

const AppLayout = ({ children }) => {
  const [opened, { toggle, close }] = useDisclosure();
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuth();

  const go = (to) => {
    navigate(to);
    close();
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{ width: 270, breakpoint: "sm", collapsed: { mobile: !opened } }}
      padding="lg"
    >
      <AppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Group gap="sm">
            <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
            <Title order={4} fw={600}>
              {titleForPath(pathname)}
            </Title>
          </Group>
          <Button variant="light" color="red" leftSection={<FaSignOutAlt size={14} />} onClick={handleLogout}>
            Logout
          </Button>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="md">
        <Box style={{ display: "flex", flexDirection: "column", height: "100%" }}>
          <Box mb="lg">
            <Text fw={800} size="lg" c="indigo" style={{ letterSpacing: "0.08em" }}>
              FUSION
            </Text>
            <Text size="xs" c="dimmed" tt="uppercase" fw={600} style={{ letterSpacing: "0.05em" }}>
              System Administrator
            </Text>
          </Box>
          <ScrollArea style={{ flex: 1 }} type="auto">
            {NAV_SECTIONS.map((section) =>
              section.links ? (
                <NavLink
                  key={section.label}
                  label={section.label}
                  leftSection={<section.icon size={16} />}
                  defaultOpened={section.links.some((l) => l.to === pathname)}
                  childrenOffset={26}
                >
                  {section.links.map((link) => (
                    <NavLink
                      key={link.to}
                      label={link.label}
                      leftSection={<link.icon size={14} />}
                      active={pathname === link.to}
                      onClick={() => go(link.to)}
                    />
                  ))}
                </NavLink>
              ) : (
                <NavLink
                  key={section.to}
                  label={section.label}
                  leftSection={<section.icon size={16} />}
                  active={pathname === section.to}
                  onClick={() => go(section.to)}
                />
              ),
            )}
          </ScrollArea>
        </Box>
      </AppShell.Navbar>

      <AppShell.Main bg="gray.0">{children}</AppShell.Main>
    </AppShell>
  );
};

export default AppLayout;
