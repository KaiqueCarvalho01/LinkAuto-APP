import React from "react";
import { User, LogOut } from "lucide-react";

const Header = ({ onLogout }) => {
  return (
    <header className="p-4 bg-white shadow-sm flex justify-between items-center sticky top-0 z-10">
      <h1 className="text-2xl font-bold text-blue-600 tracking-tight italic">
        LinkAuto
      </h1>

      {/* Botao de logout posicionado no perfil */}
      <button
        onClick={onLogout}
        className="p-2 bg-red-50 rounded-full text-red-600 active:scale-95 transition-all"
      >
        <LogOut size={20} />
      </button>
    </header>
  );
};

export default Header;
