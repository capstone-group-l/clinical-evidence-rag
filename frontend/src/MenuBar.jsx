import { useState } from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "./auth-context";
import { supabase } from "./supabase";

export default function MenuBar() {
  const { session } = useAuth();
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
          <span className="menu-email">{session?.user?.email}</span>
          <NavLink to="/" end onClick={() => setOpen(false)}>
            Ask
          </NavLink>
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
