import React, { useState } from "react";
import { User, Briefcase, ArrowRight } from "lucide-react";

const Login = ({ onLogin }) => {
  const [role, setRole] = useState("student"); // 'student' ou 'instructor'

  return (
    <div className="flex flex-col min-h-screen bg-white p-8 justify-center font-sans">
      <div className="mb-10 text-center">
        <h1 className="text-4xl font-black text-blue-600 italic mb-2 tracking-tighter">
          LinkAuto
        </h1>
        <p className="text-gray-500 font-medium text-sm">
          Escolha como deseja acessar
        </p>
      </div>

      <div className="flex gap-4 mb-8">
        <button
          onClick={() => setRole("student")}
          className={`flex-1 p-4 rounded-2xl border-2 flex flex-col items-center gap-2 transition-all ${role === "student" ? "border-blue-600 bg-blue-50 text-blue-600" : "border-gray-100 text-gray-400"}`}
        >
          <User size={24} />
          <span className="font-bold text-xs uppercase">Aluno</span>
        </button>
        <button
          onClick={() => setRole("instructor")}
          className={`flex-1 p-4 rounded-2xl border-2 flex flex-col items-center gap-2 transition-all ${role === "instructor" ? "border-blue-600 bg-blue-50 text-blue-600" : "border-gray-100 text-gray-400"}`}
        >
          <Briefcase size={24} />
          <span className="font-bold text-xs uppercase">Instrutor</span>
        </button>
      </div>

      <button
        onClick={() => onLogin(role)}
        className="w-full bg-blue-600 text-white font-bold py-4 rounded-2xl shadow-xl flex items-center justify-center gap-2 active:scale-95 transition-all"
      >
        Entrar como {role === "student" ? "Aluno" : "Instrutor"}{" "}
        <ArrowRight size={20} />
      </button>
    </div>
  );
};

export default Login;
