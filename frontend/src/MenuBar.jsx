import { useState } from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "./auth-context";
import { supabase } from "./supabase";

export default function MenuBar() {
  const { session, role } = useAuth();
  const [open, setOpen] = useState(false);

  return (
    <header className="menu-bar">
      <button
        type="button"
        className="menu-toggle"
        aria-label="Menu"
        aria-expanded={open}
        onClick={() => setOpen(!open)}
      >
        ☰
      </button>
      {open && (
        <nav className="menu-dropdown">
          {role && <span className="menu-role">{role}</span>}
          <span className="menu-email">{session?.user?.email}</span>
          <NavLink to="/" end onClick={() => setOpen(false)}>
            Ask
          </NavLink>
          {role === "admin" && (
            <NavLink to="/admin/users" onClick={() => setOpen(false)}>
              Users
            </NavLink>
          )}
          <button
            type="button"
            className="link-button"
            onClick={() => supabase.auth.signOut()}
          >
            Log out
          </button>
        </nav>
      )}
    </header>
  );
}
