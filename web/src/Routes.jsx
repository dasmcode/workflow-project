import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import FileDetail from "./pages/FileDetail";
import Chat from "./pages/Chat";
import Summary from "./pages/Summary";

function RoutesWrapper() {
  return (
    <BrowserRouter basename="/workflow/v1">
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/file/:fileId" element={<FileDetail />} />
        <Route path="/chat/:jobId" element={<Chat />} />
        <Route path="/summary/:jobId" element={<Summary />} />
      </Routes>
    </BrowserRouter>
  );
}

export default RoutesWrapper;
