import React, { useState, useEffect } from 'react';
import {
  TextInput,
  Select,
  Grid,
  Radio,
  FileInput,
  Progress,
  Button,
  Divider,
  Stack,
  Title,
  Group,
} from '@mantine/core';
import { DateInput } from '@mantine/dates';
import { FaDiceD6 } from 'react-icons/fa';
import { validateRequired } from '../../utils/validators';
import { TITLE_OPTIONS, PROGRAMMES, CATEGORIES, GENDER_OPTIONS } from '../../utils/constants';

const StudentForm = ({ 
  initialValues, 
  onSubmit, 
  departments, 
  batches,
  onDownloadSampleCSV,
  loading = false 
}) => {
  const [formValues, setFormValues] = useState(initialValues);
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const totalFields = Object.keys(formValues).length;
    const filledFields = Object.values(formValues).filter((value) => value).length;
    setProgress((filledFields / totalFields) * 100);
  }, [formValues]);

  const handleChange = (field, value) => {
    setFormValues((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleFileChange = (file) => {
    setFile(file);
  };

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    onSubmit({ formValues, file });
  };

  return (
    <>
      <Progress value={progress} color="blue" mb="md" />

      <Grid gutter="md">
        {/* Roll Number */}
        <Grid.Col span={6}>
          <TextInput
            label="Roll Number"
            placeholder="Enter roll number"
            value={formValues.username}
            onChange={(e) => handleChange('username', e.target.value)}
            required
          />
        </Grid.Col>

        {/* First Name */}
        <Grid.Col span={6}>
          <TextInput
            label="First Name"
            placeholder="Enter first name"
            value={formValues.first_name}
            onChange={(e) => handleChange('first_name', e.target.value)}
            required
          />
        </Grid.Col>

        {/* Last Name */}
        <Grid.Col span={6}>
          <TextInput
            label="Last Name"
            placeholder="Enter last name / NA"
            value={formValues.last_name}
            onChange={(e) => handleChange('last_name', e.target.value)}
            required
          />
        </Grid.Col>

        {/* Title */}
        <Grid.Col span={6}>
          <Select
            label="Title"
            placeholder="Select title"
            data={TITLE_OPTIONS}
            value={formValues.title}
            onChange={(value) => handleChange('title', value)}
          />
        </Grid.Col>

        {/* Department */}
        <Grid.Col span={12}>
          <Select
            label="Department"
            placeholder="Enter department"
            data={departments}
            value={`${formValues.department}`}
            onChange={(value) => handleChange('department', Number(value))}
          />
        </Grid.Col>

        {/* Gender */}
        <Grid.Col span={12}>
          <Radio.Group
            label="Gender"
            value={formValues.sex}
            onChange={(value) => handleChange('sex', value)}
            required
          >
            <Group spacing="sm" position="apart" mt="xs">
              {GENDER_OPTIONS.map((option) => (
                <Radio key={option.value} value={option.value} label={option.label} />
              ))}
            </Group>
          </Radio.Group>
        </Grid.Col>

        {/* Category */}
        <Grid.Col span={12}>
          <Select
            label="Category"
            placeholder="Select category"
            data={CATEGORIES}
            value={formValues.category}
            onChange={(value) => handleChange('category', value)}
            required
          />
        </Grid.Col>

        {/* Father's Name */}
        <Grid.Col span={6}>
          <TextInput
            label="Father's Name"
            placeholder="Enter father's name"
            value={formValues.father_name}
            onChange={(e) => handleChange('father_name', e.target.value)}
            required
          />
        </Grid.Col>

        {/* Mother's Name */}
        <Grid.Col span={6}>
          <TextInput
            label="Mother's Name"
            placeholder="Enter mother's name"
            value={formValues.mother_name}
            onChange={(e) => handleChange('mother_name', e.target.value)}
            required
          />
        </Grid.Col>

        {/* Programme */}
        <Grid.Col span={6}>
          <Select
            label="Programme"
            placeholder="Select programme"
            data={PROGRAMMES}
            value={formValues.programme}
            onChange={(value) => handleChange('programme', value)}
            required
          />
        </Grid.Col>

        {/* Batch */}
        <Grid.Col span={6}>
          <Select
            label="Batch"
            placeholder="Select batch"
            data={batches}
            value={`${formValues.batch}`}
            onChange={(value) => handleChange('batch', Number(value))}
            required
          />
        </Grid.Col>

        {/* Date of Birth */}
        <Grid.Col span={6}>
          <DateInput
            label="Date of Birth"
            placeholder="Select date of birth"
            value={formValues.dob}
            onChange={(value) => handleChange('dob', value)}
          />
        </Grid.Col>

        {/* Phone */}
        <Grid.Col span={6}>
          <TextInput
            label="Phone"
            placeholder="Enter phone number"
            value={formValues.phone}
            onChange={(e) => handleChange('phone', e.target.value)}
          />
        </Grid.Col>

        {/* Address */}
        <Grid.Col span={12}>
          <TextInput
            label="Address"
            placeholder="Enter address"
            value={formValues.address}
            onChange={(e) => handleChange('address', e.target.value)}
          />
        </Grid.Col>
      </Grid>

      {/* CSV Upload Section */}
      <Divider mt="xl" labelPosition="center" label={<FaDiceD6 size={12} />} />

      <Stack justify="center" align="center" mt="lg">
        <Title order={3}>Through CSV</Title>
        <FileInput
          value={file}
          onChange={handleFileChange}
          size="md"
          radius="xs"
          placeholder="Upload CSV"
          w="50%"
        />
        <Button onClick={() => handleSubmit()} w="50%" mt="sm" size="md">
          Create Students
        </Button>
        <Button
          variant="light"
          color="gray"
          onClick={onDownloadSampleCSV}
        >
          Download Sample CSV
        </Button>
      </Stack>
    </>
  );
};

export default StudentForm;
