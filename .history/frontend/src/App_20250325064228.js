import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";  // Use Routes instead of Switch
import NotificationPanel from "./components/NotificationPanel";  // Importing the notification panel component
import logo from "./logo.svg";
import "./App.css";

function App() {
  return (
    <Router>
      <div className="App">
        {/* Header with Bell Icon - for Notification */}
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <h1>Event Management</h1>
          <a href="/notifications">
            <i className="fas fa-bell" style={{ fontSize: '24px', color: 'white' }}></i>
          </a>
        </header>

        {/* Routing Section */}
        <Routes>
          <Route path="/" element={<div><h2>Welcome to the Event Management System</h2><p>Click the bell icon to view your notifications</p></div>} />
          <Route path="/notifications" element={<NotificationPanel />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
