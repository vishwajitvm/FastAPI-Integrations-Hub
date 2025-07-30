import "tailwindcss";

const Login = () => {
  const ZohoLogin = async () => {
    window.location.href = "http://localhost:8000/login";
  };
  return (
    <>
      <div className="min-h-screen bg-[#1a1a1a] flex flex-col items-center justify-center px-4">
        <div className="bg-[#2c2c2c] shadow-[0_8px_30px_rgba(255,240,150,0.2)] rounded-2xl p-8 max-w-md w-full text-center">
          <h1 className="text-3xl font-bold text-yellow-500 mb-4">
            Welcome to <span className="text-yellow-500">Bee Logical</span>
          </h1>
          <p className="text-white text-lg mb-6">
            The chatbot is waiting for you. <br />
            Let’s login through Zoho to get access.
          </p>
          <button
            onClick={() => {
              ZohoLogin();
            }}
            className="bg-yellow-600 hover:bg-yellow-500 text-black font-semibold py-2 px-6 rounded-xl shadow-md transition-all duration-300"
          >
            Login with Zoho
          </button>
        </div>
      </div>
    </>
  );
};

export default Login;
