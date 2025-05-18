import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";  // Import Link for routing
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
          <Link to="/notifications">  {/* Use Link instead of a tag */}
            <i className="fas fa-bell" style={{ fontSize: '24px', color: 'white' }}></i>
          </Link>
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
