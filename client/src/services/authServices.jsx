import axiosInstance from "../context/axiosInstance";
import { CONFIG } from "../pages/Login/constants";

/**
 * Authenticate against the backend and return the auth token.
 *
 * Pure network concern: it does NOT persist anything and never logs the credentials
 * or the token. Session persistence is centralised in AuthContext.login(token), which
 * keeps the token's lifecycle in one place.
 */
export const login = async (username, password) => {
  const { data } = await axiosInstance.post(
    "/login/",
    { username, password },
    { timeout: CONFIG.API_TIMEOUT_MS },
  );
  return data.token;
};
