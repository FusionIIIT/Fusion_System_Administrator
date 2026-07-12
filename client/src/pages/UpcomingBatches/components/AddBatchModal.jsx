/* eslint-disable react/prop-types */
import { useMemo, useState } from "react";
import { Button, Group, Modal, NumberInput, Select, Stack } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { createBatch } from "../../../api/UpcomingBatches";

const AddBatchModal = ({ opened, onClose, config, disciplines, curriculums, onCreated }) => {
  const [programme, setProgramme] = useState(null);
  const [disciplineId, setDisciplineId] = useState(null);
  const [year, setYear] = useState(String(config.yearOptions[0]));
  const [totalSeats, setTotalSeats] = useState(60);
  const [curriculumId, setCurriculumId] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const disciplineOptions = useMemo(() => {
    const allowed = programme ? config.disciplineMap[programme] || [] : [];
    return disciplines
      .filter((d) => allowed.includes(d.name))
      .map((d) => ({ value: String(d.id), label: `${d.name} (${d.acronym})` }));
  }, [programme, disciplines, config]);

  const curriculumOptions = useMemo(
    () => curriculums.map((c) => ({ value: String(c.id), label: `${c.name} v${c.version}` })),
    [curriculums],
  );

  const reset = () => {
    setProgramme(null);
    setDisciplineId(null);
    setYear(String(config.yearOptions[0]));
    setTotalSeats(60);
    setCurriculumId(null);
  };

  const handleSubmit = async () => {
    if (!programme || !disciplineId || !year || !totalSeats) {
      notifications.show({ title: "Missing fields", message: "Programme, discipline, year and seats are required.", color: "red" });
      return;
    }
    setSubmitting(true);
    try {
      const res = await createBatch({
        programme,
        discipline: Number(disciplineId),
        year: Number(year),
        total_seats: Number(totalSeats),
        curriculum: curriculumId ? Number(curriculumId) : null,
      });
      if (res.success) {
        notifications.show({ title: "Success", message: res.message, color: "green" });
        reset();
        onCreated?.();
        onClose();
      } else {
        notifications.show({ title: "Error", message: res.message, color: "red" });
      }
    } catch (error) {
      notifications.show({ title: "Error", message: error.response?.data?.message || "Failed to create batch.", color: "red" });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal opened={opened} onClose={onClose} title={`Add ${config.label} Batch`} centered>
      <Stack>
        <Select
          label="Programme"
          placeholder="Select programme"
          data={config.programmeOptions}
          value={programme}
          onChange={(value) => {
            setProgramme(value);
            setDisciplineId(null);
          }}
          required
        />
        <Select
          label="Discipline"
          placeholder={programme ? "Select discipline" : "Select a programme first"}
          data={disciplineOptions}
          value={disciplineId}
          onChange={setDisciplineId}
          disabled={!programme}
          searchable
          required
        />
        <Select
          label="Batch Year"
          data={config.yearOptions.map(String)}
          value={year}
          onChange={setYear}
          required
        />
        <NumberInput label="Total Seats" min={1} value={totalSeats} onChange={setTotalSeats} required />
        <Select
          label="Curriculum (optional)"
          placeholder="Assign a working curriculum"
          data={curriculumOptions}
          value={curriculumId}
          onChange={setCurriculumId}
          searchable
          clearable
        />
        <Group justify="flex-end" mt="sm">
          <Button variant="default" onClick={onClose}>Cancel</Button>
          <Button onClick={handleSubmit} loading={submitting}>Create Batch</Button>
        </Group>
      </Stack>
    </Modal>
  );
};

export default AddBatchModal;
