package com.manh.springbootcore.dto.response;

import lombok.Builder;
import lombok.Getter;

import java.time.LocalDateTime;
import java.util.List;

@Getter @Builder
public class ChatHistoryResponse {
    private Long id;
    private String query;
    private String answer;
    private List<SourceDto> sources;
    private LocalDateTime createdAt;
}