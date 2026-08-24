package com.manh.springbootcore.dto.response;

import lombok.Builder;
import lombok.Getter;
import java.util.List;

@Getter @Builder
public class ChatResponse {
    private String answer;
    private List<SourceDto> sources;
}