import React, { useState } from "react";
import { Bell, CheckCircle } from "lucide-react";

const NotificationPanel = () => {
  const [notifications, setNotifications] = useState([
    { text: "New event added: Shaggy Dog Show", read: false },
    { text: "Your event submission is under review", read: false },
    { text: "Reminder: Update your vendor profile", read: false },
    { text: "Payment for event received successfully", read: false },
    { text: "Admin message: System maintenance at 9 PM", read: false },
  ]);

  const markAllAsRead = () => {
    setNotifications((prevNotifications) =>
      prevNotifications.map((notification) => ({ ...notification, read: true }))
    );
  };

  return (
    <div className="min-h-screen bg-gray-100 text-gray-900">
      <header className="bg-gray-800 text-white p-4 flex justify-between items-center shadow-md">
        <div className="flex items-center gap-2">
          <span className="text-lg font-semibold">Logo</span>
          <Bell size={24} />
          <h1 className="text-xl font-bold">Notifications</h1>
        </div>
        <button
          onClick={markAllAsRead}
          className="bg-white text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-300 transition"
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
                className={`flex items-center gap-4 bg-white p-4 rounded-lg shadow-md ${
                  notification.read ? "bg-gray-200" : ""
                }`}
              >
                <CheckCircle
                  size={20}
                  className={`${
                    notification.read ? "text-gray-400" : "text-blue-500"
                  }`}
                />
                <span className={notification.read ? "text-gray-500" : ""}>
                  {notification.text}
                </span>
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
