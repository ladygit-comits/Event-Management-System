import React, { useState } from "react";
import { Bell, CheckCircle } from "lucide-react";

const NotificationPanel = () => {
  const [notifications, setNotifications] = useState([
    "New event added: Shaggy Dog Show",
    "Your event submission is under review",
    "Reminder: Update your vendor profile",
    "Payment for event received successfully",
    "Admin message: System maintenance at 9 PM"
  ]);

  const markAllAsRead = () => setNotifications([]);

  return (
    <div className="min-h-screen bg-gray-100 text-gray-900">
      <header className="bg-gray-800 text-white p-4 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <span className="text-lg font-semibold">Logo</span>
          <Bell size={24} />
          <h1 className="text-xl font-bold">Notifications</h1>
        </div>
        <button
          onClick={markAllAsRead}
          className="bg-white text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-300"
        >
          Mark all as read
        </button>
      </header>

      <main className="p-6">
        {notifications.length === 0 ? (
          <p className="text-center text-gray-500">No new notifications</p>
        ) : (
          <ul className="space-y-4">
            {notifications.map((notification, index) => (
              <li
                key={index}
                className="flex items-center gap-4 bg-white p-4 rounded-lg shadow-md"
              >
                <CheckCircle size={20} className="text-blue-500" />
                <span>{notification}</span>
              </li>
            ))}
          </ul>
        )}
      </main>

      <footer className="text-center text-gray-600 py-4">Footer</footer>
    </div>
  );
};

export default NotificationPanel;
