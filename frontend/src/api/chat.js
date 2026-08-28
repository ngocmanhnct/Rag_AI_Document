export async function streamChat(query, onToken) {
  const token = localStorage.getItem('accessToken');

  const response = await fetch(
    `http://localhost:8080/chat/stream?query=${encodeURIComponent(query)}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  if (!response.ok) {
    throw new Error('Không thể kết nối chat');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // SSE: mỗi "event" cách nhau bởi 1 dòng trống (\n\n)
    const events = buffer.split('\n\n');
    buffer = events.pop(); // giữ lại phần chưa đọc hết, chờ mẩu dữ liệu tiếp theo

    for (const event of events) {
      const line = event.split('\n').find((l) => l.startsWith('data:'));
      if (line) {
        onToken(line.slice(5).trim());
      }
    }
  }
}