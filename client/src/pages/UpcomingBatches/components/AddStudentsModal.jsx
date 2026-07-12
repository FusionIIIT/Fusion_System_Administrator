/* eslint-disable react/prop-types */
import { useState } from "react";
import { Group, Modal, SegmentedControl, Select, Stack, Text } from "@mantine/core";
import ExcelUploadFlow from "./ExcelUploadFlow";
import ManualEntryForm from "./ManualEntryForm";

const AddStudentsModal = ({ opened, onClose, config, onSaved }) => {
  const [mode, setMode] = useState("excel");
  const [academicYear, setAcademicYear] = useState(String(config.yearOptions[0]));

  const handleSaved = () => onSaved?.();

  return (
    <Modal opened={opened} onClose={onClose} size="80%" title={`Add ${config.label} Students`}>
      <Stack>
        <Group justify="space-between" align="flex-end">
          <SegmentedControl
            value={mode}
            onChange={setMode}
            data={[
              { label: "Excel Upload", value: "excel" },
              { label: "Manual Entry", value: "manual" },
            ]}
          />
          <Select
            label="Admission year"
            data={config.yearOptions.map(String)}
            value={academicYear}
            onChange={(value) => setAcademicYear(value || String(config.yearOptions[0]))}
            w={140}
          />
        </Group>
        <Text size="xs" c="dimmed">
          Students will be admitted into {config.label} batches for {academicYear}. A matching running batch must exist for that year.
        </Text>
        {mode === "excel" ? (
          <ExcelUploadFlow config={config} academicYear={academicYear} onSaved={handleSaved} onCancel={onClose} />
        ) : (
          <ManualEntryForm config={config} academicYear={academicYear} onSubmitted={handleSaved} onCancel={onClose} />
        )}
      </Stack>
    </Modal>
  );
};

export default AddStudentsModal;
