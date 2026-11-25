import { useEffect, useState } from "react";
import { useAuth } from "./auth-context";
import { getUsers } from "./api";

export default function UsersPage() {
  const { session } = useAuth();
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;
    getUsers(session?.access_token, page)
      .then((result) => {
        if (active) {
          setData(result);
          setError(null);
        }
      })
      .catch(() => {
        if (active) setError("Could not load users.");
      });
    return () => {
      active = false;
    };
  }, [session, page]);

  let totalPages = 1;
  if (data) {
    totalPages = Math.ceil(data.total / data.page_size);
  }

  return (
    <main>
      <h1>Users</h1>
      {error && <p className="status-error">{error}</p>}
      {!error && !data && <p>Loading...</p>}
      {data && (
        <>
          <div className="table-wrap">
            <table className="users-table">
              <thead>
                <tr>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {data.users.map((user) => (
                  <tr key={user.user_id}>
                    <td>{user.email}</td>
                    <td>{user.role}</td>
                    <td>{user.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <nav className="pagination" aria-label="Pagination">
            <button
              type="button"
              onClick={() => setPage(page - 1)}
              disabled={page <= 1}
            >
              Previous
            </button>
            <span>
              Page {page} of {totalPages} - {data.total} users
            </span>
            <button
              type="button"
              onClick={() => setPage(page + 1)}
              disabled={page >= totalPages}
            >
              Next
            </button>
          </nav>
        </>
      )}
    </main>
  );
}
