import { useState } from "react";
import {
  Alert,
  Button,
  Container,
  Group,
  Modal,
  Paper,
  Select,
  SimpleGrid,
  Stack,
  Text,
} from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { FaSearch, FaTrashAlt } from "react-icons/fa";
import PageHeader from "../../components/PageHeader/PageHeader";
import { deleteAllocation, fetchAllocationSummary } from "../../api/Allocations";

const PROGRAMMES = [
  { value: "UG", label: "Undergraduate (UG)" },
  { value: "PG", label: "Postgraduate (PG)" },
  { value: "PHD", label: "PhD" },
];

const FIRST_BATCH = 2018;
const THIS_YEAR = new Date().getFullYear();
const BATCHES = Array.from({ length: THIS_YEAR - FIRST_BATCH + 1 }, (_, i) => String(THIS_YEAR - i));
const SEMESTERS = Array.from({ length: 16 }, (_, i) => String(i + 1));

const COUNTS = [
  ["students", "Students"],
  ["allotted_courses", "Allotted courses"],
  ["registrations", "Published registrations"],
  ["replacement_links", "Re-take links"],
  ["pre_registrations", "Pre-registrations (kept)"],
];

const DeleteAllocationPage = () => {
  const [programme, setProgramme] = useState("UG");
  const [batch, setBatch] = useState(null);
  const [semester, setSemester] = useState(null);
  const [summary, setSummary] = useState(null);
  const [checking, setChecking] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const selection = { batch, semester, programme };
  const label = `Batch ${batch}, semester ${semester} (${programme})`;

  const reset = (setter) => (value) => {
    setter(value);
    setSummary(null);
  };

  const check = async () => {
    setChecking(true);
    try {
      setSummary(await fetchAllocationSummary(selection));
    } catch (error) {
      notifications.show({
        title: "Error",
        message: error.response?.data?.message || "Could not read the allocation.",
        color: "red",
      });
    } finally {
      setChecking(false);
    }
  };

  const remove = async () => {
    setDeleting(true);
    try {
      const result = await deleteAllocation(selection);
      notifications.show({ title: "Allocation deleted", message: result.message, color: "green" });
      setConfirming(false);
      setSummary(await fetchAllocationSummary(selection));
    } catch (error) {
      notifications.show({
        title: "Not deleted",
        message: error.response?.data?.message || "The allocation could not be deleted.",
        color: "red",
      });
      setConfirming(false);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <Container size="md">
      <PageHeader
        title="Delete Allocation"
        subtitle="Remove one batch and semester's course allocation so it can be allocated again. Pre-registration is kept."
      />

      <Paper withBorder radius="md" p="lg">
        <Stack>
          <SimpleGrid cols={{ base: 1, sm: 3 }}>
            <Select label="Programme" data={PROGRAMMES} value={programme} onChange={reset(setProgramme)} allowDeselect={false} />
            <Select label="Batch" placeholder="Select batch" data={BATCHES} value={batch} onChange={reset(setBatch)} searchable />
            <Select label="Semester" placeholder="Select semester" data={SEMESTERS} value={semester} onChange={reset(setSemester)} />
          </SimpleGrid>
          <Group justify="flex-end">
            <Button leftSection={<FaSearch />} onClick={check} loading={checking} disabled={!batch || !semester}>
              Check allocation
            </Button>
          </Group>
        </Stack>
      </Paper>

      {summary && (
        <Paper withBorder radius="md" p="lg" mt="lg">
          <Stack>
            <Text fw={600}>{label}</Text>
            <SimpleGrid cols={{ base: 2, sm: 5 }}>
              {COUNTS.map(([key, name]) => (
                <Stack key={key} gap={0}>
                  <Text size="xl" fw={700}>{summary[key]}</Text>
                  <Text size="xs" c="dimmed">{name}</Text>
                </Stack>
              ))}
            </SimpleGrid>
            {summary.can_delete ? (
              <Group justify="flex-end">
                <Button color="red" leftSection={<FaTrashAlt />} onClick={() => setConfirming(true)}>
                  Delete allocation
                </Button>
              </Group>
            ) : (
              <Alert color="gray" variant="light">{summary.reason}</Alert>
            )}
          </Stack>
        </Paper>
      )}

      <Modal opened={confirming} onClose={() => !deleting && setConfirming(false)} title="Delete allocation" centered>
        {summary && (
          <Stack>
            <Text size="sm">
              Delete the allocation of {label}? This removes {summary.allotted_courses} allotted courses for{" "}
              {summary.students} students, their {summary.registrations} published registrations
              {summary.replacement_links ? ` and ${summary.replacement_links} re-take links` : ""}.
            </Text>
            <Text size="sm">
              Pre-registration ({summary.pre_registrations} rows) is kept, so the batch can be allocated
              again in Fusion. This cannot be undone.
            </Text>
            <Group justify="flex-end">
              <Button variant="default" onClick={() => setConfirming(false)} disabled={deleting}>
                Cancel
              </Button>
              <Button color="red" onClick={remove} loading={deleting}>
                Delete
              </Button>
            </Group>
          </Stack>
        )}
      </Modal>
    </Container>
  );
};

export default DeleteAllocationPage;
