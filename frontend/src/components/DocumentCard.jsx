const statusConfig = {
  PENDING: { label: 'Đang chờ', color: 'text-ink-light border-ink-light' },
  PROCESSING: { label: 'Đang xử lý', color: 'text-ink border-ink' },
  DONE: { label: 'Đã xử lý', color: 'text-stamp-green border-stamp-green' },
  FAILED: { label: 'Lỗi', color: 'text-stamp border-stamp' },
};

export default function DocumentCard({ doc, onDelete }) {
  const status = statusConfig[doc.status] || statusConfig.PENDING;

  return (
    <div className="group relative bg-card border border-ink/40 p-5 pt-6">
      {/* Miếng "tab" nhô lên như thẻ mục lục thư viện thật */}
      <div className="absolute -top-2 left-5 w-10 h-4 bg-ink" />

      <button
        onClick={() => onDelete(doc.id)}
        className="absolute top-2 right-2 font-mono text-[10px] text-stamp opacity-0 group-hover:opacity-100 transition"
      >
        Xóa
      </button>

      <p className="font-mono text-[10px] tracking-widest text-ink-light uppercase mb-2">
        Mục lục · {String(doc.id).padStart(4, '0')}
      </p>

      <h3 className="font-display text-base text-ink mb-3 break-words leading-snug">
        {doc.filename}
      </h3>

      <div className="flex items-center justify-between mt-4 pt-3 border-t border-ink/20">
        <span className={`font-mono text-[10px] uppercase border px-2 py-0.5 -rotate-2 inline-block ${status.color}`}>
          {status.label}
        </span>
        <span className="font-mono text-[10px] text-ink-light">
          {doc.chunksIndexed != null ? `${doc.chunksIndexed} đoạn` : '—'}
        </span>
      </div>
    </div>
  );
}