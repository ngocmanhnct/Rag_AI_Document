package com.manh.springbootcore.dto.request;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Builder;
import lombok.Getter;

@Getter @Builder
public class FastApiChatRequest {
    private String query;

    @JsonProperty("top_k")
    private Integer topK;
}