import React, { useState } from "react";
import { LogIn } from "lucide-react";

const Login = ({ onLogin }) => {
  const [role, setRole] = useState("student"); // student ou instructor
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (email && password) {
      onLogin(role);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-[#F8F9FC] font-sans">
      {/* Cabecalho Azul com Degradê conforme o design */}
      <div className="bg-gradient-to-b from-[#2563EB] to-[#3B82F6] pt-16 pb-20 px-8 rounded-b-[40px] text-center shadow-lg">
        <div className="flex justify-center mb-4">
          <div className="bg-white/20 p-3 rounded-2xl backdrop-blur-md">
            <span className="text-white text-3xl font-black italic tracking-tighter">
              LinkAuto
            </span>
          </div>
        </div>
        <h1 className="text-white text-2xl font-bold mb-2">
          Bem-vindo(a) de volta!
        </h1>
        <p className="text-blue-100 text-sm opacity-90">
          Faça login para continuar sua jornada.
        </p>
      </div>

      <div className="px-8 -mt-10">
        <div className="bg-white rounded-[32px] p-8 shadow-xl shadow-blue-900/5">
          {/* Seletor de Perfil Estilo Toggle */}
          <div className="flex bg-gray-100 p-1.5 rounded-2xl mb-8">
            <button
              onClick={() => setRole("student")}
              className={`flex-1 py-3 rounded-xl text-sm font-bold transition-all ${
                role === "student"
                  ? "bg-white text-blue-600 shadow-sm"
                  : "text-gray-400"
              }`}
            >
              Aluno
            </button>
            <button
              onClick={() => setRole("instructor")}
              className={`flex-1 py-3 rounded-xl text-sm font-bold transition-all ${
                role === "instructor"
                  ? "bg-white text-blue-600 shadow-sm"
                  : "text-gray-400"
              }`}
            >
              Instrutor
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="text-[10px] font-black text-gray-400 uppercase ml-1 mb-2 block">
                E-mail
              </label>
              <input
                type="email"
                placeholder="Digite seu e-mail"
                className="w-full px-5 py-4 bg-gray-50 border border-gray-100 rounded-2xl focus:ring-2 focus:ring-blue-500 text-gray-700 outline-none transition-all placeholder:text-gray-300"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div>
              <div className="flex justify-between items-center ml-1 mb-2">
                <label className="text-[10px] font-black text-gray-400 uppercase block">
                  Senha
                </label>
                <button
                  type="button"
                  className="text-[10px] text-blue-500 font-bold"
                >
                  Esqueceu a senha?
                </button>
              </div>
              <input
                type="password"
                placeholder="........"
                className="w-full px-5 py-4 bg-gray-50 border border-gray-100 rounded-2xl focus:ring-2 focus:ring-blue-500 text-gray-700 outline-none transition-all"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <button
              type="submit"
              className="w-full bg-[#0F172A] text-white font-bold py-4 rounded-2xl shadow-lg active:scale-[0.98] transition-all flex items-center justify-center gap-2 mt-4"
            >
              Entrar
            </button>
          </form>

          {/* Divisor "ou entre com" */}
          <div className="relative my-8 text-center">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-100"></div>
            </div>
            <span className="relative bg-white px-4 text-[10px] text-gray-300 font-bold uppercase tracking-widest">
              ou entre com
            </span>
          </div>

          {/* Botao Google */}
          <button className="w-full py-4 border border-gray-100 rounded-2xl flex items-center justify-center gap-3 text-gray-600 font-bold text-sm active:bg-gray-50 transition-colors">
            <img
              src="https://www.svgrepo.com/show/475656/google-color.svg"
              className="w-5 h-5"
              alt=""
            />
            Google
          </button>

          <p className="mt-8 text-center text-xs text-gray-400 font-medium">
            Não tem uma conta?{" "}
            <span className="text-blue-600 font-bold">Cadastre-se</span>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
