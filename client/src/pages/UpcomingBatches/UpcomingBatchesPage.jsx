import { useState } from "react";
import { Container, Flex, Tabs, Title } from "@mantine/core";
import { useBatches } from "./hooks/useBatches";
import UGBatches from "./components/UGBatches";
import PGBatches from "./components/PGBatches";
import PhDBatches from "./components/PhDBatches";

const SECTIONS = {
  ug: UGBatches,
  pg: PGBatches,
  phd: PhDBatches,
};

const UpcomingBatchesPage = () => {
  const [active, setActive] = useState("ug");
  const { groups, disciplines, curriculums, loading, refresh } = useBatches();

  const ActiveSection = SECTIONS[active];

  return (
    <Container size="xl" py="xl">
      <Flex justify="center" mb="lg">
        <Title order={2}>Upcoming Batches</Title>
      </Flex>

      <Tabs value={active} onChange={setActive} variant="pills" radius="lg" keepMounted={false}>
        <Tabs.List grow mb="lg">
          <Tabs.Tab value="ug">UG</Tabs.Tab>
          <Tabs.Tab value="pg">PG</Tabs.Tab>
          <Tabs.Tab value="phd">PhD</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value={active}>
          <ActiveSection
            batches={groups[active]}
            disciplines={disciplines}
            curriculums={curriculums}
            loading={loading}
            refresh={refresh}
          />
        </Tabs.Panel>
      </Tabs>
    </Container>
  );
};

export default UpcomingBatchesPage;
