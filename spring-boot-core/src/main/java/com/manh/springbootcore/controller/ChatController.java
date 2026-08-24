package com.manh.springbootcore.controller;

import com.manh.springbootcore.dto.request.ChatRequest;
import com.manh.springbootcore.dto.response.ChatResponse;
import com.manh.springbootcore.entity.User;
import com.manh.springbootcore.service.ChatService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/chat")
@RequiredArgsConstructor
public class ChatController {

    private final ChatService chatService;

    @PostMapping
    public ChatResponse chat(@AuthenticationPrincipal User currentUser,
                             @Valid @RequestBody ChatRequest request) {
        return chatService.chat(currentUser, request);
    }
}