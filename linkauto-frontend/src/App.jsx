import React, { useState } from "react";
import Header from "./components/Header";
import Home from "./pages/Home";
import SearchPage from "./pages/SearchPage";
import InstructorProfile from "./pages/InstructorProfile";
import MyLessons from "./pages/MyLessons";
import InstructorDashboard from "./pages/InstructorDashboard";
import Login from "./pages/Login";
import { Search, Clock, LayoutDashboard } from "lucide-react";

const MOCK_INSTRUCTORS = [
  {
    id: 1,
    name: "Ricardo Silva",
    neighborhood: "Centro",
    rating: 4.8,
    price: 70,
    photo: "https://i.pravatar.cc/150?u=1",
  },
  {
    id: 2,
    name: "Ana Paula",
    neighborhood: "Parque do Estado",
    rating: 4.9,
    price: 85,
    photo: "https://i.pravatar.cc/150?u=2",
  },
  {
    id: 3,
    name: "Marcos Souza",
    neighborhood: "Mogi Mirim II",
    rating: 4.7,
    price: 65,
    photo: "https://i.pravatar.cc/150?u=3",
  },
];

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userRole, setUserRole] = useState("student");
  const [activeTab, setActiveTab] = useState("search");
  const [isSearchingPage, setIsSearchingPage] = useState(false);
  const [selectedInstructor, setSelectedInstructor] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [myLessons, setMyLessons] = useState([
    {
      id: 99,
      instructorName: "Marcos Silva",
      date: "30 MAR 2026",
      time: "14:00",
      neighborhood: "Centro",
      status: "completed",
    },
  ]);

  const handleLogin = (role) => {
    setUserRole(role);
    setIsAuthenticated(true);
    setActiveTab(role === "instructor" ? "dashboard" : "search");
  };

  const handleConfirmBooking = (instructor, time) => {
    const newLesson = {
      id: Date.now(),
      instructorName: instructor.name,
      date: "02 ABR 2026",
      time: time,
      neighborhood: instructor.neighborhood,
      status: "scheduled",
    };
    setMyLessons([...myLessons, newLesson]);
    alert("Solicitação enviada ao instrutor!");
    setSelectedInstructor(null);
    setIsSearchingPage(false);
    setActiveTab("lessons");
  };

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="flex flex-col min-h-screen bg-[#F8F9FC] font-sans pb-20">
      {!selectedInstructor && !isSearchingPage && (
        <Header onLogout={() => setIsAuthenticated(false)} />
      )}

      <div className="flex-grow">
        {userRole === "instructor" ? (
          <InstructorDashboard
            instructorData={{ name: "Ricardo Silva", rating: 4.8 }}
          />
        ) : (
          <>
            {selectedInstructor ? (
              <InstructorProfile
                instructor={selectedInstructor}
                onBack={() => setSelectedInstructor(null)}
                onConfirm={(time) =>
                  handleConfirmBooking(selectedInstructor, time)
                }
              />
            ) : isSearchingPage ? (
              <SearchPage
                searchTerm={searchTerm}
                setSearchTerm={setSearchTerm}
                instructors={MOCK_INSTRUCTORS}
                onSelectInstructor={(inst) => setSelectedInstructor(inst)}
                onBack={() => setIsSearchingPage(false)}
              />
            ) : activeTab === "search" ? (
              <Home onStartSearch={() => setIsSearchingPage(true)} />
            ) : (
              <MyLessons lessons={myLessons} />
            )}
          </>
        )}
      </div>

      {!selectedInstructor && !isSearchingPage && (
        <nav className="fixed bottom-0 w-full bg-white border-t border-gray-100 flex justify-around py-4 shadow-lg z-20">
          {userRole === "student" ? (
            <>
              <button
                onClick={() => setActiveTab("search")}
                className={`flex flex-col items-center ${activeTab === "search" ? "text-blue-600" : "text-gray-400"}`}
              >
                <Search size={22} />
                <span className="text-[10px] mt-1 font-bold">Início</span>
              </button>
              <button
                onClick={() => setActiveTab("lessons")}
                className={`flex flex-col items-center ${activeTab === "lessons" ? "text-blue-600" : "text-gray-400"}`}
              >
                <Clock size={22} />
                <span className="text-[10px] mt-1 font-bold">Aulas</span>
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => setActiveTab("dashboard")}
                className={`flex flex-col items-center ${activeTab === "dashboard" ? "text-blue-600" : "text-gray-400"}`}
              >
                <LayoutDashboard size={22} />
                <span className="text-[10px] mt-1 font-bold">Painel</span>
              </button>
              <button
                onClick={() => setActiveTab("lessons")}
                className={`flex flex-col items-center ${activeTab === "lessons" ? "text-blue-600" : "text-gray-400"}`}
              >
                <Clock size={22} />
                <span className="text-[10px] mt-1 font-bold">Agenda</span>
              </button>
            </>
          )}
        </nav>
      )}
    </div>
  );
}

export default App;
