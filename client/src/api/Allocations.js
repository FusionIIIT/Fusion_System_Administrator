import axiosInstance from "../context/axiosInstance";

const BASE = "/allocations";

export const fetchAllocationSummary = async ({ batch, semester, programme }) => {
  const { data } = await axiosInstance.get(`${BASE}/summary/`, {
    params: { batch, semester, programme },
  });
  return data;
};

export const deleteAllocation = async ({ batch, semester, programme }) => {
  const { data } = await axiosInstance.post(`${BASE}/delete/`, { batch, semester, programme });
  return data;
};
