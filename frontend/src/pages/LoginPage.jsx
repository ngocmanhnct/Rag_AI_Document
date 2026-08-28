import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { login } from '../api/auth';
import { useAuth } from '../context/AuthContext';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { loginUser } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const response = await login({ email, password });
      loginUser(response.data);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.message || 'Sai email hoặc mật khẩu');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-paper flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="bg-card border-2 border-ink rounded-sm shadow-[4px_4px_0_0_theme(colors.ink)] p-8">
          <div className="text-center mb-8">
            <p className="font-mono text-xs tracking-widest text-ink-light uppercase mb-1">Thẻ truy cập · No. 001</p>
            <h1 className="font-display text-2xl text-ink">Trợ Lý Tài Liệu</h1>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="font-mono text-xs uppercase tracking-wide text-ink-light block mb-1">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full border border-ink/30 bg-paper px-3 py-2 font-body text-ink focus:outline-none focus:border-ink focus:ring-1 focus:ring-ink"
              />
            </div>
            <div>
              <label className="font-mono text-xs uppercase tracking-wide text-ink-light block mb-1">Mật khẩu</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full border border-ink/30 bg-paper px-3 py-2 font-body text-ink focus:outline-none focus:border-ink focus:ring-1 focus:ring-ink"
              />
            </div>

            {error && <p className="font-mono text-xs text-stamp">{error}</p>}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-ink text-paper font-display py-2.5 mt-2 hover:opacity-90 transition disabled:opacity-50"
            >
              {loading ? 'Đang đăng nhập...' : 'Đăng nhập'}
            </button>
          </form>

          <p className="text-center font-mono text-xs text-ink-light mt-6">
            Chưa có thẻ? <Link to="/register" className="text-ink underline">Đăng ký</Link>
          </p>
        </div>
      </div>
    </div>
  );
}