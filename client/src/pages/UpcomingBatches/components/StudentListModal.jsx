/* eslint-disable react/prop-types */
import { useEffect, useMemo, useState } from "react";
import { Badge, Center, Loader, Modal, Table, Text, TextInput } from "@mantine/core";
import { FaSearch } from "react-icons/fa";
import { notifications } from "@mantine/notifications";
import { fetchBatchStudents } from "../../../api/UpcomingBatches";
import { ROSTER_COLUMNS } from "../config/studentFields";

const StudentListModal = ({ opened, onClose, batch }) => {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState("");

  useEffect(() => {
    if (!opened || !batch) return;
    setQuery("");
    setLoading(true);
    fetchBatchStudents(batch.batch_id)
      .then((data) => setStudents(data.students || []))
      .catch(() => notifications.show({ title: "Error", message: "Failed to load students.", color: "red" }))
      .finally(() => setLoading(false));
  }, [opened, batch]);

  const filtered = useMemo(() => {
    const term = query.trim().toLowerCase();
    if (!term) return students;
    return students.filter(
      (s) => (s.name || "").toLowerCase().includes(term) || (s.roll_number || "").toLowerCase().includes(term),
    );
  }, [students, query]);

  return (
    <Modal
      opened={opened}
      onClose={onClose}
      size="90%"
      title={batch ? `${batch.name} · ${batch.discipline} · ${batch.year}` : "Students"}
    >
      <TextInput
        mb="md"
        placeholder="Search by name or roll number"
        leftSection={<FaSearch size={12} />}
        value={query}
        onChange={(e) => setQuery(e.currentTarget.value)}
        size="md"
      />
      {loading ? (
        <Center h={200}><Loader /></Center>
      ) : filtered.length === 0 ? (
        <Text ta="center" c="dimmed" py="xl">No students found.</Text>
      ) : (
        <>
          <Text size="sm" c="dimmed" mb="xs">{filtered.length} student(s)</Text>
          <Table.ScrollContainer minWidth={900}>
            <Table striped highlightOnHover verticalSpacing="xs" stickyHeader>
              <Table.Thead>
                <Table.Tr>
                  {ROSTER_COLUMNS.map((col) => (
                    <Table.Th key={col.key}>{col.label}</Table.Th>
                  ))}
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {filtered.map((student) => (
                  <Table.Tr key={student.id}>
                    {ROSTER_COLUMNS.map((col) =>
                      col.key === "status_display" ? (
                        <Table.Td key={col.key}>
                          <Badge color={student.reported_status === "REPORTED" ? "green" : "gray"} variant="light">
                            {student.status_display}
                          </Badge>
                        </Table.Td>
                      ) : (
                        <Table.Td key={col.key}>{student[col.key] || "-"}</Table.Td>
                      ),
                    )}
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          </Table.ScrollContainer>
        </>
      )}
    </Modal>
  );
};

export default StudentListModal;
