import { useState, useEffect } from 'react';
import {
    TextInput,
    Select,
    Button,
    Grid,
    Group,
    Container,
    NumberInput,
    Radio,
    rem,
    Divider,
    Progress,
    Flex,
    Paper,
} from '@mantine/core';
import { FaCheck, FaTimes } from 'react-icons/fa';
import { showNotification } from '@mantine/notifications';
import { DateInput } from '@mantine/dates';
import { getAllDesignations, getAllDepartments } from '../../api/Roles';
import { createFaculty } from '../../api/Users';
import PageHeader from '../../components/PageHeader/PageHeader';

const FacultyCreationPage = () => {
    const xIcon = <FaTimes style={{ width: rem(20), height: rem(20) }} />;
    const checkIcon = <FaCheck style={{ width: rem(20), height: rem(20) }} />;

    const [formValues, setFormValues] = useState({
        username: '',
        first_name: '',
        last_name: '',
        department: '',
        title: '',
        designation: '',
        sex: '',
        dob: null,
        phone: '',
        address: '',
    });

    const [progress, setProgress] = useState(0);
    const [roles, setRoles] = useState([]);
    const [departments, setDepartments] = useState([]);
    const [, setLoading] = useState(false);
    const [, setErrorMessage] = useState('');

    useEffect(() => {
        const totalFields = Object.keys(formValues).length;
        const filledFields = Object.values(formValues).filter((value) => value).length;
        setProgress((filledFields / totalFields) * 100);
    }, [formValues]);

    const handleChange = (field, value) => {
        setFormValues((prev) => ({ ...prev, [field]: value }));
        setErrorMessage('');
    };

    const fetchFacultyDesignations = async () => {
        try {
            let all_designations = [];
            const designationData = {
                category: 'faculty',
                basic: true,
            }
            const response = await getAllDesignations(designationData);
            console.log(response)
            for(let i=0; i<response.length; i++){
                all_designations[i] = {value: `${response[i].id}`, label: response[i].name}
            }
            setRoles(all_designations);
        } catch {
            showNotification({
                title: 'Error',
                icon: xIcon,
                position: "top-center",
                withCloseButton: true,
                message: 'An error occurred while fetching designations.',
                color: 'red',
            });
        }
    }

    const fetchDepartments = async () => {
        try {
            let all_departments = [];
            const response = await getAllDepartments();
            console.log(response)
            for(let i=0; i<response.length; i++){
                all_departments[i] = {value: `${response[i].id}`, label: response[i].name}
            }
            setDepartments(all_departments);
        } catch {
            showNotification({
                title: 'Error',
                icon: xIcon,
                position: "top-center",
                withCloseButton: true,
                message: 'An error occurred while fetching departments.',
                color: 'red',
            });
        }
    }

    const handleSubmit = async () => {
        try {
            setLoading(true);

            // ✅ CHANGE MADE: Format dob to "YYYY-MM-DD" string before sending to API
            const formattedFormValues = {
                ...formValues,
                dob: formValues.dob ? formValues.dob.toISOString().split('T')[0] : null,
            };

            await createFaculty(formattedFormValues);

            showNotification({
                icon: checkIcon,
                title: "Success",
                position: "top-center",
                withCloseButton: true,
                autoClose: 5000,
                message: "Faculty Created Successfully.",
                color: "green",
            });
            console.log('Form Submitted', formValues);
            setFormValues({
                username: '',
                first_name: '',
                last_name: '',
                department: '',
                title: '',
                designation: '',
                sex: '',
                dob: null,
                phone: '',
                address: '',
            });
        } catch {
            showNotification({
                title: 'Error',
                icon: xIcon,
                position: "top-center",
                withCloseButton: true,
                message: 'An error occurred while creating faculty.',
                color: 'red',
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(()=>{
        fetchFacultyDesignations();
        fetchDepartments();
    // eslint-disable-next-line react-hooks/exhaustive-deps
    },[])

    useEffect(() => {
        const handleKeyDown = (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                handleSubmit();
            }
        };

        window.addEventListener('keydown', handleKeyDown);

        return () => {
            window.removeEventListener('keydown', handleKeyDown);
        };
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [formValues]);

    return (
        <Container size="lg">
            <PageHeader title="Add Faculty" />
            <Paper shadow="xl" radius="lg" p="xl">
                <Divider my="sm" />

                {/* Progress Bar */}
                <Progress value={progress} color="blue" mb="md" />

                <Grid gutter="md">
                    <Grid.Col span={12}>
                        <TextInput
                            label="Username"
                            placeholder="Enter username(20 letters)"
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
                            placeholder="Enter last name"
                            value={formValues.last_name}
                            onChange={(e) => handleChange('last_name', e.target.value)}
                            required
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

                    {/* Title */}
                    <Grid.Col span={6}>
                        <Select
                            label="Title"
                            placeholder="Select title"
                            data={['Dr.', 'Mr.', 'Mrs.', 'Ms.']}
                            value={formValues.title}
                            onChange={(value) => handleChange('title', value)}
                        />
                    </Grid.Col>

                    {/* Designation */}
                    <Grid.Col span={6}>
                        <Select
                            label="Designation"
                            placeholder="Select designation"
                            data={roles}
                            value={`${formValues.designation}`}
                            onChange={(value) => handleChange('designation', Number(value))}
                            required
                        />
                    </Grid.Col>

                    {/* Gender */}
                    <Grid.Col span={12}>
                        <Radio.Group
                            label="Gender"
                            value={formValues.sex}
                            onChange={(value) => handleChange('sex', value)}
                            required
                            styles={{
                                label: { marginRight: '1rem' },
                            }}
                        >
                            <Group spacing="sm" position="apart" mt="xs">
                                <Radio value="male" label="Male" />
                                <Radio value="female" label="Female" />
                                {/* <Radio value="other" label="Other" /> */}
                            </Group>
                        </Radio.Group>
                    </Grid.Col>

                    {/* Date of Birth */}
                    <Grid.Col span={6}>
                        <DateInput
                            value={formValues.dob}
                            onChange={(value) => handleChange('dob', value)}
                            label="Date of Birth"
                            placeholder="Pick a date"
                        />
                    </Grid.Col>

                    {/* Phone Number */}
                    <Grid.Col span={6}>
                        <NumberInput
                            label="Phone Number"
                            placeholder="Enter phone number"
                            value={formValues.phone}
                            onChange={(value) => handleChange('phone', value)}
                            hideControls
                        />
                    </Grid.Col>

                    <Grid.Col span={12}>
                        <TextInput
                            label="Address"
                            placeholder="Enter address"
                            value={formValues.address}
                            onChange={(e) => handleChange('address', e.target.value)}
                        />
                    </Grid.Col>
                </Grid>

                {/* Create Button */}
                <Flex
                    gap="md"
                    justify="center"
                    align="center"
                    direction="row"
                    wrap="wrap"
                    mt="xl"
                >
                    <Button onClick={handleSubmit} color="blue" size="md">
                        Add Faculty
                    </Button>
                </Flex>
            </Paper>
        </Container>
    );
};

export default FacultyCreationPage;
