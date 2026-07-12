/* eslint-disable react/prop-types */
import { Badge, Button, Group, Table, Text } from "@mantine/core";
import { FaEye, FaTrash } from "react-icons/fa";

const BatchTable = ({ batches, onView, onDelete }) => {
  if (!batches.length) {
    return (
      <Text ta="center" c="dimmed" py="xl">
        No batches for this category. Create one to get started.
      </Text>
    );
  }

  return (
    <Table.ScrollContainer minWidth={720}>
      <Table striped highlightOnHover verticalSpacing="sm">
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Batch</Table.Th>
            <Table.Th>Discipline</Table.Th>
            <Table.Th>Year</Table.Th>
            <Table.Th>Curriculum</Table.Th>
            <Table.Th>Seats</Table.Th>
            <Table.Th>Actions</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {batches.map((batch) => (
            <Table.Tr key={batch.batch_id}>
              <Table.Td fw={600}>{batch.name}</Table.Td>
              <Table.Td>{batch.discipline}</Table.Td>
              <Table.Td>{batch.year}</Table.Td>
              <Table.Td>
                <Text size="sm" c="dimmed" lineClamp={1} maw={220}>
                  {batch.curriculum}
                </Text>
              </Table.Td>
              <Table.Td>
                <Group gap="xs">
                  <Badge color="blue" variant="light">{batch.filled_seats} filled</Badge>
                  <Badge color="teal" variant="light">{batch.available_seats} left</Badge>
                  <Text size="xs" c="dimmed">/ {batch.total_seats}</Text>
                </Group>
              </Table.Td>
              <Table.Td>
                <Group gap="xs">
                  <Button size="xs" variant="light" leftSection={<FaEye size={12} />} onClick={() => onView(batch)}>
                    Students
                  </Button>
                  <Button size="xs" variant="light" color="red" leftSection={<FaTrash size={12} />} onClick={() => onDelete(batch)}>
                    Delete
                  </Button>
                </Group>
              </Table.Td>
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>
    </Table.ScrollContainer>
  );
};

export default BatchTable;
