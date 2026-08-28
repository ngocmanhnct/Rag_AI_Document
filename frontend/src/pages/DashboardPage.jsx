import { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { listDocuments, uploadDocument, deleteDocument } from '../api/documents';
import DocumentCard from '../components/DocumentCard';
import { Link } from 'react-router-dom';
export default function DashboardPage() {
  const { user, logout } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const fetchDocuments = useCallback(async () => {
    try {
      const res = await listDocuments();
      setDocuments(res.data);
    } catch (err) {
      console.error(err);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  // Tự động hỏi lại server mỗi 3 giây MIỄN LÀ còn tài liệu đang xử lý dở
  // (khớp đúng luồng bất đồng bộ qua RabbitMQ đã xây ở backend)
  useEffect(() => {
    const hasPending = documents.some(
      (d) => d.status === 'PENDING' || d.status === 'PROCESSING'
    );
    if (!hasPending) return;

    const interval = setInterval(fetchDocuments, 3000);
    return () => clearInterval(interval);
  }, [documents, fetchDocuments]);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setError('');
    setUploading(true);
    try {
      await uploadDocument(file);
      await fetchDocuments();
    } catch (err) {
      setError(err.response?.data?.message || 'Upload thất bại');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Xóa tài liệu này?')) return;
    try {
      await deleteDocument(id);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
    } catch (err) {
      setError('Xóa thất bại');
    }
  };

  return (
    <div className="min-h-screen bg-paper">
      <header className="flex justify-between items-center px-8 py-6 border-b border-ink/20">
        <div>
          <p className="font-mono text-[10px] tracking-widest text-ink-light uppercase">Phòng lưu trữ</p>
          <h1 className="font-display text-2xl text-ink">Kho tài liệu</h1>
        </div>
        <div className="text-right">
          <p className="font-mono text-xs text-ink">{user?.fullName}</p>
          <button onClick={logout} className="font-mono text-xs text-stamp underline">Đăng xuất</button>
        </div>
      </header>
      <Link to="/chat" className="font-mono text-xs text-ink underline">Vào phòng hỏi đáp →</Link>
      <main className="p-8">
        <div className="flex justify-between items-center mb-6">
          <p className="font-mono text-xs text-ink-light">{documents.length} tài liệu</p>
          <div>
            <input
              type="file"
              accept="application/pdf"
              ref={fileInputRef}
              onChange={handleFileChange}
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="bg-ink text-paper font-display text-sm px-4 py-2 hover:opacity-90 transition disabled:opacity-50"
            >
              {uploading ? 'Đang tải lên...' : '+ Thêm tài liệu (PDF)'}
            </button>
          </div>
        </div>

        {error && <p className="font-mono text-xs text-stamp mb-4">{error}</p>}

        {documents.length === 0 ? (
          <p className="font-body text-ink-light italic">Chưa có tài liệu nào — thêm file PDF đầu tiên để bắt đầu.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {documents.map((doc) => (
              <DocumentCard key={doc.id} doc={doc} onDelete={handleDelete} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}