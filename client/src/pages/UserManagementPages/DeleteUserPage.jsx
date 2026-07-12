/* eslint-disable react/prop-types */
import { useState, useEffect, useCallback } from 'react';
import {
    Box,
    Group,
    TextInput,
    Container,
    Title,
    Modal,
    Button,
    Flex,
    Checkbox,
    Center,
    Grid,
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { users } from '../../data/users';
import { BarChart } from '@mantine/charts';

function Simple({ title, data, colors, datakey }) {
    return (
        <div>
            {/* Heading */}
            <Title order={2} align="center" mt="md" mb="lg">
                {title}
            </Title>

            {/* BarChart */}
            <BarChart
                h={250}
                data={data}
                dataKey={datakey}
                series={colors}
                tickLine="y"
                styles={{
                    bar: {
                        transition: '0.3s', // Add smooth transition for hover
                        '&:hover': {
                            fillOpacity: 0.8, // Make it slightly transparent on hover
                        },
                    },
                }}
            />
        </div>
    );
}

const DeleteUserPage = () => {
    const [userBatchData, setUserBatchData] = useState([]);
    const [colors] = useState([{ name: 'Deleted', color: 'red' }]);
    const [userList, setUserList] = useState(users);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedUsers, setSelectedUsers] = useState([]);
    const [opened, { open, close }] = useDisclosure(false);

    useEffect(() => {
        // Aggregating user batch data to show in the BarChart
        const aggregatedData = userList.reduce((acc, user) => {
            const batch = user.batch;
            if (!acc[batch]) {
                acc[batch] = { batch, Deleted: 0 };
            }
            acc[batch].Deleted += 100; // Static data for now
            return acc;
        }, {});
        setUserBatchData(Object.values(aggregatedData));
    }, [userList]);

    const handleSearch = (event) => {
        setSearchTerm(event.target.value.toLowerCase());
    };

    const toggleSelectUsers = (id) => {
        setSelectedUsers((prevSelected) =>
            prevSelected.includes(id)
                ? prevSelected.filter((userId) => userId !== id)
                : [...prevSelected, id]
        );
    };

    const handleDelete = useCallback(() => {
        open();
    }, [open]);

    const confirmDelete = () => {
        setUserList(userList.filter(user => !selectedUsers.includes(user.id)));
        setSelectedUsers([]);
        close();
    };

    const filteredUsers = userList.filter(user => {
        const searchLower = searchTerm.toLowerCase();
        return (
            user.name.toLowerCase().includes(searchLower) ||
            user.branch.toLowerCase().includes(searchLower) ||
            user.role.toLowerCase().includes(searchLower) ||
            user.rollNo?.toLowerCase().includes(searchLower)
        );
    });

    return (
        <Container fluid my="md">
            <Flex
                direction={{ base: 'column', sm: 'row' }}
                gap={{ base: 'sm', sm: 'lg' }}
                justify={{ sm: 'center' }}
                mb={'1rem'}
            >
                <Button
                    variant="gradient"
                    size="xl"
                    radius="xs"
                    gradient={{ from: 'red', to: 'orange', deg: 90 }}
                    sx={{
                        display: 'block',
                        width: { base: '100%', sm: 'auto' },
                        whiteSpace: 'normal',
                        padding: '1rem',
                        textAlign: 'center',
                    }}
                >
                    <Title
                        order={1}
                        sx={{
                            fontSize: { base: 'lg', sm: 'xl' },
                            lineHeight: 1.2,
                            wordBreak: 'break-word',
                        }}
                    >
                        Delete Users
                    </Title>
                </Button>
            </Flex>

            <Grid style={{ display: 'flex', alignItems: 'stretch' }}>
                <Grid.Col span={12} style={{ display: 'flex' }}>
                    <Container
                        style={{
                            backgroundColor: '#f8f9fa',
                            padding: '1rem',
                            border: '2px solid #ababab',
                            borderRadius: '15px',
                            flex: 1,
                        }}
                    >
                        <Simple title={'User Batch Data'} colors={colors} data={userBatchData} />
                    </Container>
                </Grid.Col>
            </Grid>

            <Box mt={10}>
                <Group position="center" mb={5}>
                    <TextInput
                        placeholder="Search by name, role, roll no, etc."
                        value={searchTerm}
                        onChange={handleSearch}
                        styles={{
                            root: {
                                marginLeft: 'auto',
                                marginRight: 'auto',
                                width: '400px',
                            },
                            input: {
                                marginLeft: 'auto',
                                marginRight: 'auto',
                                backgroundColor: 'white',
                                borderRadius: '50px',
                                boxShadow: 'xl',
                                '&:hover': { boxShadow: '2xl' },
                                '&:focus': { borderColor: 'lightcoral' },
                            },
                        }}
                    />
                </Group>

                <Center>
                    <Grid>
                        {filteredUsers.map((user) => (
                            <Grid.Col span={6} key={user.id}>
                                <Flex
                                    mb={5}
                                    align="center"
                                    style={{
                                        backgroundColor: 'white',
                                        padding: '10px',
                                        borderRadius: '8px',
                                        border: '2px solid #f0f0f0',
                                    }}
                                >
                                    <Checkbox
                                        checked={selectedUsers.includes(user.id)}
                                        onChange={() => toggleSelectUsers(user.id)}
                                        styles={{
                                            input: {
                                                cursor: 'pointer',
                                                width: '20px',
                                                height: '20px',
                                            },
                                        }}
                                    />
                                    <Box ml={10} style={{ flex: 1 }}>
                                        <div style={{ fontWeight: 'bold', fontSize: '1.2rem' }}>{user.name}</div>
                                        <div style={{ marginLeft: '10px', fontSize: '0.9rem' }}>{user.rollNo}</div>
                                        <div style={{ marginLeft: '10px', fontSize: '0.8rem' }}>{user.role}</div>
                                    </Box>
                                </Flex>
                            </Grid.Col>
                        ))}
                    </Grid>
                </Center>

                <Center mt={5}>
                    <Group mt={5}>
                        <Button
                            gradient={{ from: 'lightyellow', to: 'red' }}
                            color="coral"
                            onClick={handleDelete}
                            disabled={selectedUsers.length === 0} // Disable if no users are selected
                        >
                            Delete Selected
                        </Button>
                    </Group>
                </Center>

                <Modal opened={opened} onClose={close} title="Confirm Action">
                    <Modal.Body>
                        Are you sure you want to delete the selected users? This action cannot be undone.
                    </Modal.Body>
                    <center>
                        <Button color="blue" onClick={confirmDelete} mr="10">
                            Proceed
                        </Button>

                        <Button variant="outline" onClick={close}>
                            Cancel
                        </Button>
                    </center>
                </Modal>
            </Box>
        </Container>
    );
};
export default DeleteUserPage;
