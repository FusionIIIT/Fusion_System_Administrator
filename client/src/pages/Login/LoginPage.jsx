import React, { useState } from "react";
import { useForm } from "@mantine/form";
import { TextInput, Button, Paper, Container, Title, Text, Alert, Group, Code, Accordion } from "@mantine/core";
import { useNavigate } from "react-router-dom";
import { handleLogin } from "../../services/authServices.jsx";
import { useAuth } from "../../context/AuthContext";

const LoginPage = () => {
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const form = useForm({
    initialValues: { email: "admin@iiitdmj.ac.in", password: "Admin@123" },
    validate: {
      email: (value) => (/^\S+@\S+\.\S+$/.test(value) ? null : "Invalid email format"),
      password: (value) => (value.length >= 6 ? null : "Password must be at least 6 characters"),
    },
  });

  const navigate = useNavigate();
  const { login } = useAuth();

  const onLogin = async (values) => {
    setError(null);
    setLoading(true);

    try {
      const user = await handleLogin(values.email, values.password);
      console.log("Logged in user:", user);
      login();
      navigate("/UserDirectory", { replace: true });
    } catch (error) {
      console.error("Login error:", error.message);
      setError(error.message || "Login failed. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  const fusionCredentials = [
    { email: 'admin@iiitdmj.ac.in', password: 'Admin@123', role: 'System Administrator' },
    { email: 'system.admin@iiitdmj.ac.in', password: 'Admin@123', role: 'System Admin' },
    { email: 'faculty@iiitdmj.ac.in', password: 'Faculty@123', role: 'Faculty Member' },
    { email: 'student@iiitdmj.ac.in', password: 'Student@123', role: 'Student' }
  ];

  return (
    <Container size={500} my={40}>
      <Title align="center" order={1}>Fusion ERP System Administrator</Title>
      <Text color="dimmed" align="center" mb="md">Login to access the system</Text>

      {error && (
        <Alert color="red" mb="md" title="Login Failed">
          {error}
        </Alert>
      )}

      <Paper withBorder shadow="md" p={30} mt={30} radius="md">
        <form onSubmit={form.onSubmit(onLogin)}>
          <TextInput
            label="Email"
            placeholder="your.email@iiitdmj.ac.in"
            {...form.getInputProps("email")}
            required
            disabled={loading}
          />
          <TextInput
            label="Password"
            placeholder="Enter your password"
            type="password"
            mt="md"
            {...form.getInputProps("password")}
            required
            disabled={loading}
          />
          <Button type="submit" fullWidth mt="xl" loading={loading} size="md">
            Login
          </Button>
        </form>

        <Accordion mt="lg" variant="contained">
          <Accordion.Item value="credentials">
            <Accordion.Control>🔑 Fusion IIITDMJ Development Credentials</Accordion.Control>
            <Accordion.Panel>
              <Text size="sm" mb="sm">Use these credentials for development testing:</Text>
              {fusionCredentials.map((cred, index) => (
                <Group key={index} mt="xs" position="apart">
                  <div>
                    <Text size="xs" color="dimmed">{cred.role}</Text>
                    <Code size="sm">{cred.email}</Code>
                  </div>
                  <Code size="sm">{cred.password}</Code>
                </Group>
              ))}
            </Accordion.Panel>
          </Accordion.Item>
        </Accordion>
      </Paper>
    </Container>
  );
};

export default LoginPage;
