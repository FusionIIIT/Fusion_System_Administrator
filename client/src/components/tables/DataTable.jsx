import React from 'react';
import { Table, ScrollArea, Text, Center, Loader } from '@mantine/core';

/**
 * DataTable Component
 * Reusable table component for displaying tabular data
 */

const DataTable = ({ 
  columns = [], 
  data = [], 
  loading = false,
  emptyMessage = 'No data available',
  striped = true,
  highlightOnHover = true,
  withBorder = true,
  verticalSpacing = 'sm',
}) => {
  if (loading) {
    return (
      <Center h={200}>
        <Loader size="md" color="blue" />
      </Center>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Center h={200}>
        <Text c="dimmed">{emptyMessage}</Text>
      </Center>
    );
  }

  const rows = data.map((row, rowIndex) => (
    <Table.Tr key={row.id || rowIndex}>
      {columns.map((col, colIndex) => {
        const cellData = typeof col.accessor === 'function' 
          ? col.accessor(row, rowIndex) 
          : row[col.accessor];

        return (
          <Table.Td key={colIndex}>
            {col.render ? col.render(cellData, row, rowIndex) : cellData}
          </Table.Td>
        );
      })}
    </Table.Tr>
  ));

  return (
    <ScrollArea>
      <Table
        striped={striped}
        highlightOnHover={highlightOnHover}
        withBorder={withBorder}
        verticalSpacing={verticalSpacing}
      >
        <Table.Thead>
          <Table.Tr>
            {columns.map((col, index) => (
              <Table.Th key={index} style={{ whiteSpace: 'nowrap' }}>
                {col.header}
              </Table.Th>
            ))}
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>{rows}</Table.Tbody>
      </Table>
    </ScrollArea>
  );
};

export default DataTable;
