/* eslint-disable react/prop-types */
import { useState, useMemo } from "react";
import {
    Tabs, Card, Text, ScrollArea, Container, Title,
    Button, TextInput, MultiSelect, Grid, Paper,
    Divider, Checkbox, Group, Badge, Center, Modal,
    rem
} from "@mantine/core";
import { debounce } from "lodash";
import { FaCheck } from "react-icons/fa";
import { showNotification } from "@mantine/notifications";
import PageHeader from "../../components/PageHeader/PageHeader";

const STATIC_FACULTY = [
    {
        id: "snsharma",
        username: "snsharma",
        full_name: "Prof. Sanjeev Narayan Sharma",
        user_type: "faculty",
        department: "ECE",
        designations: ["Professor"],
        gender: "M"
    },
    {
        id: "rkverma",
        username: "rkverma",
        full_name: "Dr. Ritu Kumari Verma",
        user_type: "faculty",
        department: "CSE",
        designations: ["Associate Professor"],
        gender: "F"
    },
    {
        id: "ajsingh",
        username: "ajsingh",
        full_name: "Dr. Ajay Singh",
        user_type: "faculty",
        department: "EEE",
        designations: ["Assistant Professor"],
        gender: "M"
    },
    {
        id: "nmathur",
        username: "nmathur",
        full_name: "Prof. Neelam Mathur",
        user_type: "faculty",
        department: "Mathematics",
        designations: ["Professor"],
        gender: "F"
    },
    {
        id: "vkrishnan",
        username: "vkrishnan",
        full_name: "Dr. Vinod Krishnan",
        user_type: "faculty",
        department: "Mechanical",
        designations: ["Assistant Professor"],
        gender: "M"
    },
    {
        id: "sgupta",
        username: "sgupta",
        full_name: "Dr. Swati Gupta",
        user_type: "faculty",
        department: "Civil",
        designations: ["Associate Professor"],
        gender: "F"
    },
    {
        id: "mjain",
        username: "mjain",
        full_name: "Prof. Manish Jain",
        user_type: "faculty",
        department: "CSE",
        designations: ["Professor"],
        gender: "M"
    },
    {
        id: "pkhanna",
        username: "pkhanna",
        full_name: "Dr. Pooja Khanna",
        user_type: "faculty",
        department: "Humanities",
        designations: ["Assistant Professor"],
        gender: "F"
    },
    {
        id: "tbhushan",
        username: "tbhushan",
        full_name: "Prof. Tarun Bhushan",
        user_type: "faculty",
        department: "Physics",
        designations: ["Professor"],
        gender: "M"
    },
    {
        id: "adewan",
        username: "adewan",
        full_name: "Dr. Anjali Dewan",
        user_type: "faculty",
        department: "Chemistry",
        designations: ["Associate Professor"],
        gender: "F"
    }
];

const InfoCard = ({ person, selectable, selected, onSelectChange }) => (
    <Card shadow="xs" radius="md" withBorder p="lg">
        <Group justify="space-between" align="flex-start" wrap="nowrap">
            <div style={{ flex: 1 }}>
                <Group gap="xs" align="center" mb="xs">
                    <Text fw={600} size="lg">{person.full_name}</Text>
                    <Badge variant="light" radius="sm">{person.department}</Badge>
                </Group>
                <Text size="sm" c="dimmed"><strong>Username:</strong> {person.username}</Text>
                <Divider my="sm" />
                <Text size="sm" mb="xs"><strong>Designation:</strong></Text>
                <Group gap="xs" mb="xs">
                    {person.designations.map((role, idx) => (
                        <Badge key={idx} color="indigo" variant="light" radius="sm">{role}</Badge>
                    ))}
                </Group>
                <Text size="sm"><strong>Gender:</strong> {person.gender}</Text>
            </div>
            {selectable && (
                <Checkbox
                    checked={selected}
                    onChange={() => onSelectChange(person.username)}
                    mt="sm"
                />
            )}
        </Group>
    </Card>
);

const extractUnique = (arr, key) => [...new Set(arr.map(item => String(item[key])))];

const filterAndSearch = (data, filters, searchQuery) =>
    data.filter((person) => {
        const matchSearch = person.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            person.username.toLowerCase().includes(searchQuery.toLowerCase());

        const matchFilters = Object.entries(filters).every(([key, values]) => {
            if (values.length === 0) return true;
            return values.includes(String(person[key]));
        });

        return matchSearch && matchFilters;
    });

