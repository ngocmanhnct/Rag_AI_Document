package com.manh.springbootcore.service;

import com.manh.springbootcore.dto.request.ChatRequest;
import com.manh.springbootcore.dto.request.FastApiChatRequest;
import com.manh.springbootcore.dto.response.ChatResponse;
import com.manh.springbootcore.dto.response.FastApiChatResponse;
import com.manh.springbootcore.entity.User;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

@Service
@RequiredArgsConstructor
public class ChatService {

    private final WebClient ragServiceWebClient;

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

        return ChatResponse.builder()
                .answer(fastApiResponse.getAnswer())
                .sources(fastApiResponse.getSources())
                .build();
    }
}