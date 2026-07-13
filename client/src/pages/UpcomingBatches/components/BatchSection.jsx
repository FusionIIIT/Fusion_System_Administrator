/* eslint-disable react/prop-types */
import { useMemo, useState } from "react";
import { Button, Center, Group, Loader, Modal, Paper, Select, Text, TextInput } from "@mantine/core";
import { FaFilter, FaPlus, FaSearch, FaUserPlus } from "react-icons/fa";
import { notifications } from "@mantine/notifications";
import { deleteBatch as deleteBatchApi } from "../../../api/UpcomingBatches";
import BatchTable from "./BatchTable";
import AddBatchModal from "./AddBatchModal";
import AddStudentsModal from "./AddStudentsModal";
import StudentListModal from "./StudentListModal";

const BatchSection = ({ config, batches, disciplines, curriculums, loading, refresh }) => {
  const [search, setSearch] = useState("");
  const [filterYear, setFilterYear] = useState("all");
  const [addBatchOpen, setAddBatchOpen] = useState(false);
  const [addStudentsOpen, setAddStudentsOpen] = useState(false);
  const [viewBatch, setViewBatch] = useState(null);
  const [pendingDelete, setPendingDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const filtered = useMemo(() => {
    let list = batches;
    if (filterYear !== "all") list = list.filter((b) => String(b.year) === filterYear);
    const term = search.trim().toLowerCase();
    if (term) {
      list = list.filter(
        (b) =>
          b.name.toLowerCase().includes(term) ||
          b.discipline.toLowerCase().includes(term) ||
          String(b.year).includes(term),
      );
    }
    return list;
  }, [batches, search, filterYear]);

  const yearOptions = [
    { value: "all", label: "All years" },
    ...config.yearOptions.map((y) => ({ value: String(y), label: String(y) })),
  ];

  const confirmDelete = async () => {
    setDeleting(true);
    try {
      const res = await deleteBatchApi(pendingDelete.batch_id);
      if (res.success) {
        notifications.show({ title: "Deleted", message: res.message, color: "green" });
        setPendingDelete(null);
        refresh();
      } else {
        notifications.show({ title: "Cannot delete", message: res.message, color: "red" });
      }
    } catch (error) {
      notifications.show({ title: "Error", message: error.response?.data?.message || "Failed to delete batch.", color: "red" });
    } finally {
      setDeleting(false);
    }
  };

  return (
    <Paper p="lg" radius="md" withBorder>
      <Group justify="space-between" mb="md" wrap="wrap">
        <TextInput
          placeholder="Search batches"
          leftSection={<FaSearch size={12} />}
          value={search}
          onChange={(e) => setSearch(e.currentTarget.value)}
          w={260}
        />
        <Group>
          <Select
            leftSection={<FaFilter size={12} />}
            data={yearOptions}
            value={filterYear}
            onChange={(value) => setFilterYear(value || "all")}
            w={150}
            aria-label="Filter by year"
          />
          <Button variant="light" leftSection={<FaPlus size={12} />} onClick={() => setAddBatchOpen(true)}>
            Add Batch
          </Button>
          <Button leftSection={<FaUserPlus size={12} />} onClick={() => setAddStudentsOpen(true)}>
            Add Students
          </Button>
        </Group>
      </Group>

      {loading ? (
        <Center h={200}><Loader /></Center>
      ) : (
        <BatchTable batches={filtered} onView={setViewBatch} onDelete={setPendingDelete} />
      )}

      <AddBatchModal
        opened={addBatchOpen}
        onClose={() => setAddBatchOpen(false)}
        config={config}
        disciplines={disciplines}
        curriculums={curriculums}
        onCreated={refresh}
      />
      <AddStudentsModal
        opened={addStudentsOpen}
        onClose={() => setAddStudentsOpen(false)}
        config={config}
        onSaved={refresh}
      />
      <StudentListModal opened={!!viewBatch} onClose={() => setViewBatch(null)} batch={viewBatch} />

      <Modal opened={!!pendingDelete} onClose={() => setPendingDelete(null)} title="Delete batch" centered>
        <Text size="sm">
          Delete batch {pendingDelete?.name} · {pendingDelete?.discipline} · {pendingDelete?.year}? This cannot be undone.
        </Text>
        <Group justify="flex-end" mt="md">
          <Button variant="default" onClick={() => setPendingDelete(null)}>Cancel</Button>
          <Button color="red" onClick={confirmDelete} loading={deleting}>Delete</Button>
        </Group>
      </Modal>
    </Paper>
  );
};

export default BatchSection;
