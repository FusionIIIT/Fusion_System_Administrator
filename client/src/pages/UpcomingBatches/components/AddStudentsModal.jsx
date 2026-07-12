/* eslint-disable react/prop-types */
import { useState } from "react";
import { Modal, SegmentedControl, Stack } from "@mantine/core";
import ExcelUploadFlow from "./ExcelUploadFlow";
import ManualEntryForm from "./ManualEntryForm";

const AddStudentsModal = ({ opened, onClose, config, academicYear, onSaved }) => {
  const [mode, setMode] = useState("excel");

  const handleSaved = () => onSaved?.();

  return (
    <Modal opened={opened} onClose={onClose} size="80%" title={`Add ${config.label} Students`}>
      <Stack>
        <SegmentedControl
          value={mode}
          onChange={setMode}
          data={[
            { label: "Excel Upload", value: "excel" },
            { label: "Manual Entry", value: "manual" },
          ]}
        />
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
