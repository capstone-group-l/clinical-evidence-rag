import { Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "./AppLayout";
import AskPage from "./AskPage";
import LoginPage from "./LoginPage";
import RequireAuth from "./RequireAuth";
import UsersPage from "./UsersPage";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        element={
          <RequireAuth>
            <AppLayout />
          </RequireAuth>
        }
      >
        <Route path="/" element={<AskPage />} />
        <Route path="/admin/users" element={<UsersPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
