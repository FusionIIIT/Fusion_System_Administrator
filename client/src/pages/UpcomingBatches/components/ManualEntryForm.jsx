/* eslint-disable react/prop-types */
import { useMemo, useState } from "react";
import { Button, Divider, Grid, Group, NumberInput, Select, Stack, Text, Textarea, TextInput, Title } from "@mantine/core";
import { DateInput } from "@mantine/dates";
import { notifications } from "@mantine/notifications";
import { addSingleStudent } from "../../../api/UpcomingBatches";
import { EMPTY_MANUAL_FORM, MANUAL_SECTIONS } from "../config/studentFields";
import { SPECIALIZATION_OPTIONS } from "../config/programmeConfig";

const toDateString = (value) => {
  if (!value) return "";
  const d = value instanceof Date ? value : new Date(value);
  return Number.isNaN(d.getTime()) ? "" : d.toISOString().slice(0, 10);
};

const ManualEntryForm = ({ config, academicYear, onSubmitted, onCancel }) => {
  const [form, setForm] = useState(EMPTY_MANUAL_FORM);
  const [submitting, setSubmitting] = useState(false);

  const disciplineOptions = useMemo(
    () => [...new Set(Object.values(config.disciplineMap).flat())],
    [config],
  );
  const setField = (key, value) => setForm((prev) => ({ ...prev, [key]: value }));

  const renderField = (field) => {
    if (field.specializationOnly && !config.showSpecialization) return null;
    if (field.visibleWhen && !field.visibleWhen(form)) return null;

    const common = {
      label: field.label,
      required: field.required,
      value: form[field.key] ?? "",
      withAsterisk: field.required,
    };

    let input;
    if (field.type === "textarea") {
      input = <Textarea {...common} autosize minRows={2} onChange={(e) => setField(field.key, e.currentTarget.value)} />;
    } else if (field.type === "number") {
      input = <NumberInput {...common} value={form[field.key]} onChange={(v) => setField(field.key, v)} />;
    } else if (field.type === "date") {
      input = <DateInput {...common} value={form[field.key]} valueFormat="YYYY-MM-DD" onChange={(v) => setField(field.key, v)} />;
    } else if (field.type === "select") {
      input = <Select {...common} data={field.options} onChange={(v) => setField(field.key, v)} clearable searchable />;
    } else if (field.type === "discipline") {
      input = <Select {...common} data={disciplineOptions} onChange={(v) => setField(field.key, v)} searchable />;
    } else if (field.type === "specialization") {
      input = <Select {...common} data={SPECIALIZATION_OPTIONS} onChange={(v) => setField(field.key, v)} searchable clearable />;
    } else {
      input = <TextInput {...common} onChange={(e) => setField(field.key, e.currentTarget.value)} />;
    }

    return (
      <Grid.Col span={{ base: 12, sm: 6, md: 4 }} key={field.key}>
        {input}
      </Grid.Col>
    );
  };

  const handleSubmit = async () => {
    const missing = MANUAL_SECTIONS.flatMap((s) => s.fields).filter(
      (f) => f.required && !(f.specializationOnly && !config.showSpecialization) && !String(form[f.key] ?? "").trim(),
    );
    if (missing.length) {
      notifications.show({ title: "Missing fields", message: `Fill: ${missing.map((f) => f.label).join(", ")}`, color: "red" });
      return;
    }

    setSubmitting(true);
    try {
      const res = await addSingleStudent({
        ...form,
        dob: toDateString(form.dob),
        programme_type: config.programmeType,
        academic_year: academicYear,
      });
      if (res.success) {
        notifications.show({ title: "Success", message: res.message, color: "green" });
        setForm(EMPTY_MANUAL_FORM);
        onSubmitted?.();
      } else {
        notifications.show({ title: "Error", message: res.message, color: "red" });
      }
    } catch (error) {
      notifications.show({ title: "Error", message: error.response?.data?.message || "Failed to add student.", color: "red" });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Stack>
      {MANUAL_SECTIONS.map((section) => (
        <div key={section.title}>
          <Title order={6} mb="xs">{section.title}</Title>
          <Grid>{section.fields.map(renderField)}</Grid>
          <Divider mt="md" />
        </div>
      ))}
      <Text size="xs" c="dimmed">
        Batch is derived from the discipline and category. A matching running batch must exist for the selected year.
      </Text>
      <Group justify="flex-end">
        <Button variant="default" onClick={onCancel}>Cancel</Button>
        <Button onClick={handleSubmit} loading={submitting}>Add Student</Button>
      </Group>
    </Stack>
  );
};

export default ManualEntryForm;
