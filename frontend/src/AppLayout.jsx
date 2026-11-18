import { Outlet } from "react-router-dom";
import MenuBar from "./MenuBar";

export default function AppLayout() {
  return (
    <>
      <MenuBar />
      <Outlet />
    </>
  );
}