const ArchiveFacultyPage = () => {
    const checkIcon = <FaCheck style={{ width: rem(20), height: rem(20) }} />;

    const [activeTab, setActiveTab] = useState("archive");
    const [searchQuery, setSearchQuery] = useState("");
    const [filters, setFilters] = useState({
        department: [], designation: [], category: [], gender: []
    });
    const [selectedUsernames, setSelectedUsernames] = useState([]);
    const [modalOpened, setModalOpened] = useState(false);

    const handleSearchChange = useMemo(() =>
        debounce((value) => setSearchQuery(value), 200), []);

    const filteredData = useMemo(() =>
        filterAndSearch(STATIC_FACULTY, filters, searchQuery),
        [filters, searchQuery]);

    const isSelected = (username) => selectedUsernames.includes(username);
    const toggleSelect = (username) => {
        setSelectedUsernames((prev) =>
            prev.includes(username) ? prev.filter(u => u !== username) : [...prev, username]
        );
    };

    const selectAll = () => {
        setSelectedUsernames(filteredData.map(u => u.username));
    };

    const clearSelection = () => setSelectedUsernames([]);

    const handleArchive = () => {
        showNotification({
            icon: checkIcon,
            title: "Success",
            position: "top-center",
            withCloseButton: true,
            autoClose: 5000,
            message: `Archived selected faculty members`,
            color: "green",
        });
        clearSelection();
        setModalOpened(false);
    };

    return (
        <Container size="xl">
            <PageHeader
                title="Archive Faculty"
                subtitle="Move faculty members who have left the institute to the archive"
            />

            <Paper p="lg" radius="lg" withBorder>
                <Tabs value={activeTab} onChange={setActiveTab} variant="pills" radius="md" keepMounted={false}>
                    <Tabs.List grow mb="lg">
                        <Tabs.Tab value="archive">ARCHIVE</Tabs.Tab>
                        <Tabs.Tab value="archived">ARCHIVED</Tabs.Tab>
                    </Tabs.List>

                    <Tabs.Panel value="archive">
                        <Grid mb="lg">
                            <Grid.Col span={12}>
                                <TextInput
                                    placeholder="Search faculty"
                                    size="md"
                                    radius="md"
                                    onChange={(e) => handleSearchChange(e.currentTarget.value)}
                                />
                            </Grid.Col>
                            {["department", "designation", "category", "gender"].map((key) => (
                                <Grid.Col span={6} key={key}>
                                    <MultiSelect
                                        label={key[0].toUpperCase() + key.slice(1)}
                                        placeholder={`Filter by ${key}`}
                                        value={filters[key]}
                                        onChange={(value) => setFilters((prev) => ({ ...prev, [key]: value }))}
                                        data={extractUnique(STATIC_FACULTY, key)}
                                        size="md"
                                        radius="md"
                                        searchable
                                        clearable
                                    />
                                </Grid.Col>
                            ))}
                        </Grid>

                        <Group mb="md">
                            <Button onClick={selectAll} variant="light">Select All</Button>
                            <Button onClick={clearSelection} variant="default">Clear Selection</Button>
                        </Group>

                        <ScrollArea h={400}>
                            {filteredData.length > 0 ? (
                                <Grid>
                                    {filteredData.map((faculty) => (
                                        <Grid.Col span={12} key={faculty.username}>
                                            <InfoCard
                                                person={faculty}
                                                selectable
                                                selected={isSelected(faculty.username)}
                                                onSelectChange={toggleSelect}
                                            />
                                        </Grid.Col>
                                    ))}
                                </Grid>
                            ) : (
                                <Center h={200}>
                                    <Text ta="center" c="dimmed" size="sm">
                                        No faculty match your search or filters.
                                    </Text>
                                </Center>
                            )}
                        </ScrollArea>

                        {selectedUsernames.length > 0 && (
                            <Group mt="lg" justify="flex-end">
                                <Button onClick={() => setModalOpened(true)}>Archive</Button>
                            </Group>
                        )}
                    </Tabs.Panel>

                    <Tabs.Panel value="archived">
                        <Title order={3} mb="md">Recently Archived</Title>
                        <Grid>
                            {STATIC_FACULTY.slice(0, 2).map((s) => (
                                <Grid.Col span={12} key={s.username}>
                                    <InfoCard person={s} />
                                </Grid.Col>
                            ))}
                        </Grid>
                    </Tabs.Panel>
                </Tabs>
            </Paper>

            <Modal
                opened={modalOpened}
                onClose={() => setModalOpened(false)}
                title="Confirm Archive"
            >
                <Text size="sm">Are you sure you want to archive the selected faculty members?</Text>
                <Group justify="flex-end" mt="md">
                    <Button variant="default" onClick={() => setModalOpened(false)}>Cancel</Button>
                    <Button onClick={handleArchive}>Confirm</Button>
                </Group>
            </Modal>
        </Container>
    );
};

export default ArchiveFacultyPage;
