package com.manh.springbootcore.service;

import tools.jackson.core.JacksonException;
import tools.jackson.core.type.TypeReference;
import tools.jackson.databind.ObjectMapper;
import com.manh.springbootcore.dto.request.ChatRequest;
import com.manh.springbootcore.dto.request.FastApiChatRequest;
import com.manh.springbootcore.dto.response.ChatHistoryResponse;
import com.manh.springbootcore.dto.response.ChatResponse;
import com.manh.springbootcore.dto.response.FastApiChatResponse;
import com.manh.springbootcore.dto.response.SourceDto;
import com.manh.springbootcore.entity.ChatMessage;
import com.manh.springbootcore.entity.User;
import com.manh.springbootcore.repository.ChatMessageRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.List;

@Service
@RequiredArgsConstructor
public class ChatService {

    private final WebClient ragServiceWebClient;
    private final ChatMessageRepository chatMessageRepository;
    private final ObjectMapper objectMapper;

    public ChatResponse chat(User currentUser, ChatRequest request) {
        FastApiChatRequest fastApiRequest = FastApiChatRequest.builder()
                .query(request.getQuery())
                .topK(4)
                .build();

        FastApiChatResponse fastApiResponse = ragServiceWebClient.post()
                .uri("/chat")
                .bodyValue(fastApiRequest)
                .retrieve()
                .bodyToMono(FastApiChatResponse.class)
                .block();

        saveHistory(currentUser, request.getQuery(), fastApiResponse);

        return ChatResponse.builder()
                .answer(fastApiResponse.getAnswer())
                .sources(fastApiResponse.getSources())
                .build();
    }

    public List<ChatHistoryResponse> getHistory(User owner) {
        return chatMessageRepository.findByOwnerOrderByCreatedAtDesc(owner).stream()
                .map(this::toHistoryResponse)
                .toList();
    }

    private void saveHistory(User owner, String query, FastApiChatResponse response) {
        try {
            String sourcesJson = objectMapper.writeValueAsString(response.getSources());
            ChatMessage message = ChatMessage.builder()
                    .query(query)
                    .answer(response.getAnswer())
                    .sourcesJson(sourcesJson)
                    .owner(owner)
                    .build();
            chatMessageRepository.save(message);
        } catch (JacksonException e) {
            // Cố ý nuốt lỗi ở đây: không để việc lưu lịch sử thất bại
            // làm hỏng luôn câu trả lời chính đang trả về cho client
        }
    }

    private ChatHistoryResponse toHistoryResponse(ChatMessage message) {
        List<SourceDto> sources;
        try {
            sources = objectMapper.readValue(
                    message.getSourcesJson(), new TypeReference<List<SourceDto>>() {});
        } catch (Exception e) {
            sources = List.of();
        }

        return ChatHistoryResponse.builder()
                .id(message.getId())
                .query(message.getQuery())
                .answer(message.getAnswer())
                .sources(sources)
                .createdAt(message.getCreatedAt())
                .build();
    }
}